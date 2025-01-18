import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TypedDict, TypeVar

from helpers import MutableRegister, RegisterBank, se

x = RegisterBank()
pc = MutableRegister()

T = TypeVar("T", bound=Mapping)


class IType(TypedDict):
    rd: int | str
    rs1: int | str
    imm: int


class RType(TypedDict):
    rd: int | str
    rs1: int | str
    rs2: int | str


class Instruction[T](ABC):
    def __init__(self, frame: T):
        self._frame = frame

    @abstractmethod
    def exec(self, rb: RegisterBank):
        pass

    @property
    def rd(self):
        return self._frame["rd"]

    @property
    def rs1(self):
        return self._frame["rs1"]

    @property
    def rs2(self):
        return self._frame["rs2"]

    @property
    def imm(self):
        return self._frame["imm"]


class AddImmediate(Instruction[IType]):
    def exec(self, rb: RegisterBank):
        rb[self.rd] = se(self.imm, 12) + rb[self.rs1]


class InvalidInstructionError(Exception):
    pass


OP_RE = re.compile(r"^\s*(\w+)(.*)$")


def asm2instr(asm: tuple) -> Instruction:
    op, args = asm
    match op:
        case "lui" | "addi" | "slti" | "sltiu" | "andi" | "ori" | "xori":
            return ITypeInstruction.from_asm(op, args)
        case _:
            raise InvalidInstructionError


def main() -> int:
    asm_instrs = []
    with open("tests/add.s") as file:
        for line in file:
            if m := OP_RE.match(line):
                op = m.group(1)
                args = m.group(2)
                if (i := args.find("#")) > -1:
                    args = args[:i]
                args = [a.strip() for a in args.split(",")]
                asm_instrs.append((op, args))

    instrs = map(asm2instr, asm_instrs)
    for instr in instrs:
        print("")
    return 0


if __name__ == "__main__":
    main()
