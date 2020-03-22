"""
Utilities to obtain pandas dataframes with all the metrics out of '.cubex' 
files via "cube_dump".
"""

def get_dump(profile_file, exclusive = True):
    '''
    Thin wrapper around `pandas.read_csv`.
    '''
    import subprocess
    import pandas as pd
    excl_incl = 'excl' if exclusive == True else 'incl'
    command = f"cube_dump -m all -x excl -z {excl_incl} -c all -s csv2 {profile_file}"
    cube_dump_process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
    return pd.read_csv(cube_dump_process.stdout,sep = '\s*,\s*', engine = 'python')

