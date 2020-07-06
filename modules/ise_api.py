'''
ISE API Module to Query Network Devices
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

from modules.xtval import xtval

pp = pprint.PrettyPrinter()

def ise_api(SESSION_TK):

    ise_status = False
    ise_log = []
    ise_list = []

    ise_log.append(('ISE API Query Initialised...', 0))

    print('\n' + '#' * 10 + ' ISE API Query ' + '#' * 10 + '\n')

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG ISE SESSION_TK Received:')
        print(pp.pprint(SESSION_TK))

    # Read .json config for required ISE values.
    ise_cfg_f = 'config/ise_cfg.json' # Script Config File.

    try:
        with open(ise_cfg_f) as ise_f:
            ise_cfg = json.load(ise_f)

        OAUTH = ise_cfg["OAUTH"]
        URL = ise_cfg['URL']
        PAGES = ise_cfg['PAGES']

    except Exception as error:
        ise_log.append(('ISE Error: ' + str(error) + '. ' + str(ise_cfg_f) \
            + ' missing or invalid', 1))
        return ise_status, ise_log, ise_list

    try:
        # Define Global API POST request values
        payload = {}
        headers = {
          'Accept': 'application/vnd.com.cisco.ise.network.networkdevice.1.1+xml',
          'Accept-Search-Result': 'application/vnd.com.cisco.ise.ers.searchresult.2.0+xm',
          'Authorization': OAUTH,
          'cache-control': 'no-cache'
        }

        # Define POST request URI.
        # Truely herendous hack due to Cisco ISE page size limitation of 100 results!!!
        # If you have more than 100 devices you need two posts to accomodate each page.
        # Also, by default ISE has a max size of 20 so this needs to be increased to
        # max 100: ?size=100&page=* where * is a page number.
        # Without this, ERS returns a max of 20 nodes (why Cisco?).
        # See: https://community.cisco.com/t5/network-access-control/ers-returns-max-20-endpoints/m-p/3499483

        xdoc = []

        for page in range(PAGES):

            url = "https://" + str(URL) + ":9060/ers/config/networkdevice?size=100&page=" + str(page+1)

            # POST GET Response. User verify=False to disable SSL wanrings
            response = requests.request("GET", url, headers=headers, data=payload, verify=False)

            # Curiosity with ISE and occasional polling where it returns 401. Retry
            # but with delay

            if response.status_code == 200:
                pass # OK

            if response.status_code == 401:
                time.sleep(5)
                response = requests.request("GET", url, headers=headers, data=payload, verify=False)

            # Convert to Python Dict {} and append to xdoc []
            xdoc.append(xmltodict.parse(response.text.encode('utf8')))

        if SESSION_TK['vDEBUG']: # True
            print('\n***DEBUG ISE GET Response:')
            print(pp.pprint(xdoc))

        # Parse through XTVAL module to extract required values
        # ids = xtval(xdoc, '@id')
        hosts = xtval(xdoc, '@name')

        # Loop through hosts. If host name contains iPATTERN and not xPATTERN append
        # to ise_list []

        for host in hosts:
            if any(iPAT in host for iPAT in SESSION_TK['iPATTERN']) and not any(xPAT in host for xPAT in SESSION_TK['xPATTERN']):
                ise_list.append(host)

        if SESSION_TK['bDEBUG']: # True
            print('\n**DEBUG ISE Filtered List Generated:')
            print(pp.pprint(ise_list))

        ise_log.append(('ISE API Successful', 0))
        ise_status = True

    except Exception as error:
        ise_log.append(('ISE API Error: ' + str(error), 1))

    return ise_status, ise_log, ise_list
