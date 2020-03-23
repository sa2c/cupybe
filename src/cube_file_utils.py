

def get_cube_dump_w_text(profile_file):
    import subprocess
    cube_dump_process = subprocess.run(['cube_dump', '-w', profile_file],
                                       capture_output=True,
                                       text=True)
    return cube_dump_process.stdout

def get_lines(cube_dump_w_text, start_hint, end_hint):
    '''
    Select the lines relative to the call tree out of the
    output of 'cube_dump -w'.
    '''
    import logging
    all_lines = cube_dump_w_text.split('\n')
    start_line_idx = next(i for i, l in enumerate(all_lines)
                          if start_hint in l)
    stop_line_idx = next(i for i, l in enumerate(all_lines)
                                   if end_hint in l)
    lines = [
        l for l in all_lines[start_line_idx + 1:stop_line_idx]
        if len(l.strip()) != 0
    ]
    logging.debug(f"No of lines: {len(lines)}\n")
    return lines


