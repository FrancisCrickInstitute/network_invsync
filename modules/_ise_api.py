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

from modules._xtval import xtval
from common._session_tk import Session_tk # Import Session Token Class
SESSION_TK = Session_tk() # Define object from Class

pp = pprint.PrettyPrinter()

def ise_api():

    ise_api_status = False
    ise_api_log = []
    ise_api_list = []

    ise_api_log.append(('%modules/_ise_api', 'ISE API Query Initialised...', 5))

    try:
        # Define Global API POST request values
        payload = {}
        headers = {
          'Accept': 'application/vnd.com.cisco.ise.network.networkdevice.1.1+xml',
          'Accept-Search-Result': 'application/vnd.com.cisco.ise.ers.searchresult.2.0+xm',
          'Authorization': SESSION_TK.ise_oauth_token,
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

        for page in range(SESSION_TK.ise_pages):

            url = "https://" + str(SESSION_TK.ise_url) + ":9060/ers/config/networkdevice?size=100&page=" + str(page+1)

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

        # Parse through XTVAL module to extract required values
        # ids = xtval(xdoc, '@id')
        hosts = xtval(xdoc, '@name')

        # Loop through hosts. If host name contains iPATTERN and not xPATTERN append
        # to ise_api_list []

        for host in hosts:
            # F(ORCE)PATTERN forces the pattern to be excluded. Handles instances
            # where the hostname matches both a I(NCLUDE)PATTERN and eX(CLUDE)PATTERN
            # e.g. DEV is excluded but PFW is included but we have DEV-PFW which we
            # want to force exclude.
            if any(fPAT in host for fPAT in SESSION_TK.fpattern):
                #partition = host.partition('.') # Partition FQDN using '.' as seperator (host.company.domain)
                #ise_api_list.append(partition[0].upper()) # Only capture hostname from partition.
                pass

            elif any(iPAT in host for iPAT in SESSION_TK.ipattern) \
                and not any(xPAT in host for xPAT in SESSION_TK.xpattern):
                partition = host.partition('.') # Partition FQDN using '.' as seperator (host.company.domain)
                ise_api_list.append(partition[0].upper()) # Only capture hostname from partition.

            else:
                pass

        if SESSION_TK.debug >= 1:
            print('\n**DEBUG ISE Filtered List Generated:')
            print(pp.pprint(ise_api_list))

        ise_api_log.append(('%modules/_ise_api', 'ISE API Successful', 5))
        ise_api_status = True

    except Exception as error:
        ise_api_log.append(('%modules/_ise_api','ISE API Error: ' + str(error), 4))

    return ise_api_status, ise_api_log, ise_api_list
