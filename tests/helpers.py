import os
import subprocess
from pathlib import Path


def get_rel_file(file_path: str):
    """Retrieve the absolute path of a file relative to the tests directory"""
    return Path(__file__).parent / file_path


def rvbinpath(gnu_bin: str) -> str:
    """Return the string path to a valid RISC-V binary on the system"""

    RISCV_TOOLCHAIN_PATH = os.getenv("RISCV_TOOLCHAIN_PATH")
    RISCV_TOOLCHAIN_PREFIX = os.getenv("RISCV_TOOLCHAIN_PREFIX", "riscv64")

    p = f"{RISCV_TOOLCHAIN_PREFIX}-unknown-elf-{gnu_bin}"
    if RISCV_TOOLCHAIN_PATH and (the_path := Path(RISCV_TOOLCHAIN_PATH)).is_dir():
        p = the_path / p

    return str(p)


COMPILE_CMD = [
    rvbinpath("gcc"),
    "-march=rv32i",
    "-mabi=ilp32",
    "-T",
    "sdk/rv32i.ld",
    "-I",
    "sdk",
    "-nostartfiles",
]


def compile_sourcefile(build_dir: Path, testcase: str) -> Path:
    """Compile source file (.S or .c) to an executable object file"""

    in_path = get_rel_file(f"testcases/{testcase}")
    out_path = build_dir / in_path.with_suffix(".elf").name
    cmd = COMPILE_CMD + ["-o", str(out_path), str(in_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"sourcefile compilation failed:\n{result.stderr}\n{result.args}"
        )
    return out_path
