"""
Contains different adapters for supported input formats. Adapters are utilities that
parse input data and output pyrv instruction objects
"""

import re

from pyrv.helpers import InvalidInstructionError
from pyrv.instructions import ITYPE_OPS, OP2INSTR, RTYPE_OPS, Instruction, IType, RType

OP_RE = re.compile(r"^\s*(\w+)(.*)$")


def asm2instr(asm: tuple) -> Instruction:
    op, args = asm

    if op in ITYPE_OPS:
        frame = IType(rd=args[0], rs1=args[1], imm=args[2])
    elif op in RTYPE_OPS:
        frame = RType(rd=args[0], rs1=args[1], rs2=args[2])
    else:
        raise InvalidInstructionError

    return OP2INSTR[op](frame)


def parse_asm(line: str) -> tuple | None:
    if m := OP_RE.match(line):
        op = m.group(1)
        args = m.group(2)
        if (i := args.find("#")) > -1:
            args = args[:i]
        args = [a.strip() for a in args.split(",")]
        return (op, args)
    else:
        return None
