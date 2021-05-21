'''
LibraNMS API Module to Query Network Devices
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

def libranms_api():

    libranms_api_status = False
    libranms_api_log = []
    libranms_api_list = []

    libranms_api_log.append(('%modules/_libranms_api', 'LibraNMS API Query Initialised...', 5))

    try:
        # Define Global API POST request values
        payload = {}
        headers = {
          'X-Auth-Token': SESSION_TK.libranms_xauth_token,
          'cache-control': 'no-cache',
          'Accept': 'application/json'
        }
        url = "http://" + str(SESSION_TK.libranms_url) + '/api/v0/devices'

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
            if item['type'] == 'network':
                stripped = item['hostname'].rstrip(str(SESSION_TK.dom_strip))
                libranms_api_list.append(stripped.upper())
                
        libranms_api_log.append(('%modules/_libranms_api', 'LibraNMS API Successful', 5))
        libranms_api_status = True

    except Exception as error:
        libranms_api_log.append(('%modules/_libranms_api','LibraNMS API Error: ' + str(error), 4))

    return libranms_api_status, libranms_api_log, libranms_api_list
