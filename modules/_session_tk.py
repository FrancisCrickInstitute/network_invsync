'''
Generate SESSION_TK
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import json # Required to Read Configuration File
import getpass # Required to Prompt
import sys # Required to exit on failure

def session_tk():
    '''
    Generate SESSION_TK
    '''
    session_tk_status = True
    session_tk_log = []
    SESSION_TK = {}

    session_tk_log.append(('SESSION_TK Generation Initialised...', 0))

    print('\n' + '#' * 10 + ' SESSION_TK Generation Initialised... ' + '#' * 10 + '\n')

    # Authentication Credentials
    try:
        network_vault_f = '../network_config/network_vault.json'

        with open(network_vault_f) as network_vault_f:
            network_vault = json.load(network_vault_f)

        SESSION_TK['AAA_UN'] = network_vault['AAA_UN']
        SESSION_TK['AAA_PW'] = network_vault['AAA_PW']
        SESSION_TK['ISE_OAUTH_TOKEN'] = network_vault['ISE_OAUTH_TOKEN']
        SESSION_TK['ISE_URL'] = network_vault['ISE_URL']
        SESSION_TK['ISE_PAGES'] = network_vault['ISE_PAGES']
        SESSION_TK['NETDISCO_USERNAME'] = network_vault['NETDISCO_USERNAME']
        SESSION_TK['NETDISCO_PASSWORD'] = network_vault['NETDISCO_PASSWORD']
        SESSION_TK['NETDISCO_URL'] = network_vault['NETDISCO_URL']

        session_tk_log.append(('Network Vault to SESSION_TK Successful', 0))

    except Exception as error:
       session_tk_log.append(('Network Vault to SESSION_TK Error: ' + str(error), 1))
       session_tk_status = False

    # Configuration Variables
    try:
        invsync_cfg_f = 'config/invsync_cfg.json'

        with open(invsync_cfg_f) as invsync_f:
            invsync_cfg = json.load(invsync_f)

        SESSION_TK['DEBUG'] = invsync_cfg['DEBUG']
        SESSION_TK['SLACKPOST'] = invsync_cfg['SLACKPOST']
        SESSION_TK['iPATTERN'] = invsync_cfg['iPATTERN']
        SESSION_TK['xPATTERN'] = invsync_cfg['xPATTERN']
        SESSION_TK['dSTRIP'] = invsync_cfg['dSTRIP']
        SESSION_TK['yFILTER'] = invsync_cfg['yFILTER']

        session_tk_log.append(('InvSync Config to SESSION_TK Successful', 0))

    except Exception as error:
       session_tk_log.append(('InvSync Config to SESSION_TK Error: ' + str(error), 1))
       session_tk_status = False

    return session_tk_status, session_tk_log, SESSION_TK
