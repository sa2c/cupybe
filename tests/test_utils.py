
import numpy as np


def check_float_equality(a,b):
    '''
    Check equality between two object having a ``values`` member (e.g.,
    ``pandas.Serie``s or ``pandas.DataFrame``s
    '''
    comp = a.values 
    ref = b.values
    den = (np.abs(comp) + np.abs(ref))
    check = np.abs(comp-ref)/ den
    
    assert np.all((check < 1e-5) | (a == b))


