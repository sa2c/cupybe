
import numpy as np

SINGLE_FILE="../test_data/profile.cubex"
SINGLE_FILE_SAMPLING="../test_data/profile.wsampling.cubex"
SINGLE_FILE_CPP="../test_data/profile_cpp.cubex"
SCALASCA_OUTPUT="../test_data/scalasca_output"

SINGLE_FILES = [SINGLE_FILE,SINGLE_FILE_SAMPLING,SINGLE_FILE_CPP]


def check_float_equality(a,b,tolerance = 1e-5):
    '''
    Check equality between two object having a ``values`` member (e.g.,
    ``pandas.Serie``s or ``pandas.DataFrame``s.

    Generates an ``AssertionError`` if the relative error exceeds the 
    specified tolerance.

    Parameters
    ----------
    a,b : pandas.DataFrames, pandas.Series
        The objects to compare
    tolerance: float
        The maximum accepted relative error


    '''
    comp = a.values 
    ref = b.values
    den = (np.abs(comp) + np.abs(ref))
    check = np.abs(comp-ref)/ den
    
    assert np.all((check < tolerance) | (a == b)), np.max(check[a!=b])


