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

def diffgen(xlist, xdict):
    '''
    DIFFGEN Function
    '''

    qdiff = []
    qlist = []

    for k in xdict.keys():
        if k in xlist:
            pass
        else:
            qlist.append(k)

    return qlist
