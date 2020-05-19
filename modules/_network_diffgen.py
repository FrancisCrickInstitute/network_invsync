'''
Python3 Script to Identify Differences Between Two Lists
'''
#!/usr/bin/env python

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import ipdb # Optional Debug. ipdb.set_trace()

def diff(listA, listB):
    '''
    DIFF Function See 'https://www.geeksforgeeks.org/python-set-difference/'
    to understand usage.
    '''
    return list(set(listA) - set(listB))

def diffgen(ilist, ylist):
    '''
    DIFFGEN Function
    '''

    idiff = []
    ydiff = []

    try:

        # Generaate list of nodes configured on ISE but not in YAML
        idiff = diff(ilist, ylist)

        # Generate list of nodes configured in YSML but no in ISE
        ydiff = diff(ylist, ilist)

    except:
        pass

    return (idiff, ydiff)
