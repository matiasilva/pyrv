import struct
import subprocess
from pathlib import Path

import pytest

from pyrv.instructions import decode_instr
from tests.helpers import get_rel_file, rvbinpath
from tests.testcases.decode import DECODE_TESTCASES

ASSEMBLER_CMD = [rvbinpath("as"), "-march=rv32i", "-mabi=ilp32"]
ELF2BIN_CMD = [
    rvbinpath("objcopy"),
    "-S",
    "-O",
    "binary",
    "--only-section=.text",
]


def compile_assembly(build_dir: Path) -> Path:
    """Compile assembly file to elf"""
    out_path = build_dir / "test.elf"
    in_path = get_rel_file("testcases/decode.s")
    cmd = ASSEMBLER_CMD + ["-o", str(out_path), str(in_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"asm compilation failed:\n{result.stderr}\n{result.args}")

    return out_path


def elf2bin(in_path: Path, build_dir: Path) -> Path:
    """Extract the instructions from an elf file and store them in a binary"""
    out_path = build_dir / "test.bin"
    cmd = ELF2BIN_CMD + [str(in_path), str(out_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f".text extraction failed:\n{result.stderr}")

    return out_path


@pytest.fixture(scope="session")
def instr_words(build_dir: Path) -> list:
    """Fixture to compile test assembly into list of words"""

    elf_path = compile_assembly(build_dir)
    bin_path = elf2bin(elf_path, build_dir)
    bin_data = bin_path.read_bytes()
    words = list(struct.unpack(f"<{len(bin_data) // 4}I", bin_data))
    return words


def test_instr_decode_from_bin(instr_words):
    """Instruction decode litmus test for all RV32I instructions"""

    instrs = [decode_instr(instr) for instr in instr_words]
    for exp, true in zip(instrs, DECODE_TESTCASES, strict=True):
        assert exp == true


def test_instr_decode_from_asm(instr_words):
    pass
