"""Adapters are utilities that parse input data and output pyrv instruction
representations"""

import re

import pyrv.instructions as instructions
from pyrv.instructions import ITYPE_OPS, OP2INSTR, RTYPE_OPS, Instruction


class InvalidInstructionError(Exception):
    pass


OP_RE = re.compile(r"^\s*(\w+)(.*)$")


def asm2instr(asm: tuple) -> Instruction:
    op, args = asm

    if op in ITYPE_OPS:
        frame = instructions.IType(rd=args[0], rs1=args[1], imm=args[2])
    elif op in RTYPE_OPS:
        frame = instructions.RType(rd=args[0], rs1=args[1], rs2=args[2])
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
