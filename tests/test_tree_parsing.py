#!/usr/bin/env python3
from sys import argv
import calltree as ct
import cube_file_utils as cfu
import tree_parsing as tp
from test_utils import SINGLE_FILES
import pytest

@pytest.mark.parametrize("filename",SINGLE_FILES)
def test_tree_parsing(filename):
    lines = ct.get_call_tree_lines(cfu.get_cube_dump_w_text(filename))
    assert list(tp.iterate(tp.collect_hierarchy(lines, tp.level_fun))) == lines

if __name__ == "__main__":
    print("All ok")
