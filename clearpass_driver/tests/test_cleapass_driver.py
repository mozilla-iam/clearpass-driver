#!/usr/bin/python

import driver
import json
import logging
import requests
import unittest

from unittest.mock import patch


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


class ClearpassDriverTest(unittest.TestCase):
    def setUp(self):
        pass

    @patch.object(requests, 'get')
    def test_get_access_rules(self, mock_request):
        class fake_request(object):
            fake_json = {'apps': {'Clearpass': {'authorized_groups': ['team_moco']}}}
            text = json.dumps(fake_json)

            def ok(self):
                return True

        mock_request.return_value = fake_request
        driver.logger = logger
        ret = driver.get_access_rules('https://cdn.sso.mozilla.com/apps.yml')
        assert(ret['Clearpass']['authorized_groups'][0] == 'team_moco')
