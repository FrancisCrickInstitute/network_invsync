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

        while True:
            # ...
            # App Config
            try:
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
                self.fpattern = app_cfg['FPATTERN']

                self.log.append(('%common/_session_tk', 'Session Token App Config Successful', 5))

            except Exception as error:
                self.log.append(('%common/_session_tk', 'Session Token App Config Error: ' + str(error), 4))
                self.log.append(('%common/_session_tk', 'Session Token App Config Error: Check Variables Exist!' , 4))

            # ...
            # Vault
            try:

                self.log.append(('%common/_session_tk', 'Session Token Vault Initialised...', 6))

                try:
                    hashBy = os.environ['NET_HASH'].encode()
                    self.log.append(('%common/_session_tk', 'Session Token HASH Envriomental Variable Found...', 6))
                except Exception as error:
                    self.log.append(('%common/_session_tk', 'Session Token HASH Environmental Variable Not Found!!!', 3))
                    self.log.append(('%common/_session_tk', "os.environ['NET_HASH'] Not Found!!! Use 'export NET_HASH={Password on Celo}", 3))
                    break 
                
                try:
                    network_vaultx_f = '../network_config/network_vaultx.json' # Fernet (Symmetric Encryption) File
                    with open (network_vaultx_f, 'rb') as file: # Read Binary
                        encryptF = file.read()
                except Exception as error:
                    self.log.append(('%common/_session_tk', 'Session Token Vault Open Error: ' + str(error), 3))
                    break
                
                # Create Fernet Object using HASH
                f = Fernet(hashBy)
                # <cryptography.fernet.Fernet object at 0x104fc0490>

                # Decrypt File
                decryptF = f.decrypt(encryptF)

                # Convert Binary to ASCII Object
                decodeA = decryptF.decode()

                # Convert ASCII to Dictionary Object usinf ATS
                decodeD = ast.literal_eval(decodeA)

                self.netdisco_username = decodeD['NETDISCO_USERNAME']
                self.netdisco_password = decodeD['NETDISCO_PASSWORD']
                self.netdisco_url = decodeD['NETDISCO_URL']
                self.ise_url = decodeD['ISE_URL']
                self.ise_pages = decodeD['ISE_PAGES']
                self.ise_oauth_token = decodeD['ISE_OAUTH_TOKEN']
                self.librenms_url = decodeD['LIBRENMS_URL']
                self.librenms_xauth_token = decodeD['LIBRENMS_XAUTH_TOKEN']
                self.slack_oauth_token = decodeD['SLACK_OAUTH_TOKEN']
                self.slack_channel = decodeD['SLACK_CHANNEL_INFO']

                self.log.append(('%common/_session_tk', 'Session Token Vault Successful', 6))

            except Exception as error:
                self.log.append(('%common/_session_tk', 'Session Token Vault Error: ' + str(error), 4))
                self.log.append(('%common/_session_tk', 'Session Token Vault Error: Check Variables Exist!' , 4))
                break 

            # ...
            # OK
            self.status = True
            break
