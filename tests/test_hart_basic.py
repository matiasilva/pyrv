import pytest
from elftools.elf.elffile import ELFFile

from pyrv.harts import Hart
from tests.helpers import compile_sourcefile, get_section_bytes


@pytest.fixture
def hart():
    return Hart()


def test_sim_control(build_dir):
    # compile test
    elf = compile_sourcefile(build_dir, "simexit.S")

    # collect facts


def test_load(build_dir, hart: Hart):
    """Test loading an ELF file, linker script works, memory contents match"""
    elf = compile_sourcefile(build_dir, "load.S")
    hart.load(elf)
    text_data = get_section_bytes(build_dir, "load.S", ".text")

    # read word by word and check
    for i in range(0, len(text_data), 4):
        addr = i + Hart.INSTRUCTION_MEMORY_BASE
        word = (
            text_data[i + 3] << 24
            | text_data[i + 2] << 16
            | text_data[i + 1] << 8
            | text_data[i]
        )
        assert hart.read(addr, 4) == word
