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

    netdisco_api_log.append(('%modules/_netdisco_api', 'NetDisco API Query Initialised...', 5))

    while True:
        try:
            # HTTPS Method
            api_key_post = requests.post('https://' + str(SESSION_TK.netdisco_url) + '/login',
                auth=(SESSION_TK.netdisco_username, SESSION_TK.netdisco_password),
                headers={'Accept': 'application/json'}, verify=False)
            api_get_devices = requests.get('https://' + str(SESSION_TK.netdisco_url) + '/api/v1/report/device/devicebylocation',
                headers={'Accept': 'application/json',
               'Authorization': api_key_post.json()['api_key'] })       
            netdisco_api_log.append(('%modules/_netdisco_api','NetDisco API HTTPS Method Used.', 5))
        
        except requests.exceptions.SSLError as error: 
            # HTTP Method
            api_key_post = requests.post('http://' + str(SESSION_TK.netdisco_url) + '/login',
                auth=(SESSION_TK.netdisco_username, SESSION_TK.netdisco_password),
                headers={'Accept': 'application/json'})
            api_get_devices = requests.get('http://' + str(SESSION_TK.netdisco_url) + '/api/v1/report/device/devicebylocation',
                headers={'Accept': 'application/json',
               'Authorization': api_key_post.json()['api_key'] })
            netdisco_api_log.append(('%modules/_netdisco_api','NetDisco API HTTP Method Used.', 5))
            
        except Exception as error:
            netdisco_api_log.append(('%modules/_netdisco_api','NetDisco API Methods Not Supported: ' + str(error), 3))
            break

        if SESSION_TK.debug == 2:
            print('\n**DEBUG (modules/netdisco_api_api.py) : Netdisco API POST Key Response: ')
            print(api_key_post.json()['api_key'])
            print(json.dumps(api_key_post.json(), indent=2))

        '''   
        # Curiosity with NetDisco and occasional polling where it returns 401. Retry
        # but with delay

        if api_get_devices.status_code == 200:
            pass # OK

        if api_get_devices.status_code == 401:
            time.sleep(5)
            api_get_devices = requests.get('http://' + str(SESSION_TK.netdisco_url) + '/api/v1/report/device/devicebylocation',
                    headers={'Accept': 'application/json',
                   'Authorization': api_key_post.json()['api_key'] })
        '''

        # Generate Host List
        xlist = []

        for host in api_get_devices.json():
            xlist.append(host['name'])

        for host in xlist:
            # F(ORCE)PATTERN forces the pattern to be excluded. Handles instances
            # where the hostname matches both a I(NCLUDE)PATTERN and eX(CLUDE)PATTERN
            # e.g. DEV is excluded but PFW is included but we have DEV-PFW which we
            # want to force exclude.
            try:
                if any(fPAT in host for fPAT in SESSION_TK.fpattern): # FORCE Pattern
                    #partition = host.partition('.') # Partition FQDN using '.' as seperator (host.company.domain)
                    #netdisco_api_list.append(partition[0].upper()) # Only capture hostname from partition.
                    pass

                elif any(iPAT in host for iPAT in SESSION_TK.ipattern) \
                    and not any(xPAT in host for xPAT in SESSION_TK.xpattern):
                    partition = host.partition('.')
                    netdisco_api_list.append(partition[0].upper())

                else:
                    pass
                
            except Exception as error:
                pass 

        if SESSION_TK.debug == 2:
            print('\n**DEBUG: NetDisco Filtered List Generated:')
            print(pp.pprint(netdisco_api_list))

        netdisco_api_log.append(('%modules/_netdisco_api','NetDisco API Query Successful', 5))
        netdisco_api_status = True
        break 

    #except Exception as error:
    #    netdisco_api_log.append(('%modules/_netdisco_api','NetDisco API Error: ' + str(error) + \
    #        ". API error occasionally occurs for no reason. NetDisco inventory check skipped in this run. Re-run recommended!", 4))

    return netdisco_api_status, netdisco_api_log, netdisco_api_list
