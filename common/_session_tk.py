'''
Generate Session_tk Class Object
REQ: None
RTN: None
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import json # Required to Read Configuration File
import base64 # Required to generate ServiceNow Basic Auth string
import ipdb # Optional Debug. ipdb.set_trace()

class Session_tk:
    def __init__(self):
        self.status = False
        self.log = []

        try:

            # ...
            # Vault
            self.log.append(('%common/_session_tk','Session Token Vault Initialised...', 5))

            network_vault_f = '../network_config/network_vault.json'

            with open(network_vault_f) as network_vault_f:
                network_vault = json.load(network_vault_f)

            self.netdisco_username = network_vault['NETDISCO_USERNAME']
            self.netdisco_password = network_vault['NETDISCO_PASSWORD']
            self.netdisco_url = network_vault['NETDISCO_URL']
            self.ise_url = network_vault['ISE_URL']
            self.ise_pages = network_vault['ISE_PAGES']
            self.ise_oauth_token = network_vault['ISE_OAUTH_TOKEN']
            self.librenms_url = network_vault['LIBRENMS_URL']
            self.librenms_xauth_token = network_vault['LIBRENMS_XAUTH_TOKEN']
            self.slack_oauth_token = network_vault['SLACK_OAUTH_TOKEN']
            self.slack_channel = network_vault['SLACK_CHANNEL']

            self.log.append(('%common/_session_tk', 'Session Token Vault Successful', 5))

        except Exception as error:
            self.log.append(('%common/_session_tk', 'Session Token Vault Error: ' + str(error), 4))
            self.log.append(('%common/_session_tk', 'Session Token Vault Error: Check Variables Exist!' , 4))

        try:
            # ...
            # App Config
            self.log.append(('%common/_session_tk', 'Session Token App Config Initialised...', 5))

            app_cfg_f = 'config/app_cfg.json'

            with open(app_cfg_f) as app_cfg_f:
                app_cfg = json.load(app_cfg_f)

            self.slack_post = app_cfg['SLACK_POST']
            self.debug = app_cfg['DEBUG']
            self.yaml_filter = app_cfg['YAML_FILTER']
            self.dom_strip = app_cfg['DOM_STRIP']
            self.ipattern = app_cfg['IPATTERN']
            self.xpattern = app_cfg['XPATTERN']

            self.log.append(('%common/_session_tk', 'Session Token App Config Successful', 5))

            # ...
            # OK
            self.status = True

        except Exception as error:
            self.log.append(('%common/_session_tk', 'Session Token App Config Error: ' + str(error), 4))
            self.log.append(('%common/_session_tk', 'Session Token App Config Error: Check Variables Exist!' , 4))
