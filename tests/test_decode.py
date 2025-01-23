import os
import subprocess
from pathlib import Path

import pytest

from pyrv.instructions import decode_instr

ASSEMBLER_CMD = (
    "riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o {out_file} {in_file}"
)
BIN_CMD = "riscv64-unknown-elf-objcopy -S -O binary {in_file} {out_file}"


def get_rel_file(file_path: str):
    """Retrieve the absolute path of a file relative to the tests directory"""
    return Path(__file__).parent / file_path


@pytest.fixture(scope="session")
def build_dir(tmp_path_factory):
    """Create a temporary build directory that persists for the test session"""
    return tmp_path_factory.mktemp("build")


def compile_assembly(build_dir: Path) -> Path:
    """Compile assembly file to binary"""
    out_path = build_dir / "test.elf"
    in_path = get_rel_file("testcases/decode.s")
    cmd = ASSEMBLER_CMD.format(out_path, in_path)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"asm compilation failed:\n{result.stderr}")

    return out_path


def link_binary(obj_path: Path, build_dir: Path, linker_cmd: list) -> Path:
    """Link object file to executable"""
    bin_path = build_dir / obj_path.stem
    cmd = [*linker_cmd, "-o", str(bin_path), str(obj_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Linking failed:\n{result.stderr}")

    return bin_path


@pytest.fixture
def test_binary(tmp_path, build_dir, assembler_cmd, linker_cmd):
    """Fixture to compile test assembly into binary"""
    # Assuming test files are in a 'test_asm' directory next to the test file
    asm_dir = Path(__file__).parent / "test_asm"
    test_asm = asm_dir / "test.asm"

    obj_file = self.compile_assembly(test_asm, build_dir, assembler_cmd)
    binary = self.link_binary(obj_file, build_dir, linker_cmd)

    return binary


def test_binary_execution(test_binary):
    """Example test that runs the binary and checks its output"""
    result = subprocess.run([str(test_binary)], capture_output=True)
    assert result.returncode == 0
    # Add your binary processing and assertions here
