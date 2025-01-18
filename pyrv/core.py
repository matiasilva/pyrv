from abc import ABC, abstractmethod
import re

from helpers import MutableRegister, RegisterBank

x = RegisterBank()
pc = MutableRegister()


class Instruction(ABC):
    @abstractmethod
    def exec(self, rb: RegisterBank):
        pass


class RTypeInstruction(Instruction):
    def __init__(self, rs1, rs2, rd):
        self._rs1 = rs1
        self._rs2 = rs2
        self._rd = rd

    @classmethod
    def from_asm(cls, op: str, args: str):
        return cls


class ITypeInstruction(Instruction):
    def __init__(self, rs1, rd, imm):
        self._rs1 = rs1
        self._rd = rd
        self._imm = imm

    @staticmethod
    def from_asm(op: str, args: str):
        args_list = [a.strip() for a in args.split(",")]
        print(args_list)
        return 0


OP_RE = re.compile(r"^\s*(\w+)(.*)$")


def main() -> int:
    instrs = []
    with open("tests/add.s") as file:
        for line in file:
            if m := OP_RE.match(line):
                op = m.group(1)
                args = m.group(2)
                if (i := args.find("#")) > -1:
                    args = args[:i]
                args = args.strip()
                instrs.append((op, args))

    def to_instr(instr):
        op, args = instr
        match op:
            case "li" | "lui" | "addi" | "slti" | "sltiu" | "andi" | "ori" | "xori":
                return ITypeInstruction.from_asm(op, args)
            case _:
                return "not defined"

    instrs = list(map(to_instr, instrs))
    print(instrs)
    return 0


if __name__ == "__main__":
    main()
