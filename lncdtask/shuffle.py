#!/usr/bin/env python3
import numpy
import math
import numpy.matlib
import numpy.random

def shuf_for_ntrials(vec, ntrials):
    '''
     shuf_for_ntrials creates a shuffled vector
     repeated to match the number of trials
    >>> x = shuf_for_ntrials([1,2,3,4,5], 40) 
    >>> len(x)
    40
    >>> x = shuf_for_ntrials([1,2,3,4,5], 2) 
    >>> len(x)
    2
    '''
    nitems = len(vec)
    if nitems == 0 or ntrials == 0:
        return([])

    items_over = ntrials % nitems
    nfullvec = int(math.floor(ntrials/nitems))
    # have 3 items want 5 trials
    # nfullvec=1; items_over=2

    # repeat full vector as many times as we can
    mat = numpy.matlib.repmat(vec, 1, nfullvec).flatten()
    # then add a truncated shuffled vector as needed
    if items_over > 0:
        numpy.random.shuffle(vec)
        mat = numpy.append(mat, vec[:items_over])

    numpy.random.shuffle(mat)
    return(mat)


def dist_total_into_n(total, n):
    """
    @param: total  total to be distrubuted
    @param: n      number of elements
    @return: arr   array that sums to total
    eg. want 10 events binned into 5 runs
    >>> dist_total_into_n(10, 5)
    [2, 2, 2, 2, 2]
    >>> dist_total_into_n(11, 5)
    ValueError ....
    """
    if n == 0 or total == 0:
        return([])
    arr = [float(total)/float(n)]*n
    arr[0] = int(numpy.ceil(arr[0]))
    arr[1:] = [int(numpy.floor(x)) for x in arr[1:]]
    if numpy.sum(arr) != total:
        raise ValueError('total %d not matched in %s' % (total, arr))
    numpy.random.shuffle(arr)
    return(arr)
