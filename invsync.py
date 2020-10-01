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
from modules._session_tk import session_tk
from modules._diffgen import diffgen
from modules._ise_api import ise_api
from modules._nornir import nornir
from modules._netdisco_api import netdisco_api
from modules._slackpost import slackpost

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
    repo_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    homedir = os.path.expanduser("~")
    hostname = socket.gethostname()

    MASTER_LOG.append(('InvSync Python script started @ ' + str(start_time) + '\n' + ' by ' + str(homedir) + ' on ' + str(hostname), 1))

    while True:
        try:

            # Generate SESSION_TK
            session_tk_status, session_tk_log, SESSION_TK = session_tk()

            for line in session_tk_log:
                MASTER_LOG.append(line)

            if not session_tk_status:
                break

            if SESSION_TK['DEBUG'] == 2:
                print('\n**DEBUG: SESSION_TK:')
                print(SESSION_TK)

            # ISE API Query
            ise_status, ise_log, ise_list = ise_api(SESSION_TK)

            for line in ise_log:
                MASTER_LOG.append(line)

            if not ise_status: # False
                break

            # Nornir YAML Query
            nornir_status, nornir_log, nornir_list = nornir(SESSION_TK)

            for line in nornir_log:
                MASTER_LOG.append(line)

            if not nornir_status: # False
                break

            # NetDisco API Query
            netdisco_status, netdisco_log, netdisco_list = netdisco_api(SESSION_TK)

            for line in netdisco_log:
                MASTER_LOG.append(line)

            if not netdisco_status: # False
                break

            # DIFF Method
            xdict = {} # Use a dict key to dedup(licate)

            for i in ise_list:
                xdict[i] = ''

            for y in nornir_list:
                xdict[y] = ''

            for n in netdisco_list:
                xdict[n] = ''

            # xdict {} should now contain all nodes across all methods

            # Call diffgen Module
            idiff = diffgen(ise_list, xdict)
            ydiff = diffgen(nornir_list, xdict)
            ndiff = diffgen(netdisco_list, xdict)

            MASTER_LOG.append(('\n*** RESULTS ***', 1))

            if idiff:
                MASTER_LOG.append(('\n' + u'\u2717' + ' Missing from ISE Inventory ' + u'\u2717', 1))
            for i in idiff:
                MASTER_LOG.append((i, 1))

            if ydiff:
                MASTER_LOG.append(('\n' + u'\u2717' + ' Missing from YAML Inventory ' + u'\u2717', 1))
            for y in ydiff:
                MASTER_LOG.append((y, 1))

            if ndiff:
                MASTER_LOG.append(('\n' + u'\u2717' + ' Missing from NetDisco Inventory ' + u'\u2717', 1))
            for n in ndiff:
                MASTER_LOG.append((n, 1))

            if not idiff and not ydiff and not ndiff:
                MASTER_LOG.append(('\n' + u'\u2714' + ' No Difference Found Between YAML, ISE and NetDisco Inventory', 1))

            break

        except Exception as error:
            MASTER_LOG.append(('InvSync Error: ' + str(error), 1))


    log_time = start_time.strftime('%Y_%m_%d_%H_%M_%S')
    end_time = datetime.datetime.now()
    diff_time = end_time - start_time

    MASTER_LOG.append(('\nInvSync Python script ended @ ' + str(diff_time) + ' ~ Elapsed: ' + str(diff_time) + '\n', 1))

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
        logfile.write(str(line[0]) + '\n')

    logfile.close()

    MASTER_LOG.append(('\nMASTER_LOG Saved To ' + logdir + str(log_time) + '.log\n', 1))

    # Print all lines in MASTER_LOG
    for line in MASTER_LOG:
        if line[1] >= 0:
            print(line[0])

    # POST to Slack MASTER_LOG lines flagged with 1
    if SESSION_TK['SLACKPOST'] == 1: # True
        SLACK_LOG = []
        for line in MASTER_LOG:
            if line[1] == 1:
                SLACK_LOG.append(line[0])

        slackpost_status = slackpost(SLACK_LOG)

        if slackpost_status:
            print('Posted to Slack')

if __name__ == "__main__":
    main()
