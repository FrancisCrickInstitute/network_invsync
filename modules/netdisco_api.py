'''
NetDisco API Function to Query Network Inventory
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import json # Required to process JSON requests
import requests # Required for API POST
import xmltodict # Requird to convert POST XML response to DICT
import pprint # Optional to Pretty Print Responses
import ipdb # Optional Debug. ipdb.set_trace()

pp = pprint.PrettyPrinter()

def netdisco_api(SESSION_TK):

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG NetDisco SESSION_TK Received:')
        print(pp.pprint(SESSION_TK))

    netdisco_cfg_f = 'modules/netdisco_cfg.json' # NetDisco Config File

    with open(netdisco_cfg_f) as netdisco_f:
        netdisco_cfg = json.load(netdisco_f)

    USERNAME = netdisco_cfg["USERNAME"]
    PASSWORD = netdisco_cfg["PASSWORD"]
    URL = netdisco_cfg["URL"]

    #Get API KEY. Valid for 3600 seconds
    api_key_post = requests.post('http://' + str(URL) + '/login',
                  auth=(USERNAME, PASSWORD),
                  headers={'Accept': 'application/json'})

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG (modules/netdisco_api.py) : Netdisco API Session Key: ')
        print(api_key_post.json()['api_key'])

    api_get_devices = requests.get('http://' + str(URL) + '/api/v1/report/device/devicebylocation',
                headers={'Accept': 'application/json',
               'Authorization': api_key_post.json()['api_key'] })

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG (modules/netdisco_api.py) : Netdisco API Session Key: ')
        print(json.dumps(api_get_devices.json(), indent=2, sort_keys=True))

    xlist = []
    nlist = []

    for host in api_get_devices.json():
        xlist.append(host['name'])

    for host in xlist:
        if any(iPAT in host for iPAT in SESSION_TK['iPATTERN']) and not any(xPAT in host for xPAT in SESSION_TK['xPATTERN']):
            for strip in SESSION_TK['dSTRIP']:
                nlist.append(host.strip(strip))

    if SESSION_TK['bDEBUG']: # True
        print('\n**DEBUG NetDisco Filtered List Generated:')
        print(pp.pprint(nlist))

    return nlist
