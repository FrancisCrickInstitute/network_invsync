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

from common._session_tk import Session_tk # Import Session Token Class
SESSION_TK = Session_tk() # Define object from Class

pp = pprint.PrettyPrinter()

def netdisco_api():

    netdisco_api_status = False
    netdisco_api_log = []
    netdisco_api_list = []

    netdisco_api_log.append(('NetDisco API Query Initialised...', 0))

    try:
        #Get API KEY with POST request . Valid for 3600 seconds
        api_key_post = requests.post('http://' + str(SESSION_TK.netdisco_url) + '/login',
                  auth=(SESSION_TK.netdisco_username, SESSION_TK.netdisco_password),
                  headers={'Accept': 'application/json'})

        if SESSION_TK.debug == 2:
            print('\n**DEBUG (modules/netdisco_api_api.py) : Netdisco API Session Key: ')
            print(api_key_post.json()['api_key'])

        api_get_devices = requests.get('http://' + str(SESSION_TK.netdisco_url) + '/api/v1/report/device/devicebylocation',
                headers={'Accept': 'application/json',
               'Authorization': api_key_post.json()['api_key'] })

        if SESSION_TK.debug == 2:
            print('\n**DEBUG (modules/netdisco_api_api.py) : Netdisco API POST Key Response: ')
            print(json.dumps(api_key_post.json(), indent=2))

        # Curiosity with NetDisco and occasional polling where it returns 401. Retry
        # but with delay

        if api_get_devices.status_code == 200:
            pass # OK

        if api_get_devices.status_code == 401:
            time.sleep(5)
            api_get_devices = requests.get('http://' + str(SESSION_TK.netdisco_url) + '/api/v1/report/device/devicebylocation',
                    headers={'Accept': 'application/json',
                   'Authorization': api_key_post.json()['api_key'] })

        if SESSION_TK.debug == 2:
            print('\n**DEBUG (modules/netdisco_api_api.py) : Netdisco API Device By Location Response: ')
            print(json.dumps(api_get_devices.json(), indent=2))

        # Generate Host List
        xlist = []

        for host in api_get_devices.json():
            xlist.append(host['name'])

        for host in xlist:
            if any(iPAT in host for iPAT in SESSION_TK.ipattern) and not any(xPAT in host for xPAT in SESSION_TK.xpattern):
                for strip in SESSION_TK.dom_strip:
                    netdisco_api_list.append(host.strip(strip))

        if SESSION_TK.debug == 2:
            print('\n**DEBUG: NetDisco Filtered List Generated:')
            print(pp.pprint(netdisco_api_list))

        netdisco_api_log.append(('NetDisco API Query Successful', 0))
        netdisco_api_status = True

    except Exception as error:
        netdisco_api_log.append(('NetDisco API Error: ' + str(error) + \
            ". API error occasionally occurs for no reason. NetDisco inventory check skipped in this run. Re-run recommended!", 1))

    return netdisco_api_status, netdisco_api_log, netdisco_api_list
