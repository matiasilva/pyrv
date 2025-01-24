import os
import struct
import subprocess
from pathlib import Path

import pytest

from pyrv.instructions import decode_instr
from tests.testcases.decode import DECODE_TESTCASES

RISCV_TOOLCHAIN_PATH = os.getenv('RISCV_TOOLCHAIN_PATH')
RISCV_TOOLCHAIN_PREFIX = os.getenv('RISCV_TOOLCHAIN_PREFIX', 'riscv64')


def rvbinpath(gnu_bin: str) -> str:
    """Return the string path to a valid RISC-V binary on the system"""

    p = f"{RISCV_TOOLCHAIN_PREFIX}-unknown-elf-{gnu_bin}"
    if RISCV_TOOLCHAIN_PATH and (the_path := Path(RISCV_TOOLCHAIN_PATH)).is_dir():
        p = the_path / p

    return str(p)

ASSEMBLER_CMD = [rvbinpath('as'), "-march=rv32i", "-mabi=ilp32"]
ELF2BIN_CMD = [
    rvbinpath('objcopy'),
    "-S",
    "-O",
    "binary",
    "--only-section=.text",
]

def get_rel_file(file_path: str):
    """Retrieve the absolute path of a file relative to the tests directory"""
    return Path(__file__).parent / file_path


@pytest.fixture(scope="session")
def build_dir(tmp_path_factory):
    """Create a temporary build directory that persists for the test session"""
    return tmp_path_factory.mktemp("build")


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
