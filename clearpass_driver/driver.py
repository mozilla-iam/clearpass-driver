import credstash
import os
import utils
import requests
import yaml

from settings import get_config
from vault import People


def setup_logging(config):
    global logger
    custom_logger = utils.CISLogger(
        name=__name__,
        level=config('logging_level', namespace='cis', default='INFO'),
        cis_logging_output=config('logging_output', namespace='cis', default='cloudwatch'),
        cis_cloudwatch_log_group=config('cloudwatch_log_group', namespace='cis', default='staging')
    ).logger()

    logger = custom_logger.get_logger()


def get_access_rules(appsyml):
    """
    Fetch access rules
    @appsyml str URL
    returns dict
    """
    ## Sample appsyml return value format:
    ## { 'apps': [
    ##          {'application': {'name': 'Account Portal', 'op': 'auth0', 'url': 'https://login.mozilla.com/', 'logo':
    ##          'accountmanager.png', 'authorized_users': [], 'authorized_groups': ['team_moco', 'team_mofo'],
    ##          'display': True, ## 'vanity_url': ['/accountmanager']}}
    ##         ]
    ## }
    logger.debug('Fetching access rules.')
    r = requests.get(appsyml)
    if not r.ok:
        logger.warning('Failed to fetch access rules, will not deprovision users.')
        return []

    access_rules = yaml.load(r.text).get('apps')
    logger.debug('Received apps.yml size {}'.format(len(r.text)))
    return access_rules


def get_secret(secret_name, context):
    """Fetch secret from environment or credstash."""
    secret = os.getenv(secret_name.split('.')[1], None)

    if not secret:
        secret = credstash.getSecret(
            name=secret_name,
            context=context,
            region="us-west-2"
        )
    return secret


def verify_clearpass_users(allowed_users):
    """
    Find all Clearpass users which aren't allowed and deactivate them
    """
    # 1. list all clearpass users
    # 2. diff clearpassusers with allowed_users
    # 3. disable all users in the diff and log

def handle(event=None, context={}):
    config = get_config()
    setup_logging(config)
    logger.info('Initializing Clearpass driver.')

    appsyml = config('appsyml', namespace='clearpass_driver', default='https://cdn.sso.mozilla.com/apps.yml')
    clearpass_app = config('clearpass_app', namespace='clearpass_driver', default='clearpass')

    access_rules = get_access_rules(appsyml)
    app = None
    authorized_groups = []
    for app in access_rules:
        actual_app = app.get('application')
        if actual_app.get('name') == clearpass_app:
            # XXX CIS with v1 profile prepend ldap groups with `ldap_` but the rest of the infra does not... so
            # workaround here:
            authorized_groups = []
            known_idp_prefix = ['mozilliansorg', 'hris', 'ldap']
            for g in actual_app.get('authorized_groups'):
                if g.split('_')[0] not in known_idp_prefix:
                    # its an ldap group
                    authorized_groups.append("ldap_" + g)
                else:
                    authorized_groups.append(g)

            logger.debug('Valid and authorized users are in groups {}'.format(authorized_groups))
            break

    if app is None:
        logger.warning('Did not find {} in access rules, will not deprovision users'.format(clearpass_app))
        return

    logger.debug('Searching DynamoDb for people.')
    people = People()

    logger.debug('Filtering person list to groups.')
    allowed_users = people.people_in_group(authorized_groups)
    logger.debug('Found {} Clearpass users which are allowed'.format(len(allowed_users)))

    logger.debug('Disable Clearpass users.')
    if not verify_clearpass_users(allowed_users):
        logger.warning('Failed to verify clearpass users - some users may not have been deprovisioned')
