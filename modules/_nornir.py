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

pp = pprint.PrettyPrinter()

def nornir(SESSION_TK):

    nornir_status = False
    nornir_log = []
    nornir_list = []

    nornir_log.append(('Nornir YAML Query Initialised...', 0))

    print('\n' + '#' * 10 + ' Nornir Inventory Query ' + '#' * 10 + '\n')

    if SESSION_TK['DEBUG'] == 2: # True
        print('\n***DEBUG Nornir YAML SESSION_TK Received:')
        print(pp.pprint(SESSION_TK))

    try:
        nr = InitNornir(config_file='config/nornir_cfg.yaml')

        filter  = nr.filter(F(groups__contains=SESSION_TK['yFILTER'][0]))
        for i in filter.inventory.hosts.keys():
            nornir_list.append(i)

        if SESSION_TK['DEBUG'] == 2: # True
            print('\n**DEBUG Nornir YAML List Generated:')
            print(pp.pprint(nornir_list))

        nornir_status = True
        nornir_log.append(('Nornir YAML Query Successful', 0))

    except Exception as error:
        nornir_log.append(('Nornir YAML Query Error: ' + str(error), 1))

    return nornir_status, nornir_log, nornir_list
