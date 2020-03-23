"""
Utilities to get metric informations out of the output of `cube_dump -w`.

"""
from collections import namedtuple

Metric = namedtuple('Metric', ['shortname', 'convertibility'])


def get_metric_lines(cube_dump_w_text):
    '''
    Select the lines relative to the metrics out of the output of 
    'cube_dump -w'.
    '''
    from cube_file_utils import get_lines
    return get_lines(
        cube_dump_w_text,
        start_hint='METRIC DIMENSION',
        end_hint='CALLTREE DIMENSION')


def parse_line(line):
    '''
    Read a single line out of the `cube_dump -w` output.
    INPUT:
    "PAPI_L1_ICM  ( id=11, PAPI_L1_ICM, #, UINT64, , Level 1 instruction cache misses. [ L2_RQSTS:ALL_CODE_RD ], INCLUSIVE convertible, cacheable)"
    OUTPUT:
    (PAPI_L1_ICM,"INCLUSIVE convertible")
    '''
    # this is brittle but should work for now.
    # TODO : Strengthen it.
    start_parens_idx = line.find('(')
    end_parens_idx = line.find(')')
    info = line[start_parens_idx + 1:end_parens_idx].split(',')
    return Metric(shortname=info[1].strip(), convertibility=info[6].strip())


def get_metric_info(lines):
    return [parse_line(line) for line in lines]

def get_inclusive_convertible_metrics(profile_file):
    from cube_file_utils import get_cube_dump_w_text
    cube_dump_w_text = get_cube_dump_w_text(profile_file)
    lines = get_metric_lines(cube_dump_w_text)
    metrics  = get_metric_info(lines)
    return set([metric.shortname for metric in metrics if metric.convertibility == 'INCLUSIVE convertible'])



