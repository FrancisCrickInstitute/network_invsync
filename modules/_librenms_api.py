'''
Librenms API Module to Query Network Devices
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

def librenms_api():

    librenms_api_status = False
    librenms_api_log = []
    librenms_api_list = []

    librenms_api_log.append(('%modules/_librenms_api', 'librenms API Query Initialised...', 5))

    try:
        # Define Global API POST request values
        payload = {}
        headers = {
          'X-Auth-Token': SESSION_TK.librenms_xauth_token,
          'cache-control': 'no-cache',
          'Accept': 'application/json'
        }
        url = "http://" + str(SESSION_TK.librenms_url) + '/api/v0/devices'

        # POST GET Response. User verify=False to disable SSL wanrings
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        if response.status_code == 200:
            pass # OK

        if response.status_code == 401:
            time.sleep(5)
            response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        # Convert from JSON to Python Dict
        xdict = json.loads(response.text)

        for item in xdict['devices']:
            if item['type'] == 'network' or \
                item['type'] == 'wireless' or \
                item['type'] == 'firewall':
                if any(iPAT in item['hostname'].upper() for iPAT in SESSION_TK.ipattern) \
                    and not any(xPAT in item['hostname'].upper() for xPAT in SESSION_TK.xpattern):
                    partition = item['hostname'].partition('.')
                    librenms_api_list.append(partition[0].upper())

        if SESSION_TK.debug == 2:
            print('\n**DEBUG: LibreNMS Filtered List Generated:')
            print(pp.pprint(librenms_api_list))

        librenms_api_log.append(('%modules/_librenms_api', 'librenms API Successful', 5))
        librenms_api_status = True

    except Exception as error:
        librenms_api_log.append(('%modules/_librenms_api','librenms API Error: ' + str(error), 4))

    return librenms_api_status, librenms_api_log, librenms_api_list
