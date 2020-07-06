'''
NetDisco API Module to Query Network Inventory
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import json # Required to process JSON requests
import requests # Required for API POST
import xmltodict # Requird to convert POST XML response to DICT
import pprint # Optional to Pretty Print Responses
import time # Require for requests delay function
import ipdb # Optional Debug. ipdb.set_trace()

pp = pprint.PrettyPrinter()

def netdisco_api(SESSION_TK):

    netdisco_status = False
    netdisco_log = []
    netdisco_list = []

    netdisco_log.append(('NetDisco API Query Initialised...', 0))

    print('\n' + '#' * 10 + ' NetDisco API Query ' + '#' * 10 + '\n')

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG NetDisco SESSION_TK Received:')
        print(pp.pprint(SESSION_TK))

    netdisco_cfg_f = 'config/netdisco_cfg.json' # NetDisco Config File

    try:
        with open(netdisco_cfg_f) as netdisco_f:
            netdisco_cfg = json.load(netdisco_f)

        USERNAME = netdisco_cfg["USERNAME"]
        PASSWORD = netdisco_cfg["PASSWORD"]
        URL = netdisco_cfg["URL"]

    except Exception as error:
        netdisco_log.append(('NetDisco Error: ' + str(error) + '. ' + str(netdisco_cfg_f ) \
            + ' maybe missing or invalid', 1))
        return netdisco_status, netdisco_log, netdisco_list

    try:
        #Get API KEY with POST request . Valid for 3600 seconds
        api_key_post = requests.post('http://' + str(URL) + '/login',
                  auth=(USERNAME, PASSWORD),
                  headers={'Accept': 'application/json'})

        if SESSION_TK['vDEBUG']: # True
            print('\n***DEBUG (modules/netdisco_api.py) : Netdisco API Session Key: ')
            print(api_key_post.json()['api_key'])

        api_get_devices = requests.get('http://' + str(URL) + '/api/v1/report/device/devicebylocation',
                headers={'Accept': 'application/json',
               'Authorization': api_key_post.json()['api_key'] })

        # Curiosity with NetDisco and occasional polling where it returns 401. Retry
        # but with delay

        if api_get_devices.status_code == 200:
            pass # OK

        if api_get_devices.status_code == 401:
            time.sleep(5)
            api_get_devices = requests.get('http://' + str(URL) + '/api/v1/report/device/devicebylocation',
                    headers={'Accept': 'application/json',
                   'Authorization': api_key_post.json()['api_key'] })

        if SESSION_TK['vDEBUG']: # True
            print('\n***DEBUG (modules/netdisco_api.py) : Netdisco API Device By Location Response: ')
            print(json.dumps(api_get_devices.json(), indent=2))

        # Generate Host List
        xlist = []

        for host in api_get_devices.json():
            xlist.append(host['name'])

        for host in xlist:
            if any(iPAT in host for iPAT in SESSION_TK['iPATTERN']) and not any(xPAT in host for xPAT in SESSION_TK['xPATTERN']):
                for strip in SESSION_TK['dSTRIP']:
                    netdisco_list.append(host.strip(strip))

        if SESSION_TK['bDEBUG']: # True
            print('\n**DEBUG NetDisco Filtered List Generated:')
            print(pp.pprint(netdisco_list))

        netdisco_log.append(('NetDisco API Query Successful', 0))
        netdisco_status = True

    except Exception as error:
        netdisco_log.append(('NetDisco API Error: ' + str(error) + \
            ". API error occasionally occurs for no reason. NetDisco inventory check skipped in this run. Re-run recommended!", 1))

    return netdisco_status, netdisco_log, netdisco_list
