from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TypedDict, TypeVar

from pyrv.helpers import RegisterBank, as_signed, se

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
    """
    Add the source register to the sign-extended 12-bit immediate, placing the
    result in the destination register

    addi rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] + se(self.imm, 12)


class SetOnLessThanImmediate(Instruction[IType]):
    """
    Write 1 to the destination register if the signed source register is less than the
    sign-extended 12-bit immediate

    slti rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = int(as_signed(rb[self.rs1].read()) < as_signed(se(self.imm, 12)))


class SetOnLessThanImmediateU(Instruction[IType]):
    """
    Write 1 to the destination register if the source register is less than the
    sign-extended 12-bit immediate

    sltiu rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = int(rb[self.rs1] < se(self.imm, 12))


class ExclusiveOrImmediate(Instruction[IType]):
    """
    Perform a bitwise XOR operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination register

    xori rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] ^ se(self.imm, 12)


class OrImmediate(Instruction[IType]):
    """
    Perform a bitwise OR operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination  register

    ori rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] | se(self.imm, 12)


class AndImmediate(Instruction[IType]):
    """
    Perform a bitwise AND operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination  register

    addi rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] & se(self.imm, 12)


class ShiftLeftLogicalImmediate(Instruction[IType]):
    """
    Shift the source register left by the lower 5 bits of the immediate,
    placing the result in destination register

    slli rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] << self.imm


class ShiftRightLogicalImmediate(Instruction[IType]):
    """
    Shift the source register right by the lower 5 bits of the immediate,
    placing the result in destination register

    srli rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] >> self.imm


class ShiftRightArithemeticImmediate(Instruction[IType]):
    """
    Shift the source register right by the lower 5 bits of the immediate, copying the
    sign bit into fresh bits and placing the result in destination register

    srai rd, rs1, imm
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = se(rb[self.rs1].read(), 32) >> self.imm


class Add(Instruction[RType]):
    """
    Add two registers together, placing the result in a third register

    add rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] + rb[self.rs2]


class Sub(Instruction[RType]):
    """
    Subtract the second register from the first, placing the result in a third register

    sub rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] - rb[self.rs2]


class ShiftLeftLogical(Instruction[RType]):
    """
    Shift the first register left by the amount in the second
    register, placing the result in a third register

    sll rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] << rb[self.rs2]


class SetOnLessThan(Instruction[RType]):
    """
    Write 1 to the destination register if the first register is less than the
    second

    slt rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = int(as_signed(self.rs1) < as_signed(self.rs2))


class SetOnLessThanU(Instruction[RType]):
    """
    Write 1 to the destination register if the first register is less than the
    second (unsigned)

    sltu rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = int(self.rs1 < self.rs2)


class ExclusiveOr(Instruction[RType]):
    """
    Perform a bitwise XOR operation on the first and second register, placing
    the result in the third register

    xor rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] ^ rb[self.rs2]


class ShiftRightLogical(Instruction[RType]):
    """
    Shift the first register right by the amount in the second
    register, placing the result in a third register

    srl rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] >> rb[self.rs2]


class ShiftRightArithemetic(Instruction[RType]):
    """
    Shift the first register right by the amount in the second
    register and preserve the sign bit, placing the result in a third register

    sra rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:  # cheeky, width of Python int >>>> 32
        rb[self.rd] = se(rb[self.rs1].read(), 32) >> rb[self.rs2].read()


class Or(Instruction[RType]):
    """
    Perform a bitwise OR operation on the first and second register, placing
    the result in the third register

    or rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] | rb[self.rs2]


class And(Instruction[RType]):
    """
    Perform a bitwise AND operation on the first and second register, placing
    the result in the third register

    and rd, rs1, rs2
    """

    def exec(self, rb: RegisterBank) -> None:
        rb[self.rd] = rb[self.rs1] & rb[self.rs2]


OP2INSTR = {
    "addi": AddImmediate,
    "slti": SetOnLessThanImmediate,
    "sltiu": SetOnLessThanImmediateU,
    "andi": AndImmediate,
    "ori": OrImmediate,
    "xori": ExclusiveOrImmediate,
}

ITYPE_OPS = ("addi", "slti", "sltiu", "andi", "ori", "xori")
