"""
Contains different adapters for supported input formats. Adapters are utilities that
parse input data and output pyrv instruction objects
"""

import logging
import re

import elftools.elf.descriptions as elf_desc
from elftools.elf.elffile import ELFFile

from pyrv.helpers import InvalidInstructionError, UnsupportedExecutableError
from pyrv.instructions import (
    BTYPE_OPS,
    ITYPE_OPS,
    JTYPE_OPS,
    OP2INSTR,
    RTYPE_OPS,
    STYPE_OPS,
    UTYPE_OPS,
    BType,
    Instruction,
    IType,
    JType,
    RType,
    SType,
    UType,
)

OP_RE = re.compile(r"^\s*(\w+)(.*)$")
logger = logging.getLogger(__name__)


def asm2instr(asm: tuple) -> Instruction:
    """
    Convert a string representation of an instruction to a `pyrv` Instruction model.

    This is valid for debug only, compliance with how the assembler compiles
    assembly files is not guaranteed.
    """
    op, args = asm

    if op in ITYPE_OPS:
        frame = IType(rd=args[0], rs1=args[1], imm=args[2])
    elif op in RTYPE_OPS:
        frame = RType(rd=args[0], rs1=args[1], rs2=args[2])
    elif op in BTYPE_OPS:
        frame = BType(rs1=args[0], rs2=args[1], imm=args[2])
    elif op in JTYPE_OPS:
        frame = JType(rd=args[0], imm=args[1])
    elif op in STYPE_OPS:
        frame = SType(rs1=args[0], rs2=args[1], imm=args[2])
    elif op in UTYPE_OPS:
        frame = UType(rd=args[0], imm=args[1])
    else:
        raise InvalidInstructionError

    return OP2INSTR[op](frame)


def parse_asm(line: str) -> tuple | None:
    """
    Parse an assembly file for instructions, returning the operation and any arguments.

    This is valid for debug only, there is no advanced calculation of label offsets, no
    notion of linker relaxations, and so on.
    """
    if m := OP_RE.match(line):
        op = m.group(1)
        args = m.group(2)
        if (i := args.find("#")) > -1:  # strip comments
            args = args[:i]
        args = [a.strip() for a in args.split(",")]
        return (op, args)


def check_elf(elf_file: ELFFile):
    """
    Validate basic parameters of an ELF file, ensuring safe subsequent usage
    """

    endianness = elf_desc.describe_ei_data(elf_file["e_ident"]["EI_DATA"])
    logger.info(f"Found ELF file: {elf_file.get_machine_arch()}, {endianness}")

    conds = (
        elf_file["e_machine"] != "EM_RISCV",
        elf_file.elfclass != 32,
        not elf_file.little_endian,
        elf_file["e_type"] != "ET_EXEC",
    )
    if any(conds):
        raise UnsupportedExecutableError
