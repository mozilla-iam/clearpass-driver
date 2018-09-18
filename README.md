# Clearpass Driver

## About
This driver was created for the Mozilla IAM Project to deprovision Wifi users using Clearpass authentication.

## Behavior

1. Spin up on cron/event trigger.
2. Scan the dynamodb table of all profiles.
3. Build a group data structure from all profiles.
4. Query the Clearpass API for all users profiles.
5. Fetch `apps.yml` access control file.
6. Disable any user without access to Clearpass (wifi in this case) through a Clearpass API call.
7. Enable any previously-disabled user that is still present in Clearpass database.


## Deployment

### Insert credstash api key

You only need to do this once.

```
credstash -r us-west-2 put -a clearpass-driver.token @clearpass-driver-api-key.txt app=clearpass-driver
```

To obtain the token, contact your Clearpass administator.

### Deploy, test, etc

1. `cd clearpass_driver`
2. `make` for a list of targets, ex:

- `make python-venv` if you don't have your own virtual environment scripts

- `make tests` runs all tests
- `make deploy` deploys the code in the dev environment
- `make remove-deploy` deletes the dev deployment
- `make STAGE=prod deploy` deploys the code in the prod environment
- `make logs` just watch cloudwatch logs
