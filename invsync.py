'''
Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronized.
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

from argparse import ArgumentParser # Required for Command Line Argument parsing

import json # Required to process *.json ISE config file and Slack Posting
import os # Required for Log File Writing and get users home director
import socket # Required to get and log hostname
import datetime # Required for Start/ End time
import urllib3 # Required to disable SSL Warnings
import sys # Required for Python version check
import ipdb # Optional Debug. ipdb.set_trace()

# Import custom modules
from modules._diffgen import diffgen
from modules._ise_api import ise_api
from modules._netdisco_api import netdisco_api
from modules._librenms_api import librenms_api
from modules._nornir_yml import nornir_yml
from common._slack_api import slack_api
from common._session_tk import Session_tk # Import Session Token Class
SESSION_TK = Session_tk() # Define object from Class


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MASTER_LOG = []

# Detect Python version. Python Major=3, Minor=6 expected
if (sys.version_info < (3, 6)):
     print('Must be running Python 3.6 for Nornir Framework')
     sys.exit(1)

def main():
    '''
    Main Function
    '''

    # LOG Script Start Date/ Time
    start_time = datetime.datetime.now()

    # Date and Time in simple string format (YYYYMMDDHHMMSS).
    # Used in node_*node_c3k_collection.py to create unique repo folder.
    repo_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

    homedir = os.path.expanduser("~")
    hostname = socket.gethostname()

    MASTER_LOG.append(('%invsync','InvSync Python script started @ ' + \
        str(start_time) + ' by ' + str(homedir) + ' on ' + str(hostname), 5))

    while True:

        # Nornir YAML Query
        nornir_yml_status, nornir_yml_log, nornir_yml_list = nornir_yml()

        for line in nornir_yml_log:
            MASTER_LOG.append(line)

        if not nornir_yml_status: # False
            break

        # ISE API Query
        ise_api_status, ise_api_log, ise_api_list = ise_api()

        for line in ise_api_log:
            MASTER_LOG.append(line)

        if not ise_api_status: # False
            break

        # NetDisco API Query
        netdisco_api_status, netdisco_api_log, netdisco_api_list = netdisco_api()

        for line in netdisco_api_log:
            MASTER_LOG.append(line)

        if not netdisco_api_status: # False
            break

        # LibreNMS API Query
        librenms_api_status, librenms_api_log, librenms_api_list = librenms_api()

        for line in librenms_api_log:
            MASTER_LOG.append(line)

        if not librenms_api_status: # False
            break

        # DIFF Method
        xdict = {} # Use a dict key to dedup(licate)

        for y in nornir_yml_list:
            xdict[y] = ''

        for i in ise_api_list:
            xdict[i] = ''

        for n in netdisco_api_list:
            xdict[n] = ''

        for n in librenms_api_list:
            xdict[n] = ''

        # xdict {} should now contain all nodes across all methods

        # Call diffgen Module
        ydiff = diffgen(nornir_yml_list, xdict)
        idiff = diffgen(ise_api_list, xdict)
        ndiff = diffgen(netdisco_api_list, xdict)
        ldiff = diffgen(librenms_api_list, xdict)

        MASTER_LOG.append(('%invsync','*** RESULTS ***', 5))

        if idiff:
            MASTER_LOG.append(('%invsync','\n' + u'\u2717' + ' Missing from ISE Inventory ' + u'\u2717', 4))
        for i in idiff:
            MASTER_LOG.append(('%invsync',i, 4))

        if ydiff:
            MASTER_LOG.append(('%invsync','\n' + u'\u2717' + ' Missing from YAML Inventory ' + u'\u2717', 4))
        for y in ydiff:
            MASTER_LOG.append(('%invsync',y, 4))

        if ndiff:
            MASTER_LOG.append(('%invsync','\n' + u'\u2717' + ' Missing from NetDisco Inventory ' + u'\u2717', 4))
        for n in ndiff:
            MASTER_LOG.append(('%invsync',n, 4))

        if ldiff:
            MASTER_LOG.append(('%invsync','\n' + u'\u2717' + ' Missing from LibreNMS Inventory ' + u'\u2717', 4))
        for n in ldiff:
            MASTER_LOG.append(('%invsync',n, 4))


        if not idiff and not ydiff and not ndiff and not ldiff:
            MASTER_LOG.append(('%invsync','\n' + u'\u2714' + ' No Difference Found Between YAML, ISE and NetDisco Inventory', 4))

        break

    log_time = start_time.strftime('%Y_%m_%d_%H_%M_%S')
    end_time = datetime.datetime.now()
    diff_time = end_time - start_time

    MASTER_LOG.append(('%invsync','\nInvSync Python script ended @ ' + str(diff_time) + ' ~ Elapsed: ' + str(diff_time) + '\n', 5))

    # WRITE MASTER_LOG to file
    # Make a folder in script working directory to store results
    logdir = '../LOGS/network_invsync_log/'
    # Modify the time stamp to not contain special characters (: & /)

    try:
        os.makedirs(logdir)
    except FileExistsError:
        pass # Folder exisits so nothing to do

    logfile = open(logdir + str(repo_time) + '.log', 'w')

    for line in MASTER_LOG:
        logfile.write(str(line) + '\n')

    logfile.close()

    MASTER_LOG.append(('%invsync','\nMASTER_LOG Saved To ' + logdir + str(repo_time) + '.log\n', 5))

    # Print all lines in MASTER_LOG
    for line in MASTER_LOG:
        print(line)

    # POST to Slack MASTER_LOG lines flagged with 1
    if SESSION_TK.slack_post == 1: # True
        SLACK_LOG = []
        for line in MASTER_LOG:
            if line[2] <= 4:
                SLACK_LOG.append(line[1])

        slack_api_status = slack_api(SLACK_LOG, end_time)

        if slack_api_status:
            print('Posted to Slack')

if __name__ == "__main__":
    main()
