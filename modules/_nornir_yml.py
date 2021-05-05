'''
Nornir Module to Query YAML Inventory
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import pprint # Optional to Pretty Print Responses
import ipdb # Optional Debug. ipdb.set_trace()

from nornir import InitNornir # Required for YAML
from nornir.core.filter import F

from common._session_tk import Session_tk # Import Session Token Class
SESSION_TK = Session_tk() # Define object from Class

pp = pprint.PrettyPrinter()

def nornir_yml():

    nornir_yml_status = False
    nornir_yml_log = []
    nornir_yml_list = []

    nornir_yml_log.append(('%modules/_nornir_yml','Nornir YAML Query Initialised...', 5))

    if SESSION_TK.debug == 2: # True
        print('\n***DEBUG Nornir YAML SESSION_TK Received:')
        print(pp.pprint(SESSION_TK))

    try:
        nr = InitNornir(config_file='config/nornir_cfg.yaml')

        filter  = nr.filter(F(groups__contains=SESSION_TK.yaml_filter[0]))
        for i in filter.inventory.hosts.keys():
            nornir_yml_list.append(i)

        if SESSION_TK.debug == 2: # True
            print('\n**DEBUG Nornir YAML List Generated:')
            print(pp.pprint(nornir_yml_list))

        nornir_yml_status = True
        nornir_yml_log.append(('%modules/_nornir_yml','Nornir YAML Query Successful', 5))

    except Exception as error:
        nornir_yml_log.append(('%modules/_ise_api','Nornir YAML Query Error: ' + str(error), 4))

    return nornir_yml_status, nornir_yml_log, nornir_yml_list
