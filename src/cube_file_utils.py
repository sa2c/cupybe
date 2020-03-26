"""
This module contains low-level functions that wrap/call the
``cube_dump`` utility.
"""
import subprocess
import logging
import sys
import pandas as pd


class CubeDumpException(Exception):
    pass


def get_cube_dump_w_text(profile_file):
    """Simple function that calls ``cube_dump -w`` and gets the output as a
    string.

    Parameters
    ==========
    profile_file : str
        Name of the ``*.cubex`` file.

    Returns
    =======
    cube_dump_w_text : str
        Output of ``cube_dump -w``
    """

    if sys.version_info >= (3, 7, 0):
        cube_dump_process = subprocess.run(
            ["cube_dump", "-w", profile_file], capture_output=True, text=True
        )

    if sys.version_info < (3, 7, 0):
        cube_dump_process = subprocess.run(
            ["cube_dump", "-w", profile_file],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

    if cube_dump_process.returncode:
        raise CubeDumpException(
            f"Cube dump run failed with error code \
            {int(cube_dump_process.returncode)}.\n\
            Is {profile_file} a valid profile file? \
            {cube_dump_process.stderr}"
        )

    return cube_dump_process.stdout


def get_lines(cube_dump_w_text, start_hint, end_hint):
    """
    Select a section of the output of 'cube_dump -w'.

    Parameters
    ==========
    cube_dump_w_text : str
        Text containing the whole output of ``cube_dump -w``
    start_hint : str
        String signalling the beginning of the section of interest.
    end_hint : str
        String signalling the end of the section of interest.

    Returns
    =======
    lines : list of str
        List of all non-empty lines between start_hint and end_hint.
    """

    all_lines = cube_dump_w_text.split("\n")
    start_line_idx = next(i for i, l in enumerate(all_lines) if start_hint in l)
    stop_line_idx = next(i for i, l in enumerate(all_lines) if end_hint in l)
    lines = [
        l for l in all_lines[start_line_idx + 1 : stop_line_idx] if len(l.strip()) != 0
    ]
    logging.debug(f"No of lines: {len(lines)}\n")
    return lines


def get_dump(profile_file, exclusive=True):
    """ Parses output of ``cube_dump`` on a ``.cubex`` file and returns a
    dataframe.

    Thin wrapper around ``pandas.read_csv``, to obtain pandas dataframes 
    with all the metrics out of ``.cubex`` files via ``cube_dump``.
    The layout of the dataframe is the same as the one coming out of 
    ``cube_dump``.

    Parameters
    ==========
    profile_file : str
        Name of the ``.cubex`` file.
    exclusive : bool
        Whether to ask ``cube_dump`` for exclusive (True) or inclusive (False) 
        metrics.

    Returns
    =======
    res : pandas.DataFrame
        A DataFrame containing all the metrics in the ``.cubex`` file. 
    """
    excl_incl = "excl" if exclusive == True else "incl"
    command = f"cube_dump -m all -x excl -z {excl_incl} -c all -s csv2 {profile_file}"
    cube_dump_process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return pd.read_csv(cube_dump_process.stdout, sep="\s*,\s*", engine="python")
