"""
To Deal with the data files.
WIP
"""

def get_dump(profile_file):
    import subprocess
    import pandas as pd
    command = f"cube_dump -m all -x excl -z excl -c all -s csv2 {profile_file}"
    cube_dump_process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
    return pd.read_csv(cube_dump_process.stdout,sep = '\s*,\s*', engine = 'python').set_index(['Cnode ID','Thread ID'])


