import pytest
from elftools.elf.elffile import ELFFile

from tests.helpers import compile_sourcefile


def test_sim_control(build_dir):
    # compile test
    elf = compile_sourcefile(build_dir, "simexit.S")

    # collect facts
    with open(elf, "rb") as f:
        elf_file = ELFFile(f)
        print(elf_file.header.e_entry)
