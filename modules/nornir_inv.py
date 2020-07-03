'''
Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronized.
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import pprint # Optional to Pretty Print Responses
import ipdb # Optional Debug. ipdb.set_trace()

from nornir import InitNornir # Required for YAML
from nornir.core.filter import F

pp = pprint.PrettyPrinter()

def nornir_inv(SESSION_TK):

    print('\n' + '#' * 10 + ' Nornir Inventory Query ' + '#' * 10 + '\n')

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG Nornir YAML SESSION_TK Received:')
        print(pp.pprint(SESSION_TK))

    ylist = []

    nr = InitNornir(config_file='config/nornir_inv.yaml')

    filter  = nr.filter(F(groups__contains=SESSION_TK['yFILTER'][0]))
    for i in filter.inventory.hosts.keys():
         ylist.append(i)

    if SESSION_TK['bDEBUG']: # True
        print('\n**DEBUG Nornir YAML List Generated:')
        print(pp.pprint(ylist))

    return ylist
