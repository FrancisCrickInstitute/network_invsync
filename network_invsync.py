'''
Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronized.
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

from argparse import ArgumentParser # Required for Command Line Argument parsing

import json # Required to process *.json ISE config file and Slack Posting
import os # Required for Log File Writing
import datetime # Required for Start/ End time
import urllib3 # Required to disable SSL Warnings
#import ipdb # Optional Debug. ipdb.set_trace()

# Import custom modules
from modules.diffgen import diffgen
from modules.ise_api import ise_api
from modules.nornir_yml import nornir_yml
from modules.netdisco_api import netdisco_api
from modules.slackpost import slackpost

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    ''' MAIN FUNCTION '''

    SESSION_TK = {}
    MASTER_LOG = [] # MASTER_LOG as list of tuples. Logs flagged with 1 to be sent to
                    # slackpost.
    status = False

    print('\nQuerying ISE, YAML and NetMiko Inventory. Please Wait...')

    start_time = datetime.datetime.now()

    # Process Command Line Argument
    parser = ArgumentParser(description='Usage:')
    parser.add_argument('-d', '--basicdebug', action='store_true',
                        help='Basic Debug')
    parser.add_argument('-v', '--verbosedebug', action='store_true',
                        help='Verbose Debug')
    arg = parser.parse_args()

    SESSION_TK['bDEBUG'] = arg.basicdebug
    SESSION_TK['vDEBUG'] = arg.verbosedebug

    MASTER_LOG.append(('Network InvSync Script Results...', 1))

    # File Method
    try:
        # Read INVSYNC Config File
        invsync_cfg_f = 'config/invsync_cfg.json' # Script Config File.

        with open(invsync_cfg_f) as cfg_f:
            cfg = json.load(cfg_f)

        SESSION_TK['iPATTERN'] = cfg["iPATTERN"] # ISE Include Pattern
        SESSION_TK['xPATTERN'] = cfg["xPATTERN"] # ISE Exclude Pattern
        SESSION_TK['dSTRIP'] = cfg["dSTRIP"] # Domain Strip Patter
        SESSION_TK['yFILTER'] = cfg["yFILTER"] # YAML Group
        SESSION_TK['SLACKPOST'] = cfg['SLACKPOST']

    except Exception as error:
        MASTER_LOG.append(('INVSYNC Config File Error: ' + str(error) + '. ' \
            + str(invsync_cfg_f) + ' Missing or Invalid!', 1))

    # GET Query Methods
    try:
        while True:
            # ISE API Query
            ise_status, ise_log, ise_list = ise_api(SESSION_TK)

            for line in ise_log:
                MASTER_LOG.append(line)

            if not ise_status: # False
                status = False
                break

            # Nornir YAML Query
            nornir_status, nornir_log, nornir_list = nornir_yml(SESSION_TK)

            for line in nornir_log:
                MASTER_LOG.append(line)

            if not nornir_status: # False
                status = False
                break

            # NetDisco API Query
            netdisco_status, netdisco_log, netdisco_list = netdisco_api(SESSION_TK)

            for line in netdisco_log:
                MASTER_LOG.append(line)

            if not netdisco_status: # False
                status = False
                break

            status = True

            break

    except Exception as error:
        MASTER_LOG.append(('Query Error: ' + str(error), 1))

    # DIFF Method
    if status: # True

        xdict = {} # Use a dict to de-duplicate

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

        if idiff:
            MASTER_LOG.append(('\n** Missing from ISE Inventory:', 1))
            for i in idiff:
                MASTER_LOG.append((i, 1))

        if ydiff:
            MASTER_LOG.append(('\n** Missing from YAML Inventory:', 1))
            for y in ydiff:
                MASTER_LOG.append((y, 1))

        if ndiff:
            MASTER_LOG.append(('\n** Missing from NetDisco Inventory:', 1))
            for n in ndiff:
                MASTER_LOG.append((n, 1))

        if not idiff and not ydiff and not ndiff:
            MASTER_LOG.append(('\n** No Difference Found Between YAML, ISE and NetDisco Inventory ' + u'\u2714', 1))

    # WRITE MASTER_LOG to file
    # Make a folder in script working directory to store results
    logdir = '../LOGS/network_invsync_log/'
    # Modify the time stamp to not contain special characters (: & /)
    log_time = start_time.strftime('%Y_%m_%d_%H_%M_%S')

    try:
        os.makedirs(logdir)
    except FileExistsError:
        pass # Folder exisits so nothing to do

    logfile = open(logdir + str(log_time) + '.log', 'w')

    for line in MASTER_LOG:
        logfile.write(str(line[0]) + '\n')

    logfile.close()

    for line in MASTER_LOG:
        print(line)

    print('MASTER_LOG saved to ' + str(logfile))

    # POST to Slack
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
