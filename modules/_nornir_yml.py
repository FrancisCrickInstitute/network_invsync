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

        for group in SESSION_TK.yaml_filter:
            filter  = nr.filter(F(groups__contains=group))
            for host in filter.inventory.hosts.keys():
                # F(ORCE)PATTERN forces the pattern to be excluded. Handles instances
                # where the hostname matches both a I(NCLUDE)PATTERN and eX(CLUDE)PATTERN
                # e.g. DEV is excluded but PFW is included but we have DEV-PFW which we
                # want to force exclude.
                if any(fPAT in host.upper() for fPAT in SESSION_TK.fpattern):
                    #partition = host['hostname'].partition('.') # Partition FQDN using '.' as seperator (host.company.domain)
                    #librenms_api_list.append(partition[0].upper()) # Only capture hostname from partition.
                    pass
    
                elif any(iPAT in host for iPAT in SESSION_TK.ipattern) \
                    and not any(xPAT in host for xPAT in SESSION_TK.xpattern):
                    nornir_yml_list.append(host)
    
                else:
                    pass
    
        if SESSION_TK.debug == 2: # True
            print('\n**DEBUG Nornir YAML List Generated:')
            print(pp.pprint(nornir_yml_list))

        nornir_yml_status = True
        nornir_yml_log.append(('%modules/_nornir_yml','Nornir YAML Query Successful', 5))

    except Exception as error:
        nornir_yml_log.append(('%modules/_ise_api','Nornir YAML Query Error: ' + str(error), 4))

    return nornir_yml_status, nornir_yml_log, nornir_yml_list
