from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TypedDict, TypeVar

from pyrv.helpers import Hart, se

T = TypeVar("T", bound=Mapping)


class IType(TypedDict):
    rd: int | str
    rs1: int | str
    imm: int


class RType(TypedDict):
    rd: int | str
    rs1: int | str
    rs2: int | str


class SType(TypedDict):
    rs1: int | str
    rs2: int | str
    imm: int


class BType(TypedDict):
    rs1: int | str
    rs2: int | str
    imm: int


class UType(TypedDict):
    rd: int | str
    imm: int


class JType(TypedDict):
    rd: int | str
    imm: int


class Instruction[T](ABC):
    def __init__(self, frame: T):
        self._frame = frame

    @abstractmethod
    def exec(self, hart: Hart):
        pass

    @property
    def rd(self):
        return self._frame["rd"]  # type: ignore

    @property
    def rs1(self):
        return self._frame["rs1"]  # type: ignore

    @property
    def rs2(self):
        return self._frame["rs2"]  # type: ignore

    @property
    def imm(self):
        return self._frame["imm"]  # type: ignore


# --- Control Flow instructions --- #


class JumpAndLink(Instruction[JType]):
    """
    Set the program counter to the address formed by adding the sign-extended
    20-bit immediate offset to this instruction's address.
    Store the address of the next instruction in rd.

    Note: the immediate encodes 2 bytes (half words)

    jal rd, imm
    """

    def exec(self, hart: Hart):
        hart.rf[self.rd] = hart.pc + 4
        hart.pc += se(self.imm << 1, 20 + 1)


class JumpAndLinkRegister(Instruction[IType]):
    """
    Set the program counter to the address formed by adding the sign-extended
    12-bit immediate offset to rs1 and setting the LSB to 0.
    Store the address of the next instruction in rd.

    jalr rd, rs1, imm
    """

    def exec(self, hart: Hart):
        hart.rf[self.rd] = hart.pc + 4
        val = hart.rf[self.rs1] + se(self.imm << 1, 12 + 1)
        hart.pc.write(val & 0xFFFF_FFFE)


class BranchEqual(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 equals rs2.

    Note: the immediate encodes 2 bytes (half words)

    beq rs1, rs2, imm
    """

    def exec(self, hart: Hart):
        if hart.rf[self.rs1] == hart.rf[self.rs2]:
            hart.pc += se(self.imm << 1, 12 + 1)


class BranchNotEqual(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is not equal to
    rs2.

    Note: the immediate encodes 2 bytes (half words)

    bne rs1, rs2, imm
    """

    def exec(self, hart: Hart):
        if hart.rf[self.rs1] != hart.rf[self.rs2]:
            hart.pc += se(self.imm << 1, 12 + 1)


class BranchOnLessThan(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is less than
    rs2 (signed).

    blt rs1, rs2, imm
    """

    def exec(self, hart: Hart):
        a = se(hart.rf[self.rs1].read())
        b = se(hart.rf[self.rs2].read())
        if a < b:
            hart.pc += se(self.imm << 1, 12 + 1)


class BranchOnLessThanU(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is less than
    rs2.

    bltu rs1, rs2, imm
    """

    def exec(self, hart: Hart):
        if hart.rf[self.rs1] < hart.rf[self.rs2]:
            hart.pc += se(self.imm << 1, 12 + 1)


class BranchOnGreaterThanEqual(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is >=
    rs2 (signed).

    bge rs1, rs2, imm
    """

    def exec(self, hart: Hart):
        a = se(hart.rf[self.rs1].read())
        b = se(hart.rf[self.rs2].read())
        if a >= b:
            hart.pc += se(self.imm << 1, 12 + 1)


class BranchOnGreaterThanEqualU(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is >=
    rs2.

    bgeu rs1, rs2, imm
    """

    def exec(self, hart: Hart):
        if hart.rf[self.rs1] >= hart.rf[self.rs2]:
            hart.pc += se(self.imm << 1, 12 + 1)


# --- Load/Store instructions ---


class LoadWord(Instruction[IType]):
    """
    Set rd to the word retrieved from the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate

    lw rd, imm(rs1)
    """

    def exec(self, hart: Hart):
        assert hart.system_bus is not None
        hart.rf[self.rd] = hart.system_bus.read(self.rs1 + se(self.imm, 12), 4)


class LoadHalfword(Instruction[IType]):
    """
    Set rd to the zero-extended halfword retrieved from the system bus at the
    address obtained by adding rs1 to the sign-extended 12-bit immediate

    lh rd, imm(rs1)
    """

    def exec(self, hart: Hart):
        assert hart.system_bus is not None
        hart.rf[self.rd] = hart.system_bus.read(self.rs1 + se(self.imm, 12), 2)


class LoadByte(Instruction[IType]):
    """
    Set rd to the zero-extended byte retrieved from the system bus at the
    address obtained by adding rs1 to the sign-extended 12-bit immediate

    lh rd, imm(rs1)
    """

    def exec(self, hart: Hart):
        assert hart.system_bus is not None
        hart.rf[self.rd] = hart.system_bus.read(self.rs1 + se(self.imm, 12), 1)


class StoreWord(Instruction[SType]):
    """
    Write the word in rs2 to the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate.

    sw rs2, imm(rs1)
    """

    def exec(self, hart: Hart):
        assert hart.system_bus is not None
        addr = self.rs1 + se(self.imm, 12)
        hart.system_bus.write(addr, self.rs2, 4)


class StoreHalfword(Instruction[SType]):
    """
    Write the lower 16 bits of rs2 to the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate.

    sh rs2, imm(rs1)
    """

    def exec(self, hart: Hart):
        assert hart.system_bus is not None
        addr = self.rs1 + se(self.imm, 12)
        hart.system_bus.write(addr, self.rs2, 2)


class StoreByte(Instruction[SType]):
    """
    Write the lower 8 bits of rs2 to the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate.

    sb rs2, imm(rs1)
    """

    def exec(self, hart: Hart):
        assert hart.system_bus is not None
        addr = self.rs1 + se(self.imm, 12)
        hart.system_bus.write(addr, self.rs2, 1)


# --- Integer-Register immediate operations ---


class AddImmediate(Instruction[IType]):
    """
    Add the source register to the sign-extended 12-bit immediate, placing the
    result in the destination register

    addi rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] + se(self.imm, 12)


class SetOnLessThanImmediate(Instruction[IType]):
    """
    Write 1 to the destination register if the signed source register is less than the
    sign-extended 12-bit immediate

    slti rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = int(se(hart.rf[self.rs1].read()) < se(self.imm, 12))


class SetOnLessThanImmediateU(Instruction[IType]):
    """
    Write 1 to the destination register if the source register is less than the
    sign-extended 12-bit immediate

    sltiu rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = int(hart.rf[self.rs1] < se(self.imm, 12))


class ExclusiveOrImmediate(Instruction[IType]):
    """
    Perform a bitwise XOR operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination register

    xori rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] ^ se(self.imm, 12)


class OrImmediate(Instruction[IType]):
    """
    Perform a bitwise OR operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination  register

    ori rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] | se(self.imm, 12)


class AndImmediate(Instruction[IType]):
    """
    Perform a bitwise AND operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination  register

    addi rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] & se(self.imm, 12)


class ShiftLeftLogicalImmediate(Instruction[IType]):
    """
    Shift the source register left by the lower 5 bits of the immediate,
    placing the result in destination register

    slli rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] << self.imm


class ShiftRightLogicalImmediate(Instruction[IType]):
    """
    Shift the source register right by the lower 5 bits of the immediate,
    placing the result in destination register

    srli rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] >> self.imm


class ShiftRightArithemeticImmediate(Instruction[IType]):
    """
    Shift the source register right by the lower 5 bits of the immediate, copying the
    sign bit into fresh bits and placing the result in destination register

    srai rd, rs1, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = se(hart.rf[self.rs1].read()) >> self.imm


class LoadUpperImmediate(Instruction[UType]):
    """
    Shift the sign-extended 20-bit immediate left by 20, storing the value in rd.

    lui rd, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = self.imm << 20


class AddUpperImmediateToPc(Instruction[UType]):
    """
    Shift the sign-extended 20-bit immediate left by 20 and add to the pc,
    storing the value in rd.

    auipc rd, imm
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.pc + self.imm << 20


# --- Integer Register-Register operations ----


class Add(Instruction[RType]):
    """
    Add two registers together, placing the result in a third register

    add rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] + hart.rf[self.rs2]


class Sub(Instruction[RType]):
    """
    Subtract the second register from the first, placing the result in a third register

    sub rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] - hart.rf[self.rs2]


class ShiftLeftLogical(Instruction[RType]):
    """
    Shift the first register left by the amount in the second
    register, placing the result in a third register

    sll rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] << hart.rf[self.rs2]


class SetOnLessThan(Instruction[RType]):
    """
    Write 1 to the destination register if the first register is less than the
    second

    slt rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = int(
            se(hart.rf[self.rs1].read()) < se(hart.rf[self.rs2].read())
        )


class SetOnLessThanU(Instruction[RType]):
    """
    Write 1 to the destination register if the first register is less than the
    second (unsigned)

    sltu rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = int(hart.rf[self.rs1] < hart.rf[self.rs2])


class ExclusiveOr(Instruction[RType]):
    """
    Perform a bitwise XOR operation on the first and second register, placing
    the result in the third register

    xor rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] ^ hart.rf[self.rs2]


class ShiftRightLogical(Instruction[RType]):
    """
    Shift the first register right by the amount in the second
    register, placing the result in a third register

    srl rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] >> hart.rf[self.rs2]


class ShiftRightArithemetic(Instruction[RType]):
    """
    Shift the first register right by the amount in the second
    register and preserve the sign bit, placing the result in a third register

    sra rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:  # cheeky, width of Python int >>>> 32
        hart.rf[self.rd] = se(hart.rf[self.rs1].read()) >> hart.rf[self.rs2].read()


class Or(Instruction[RType]):
    """
    Perform a bitwise OR operation on the first and second register, placing
    the result in the third register

    or rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] | hart.rf[self.rs2]


class And(Instruction[RType]):
    """
    Perform a bitwise AND operation on the first and second register, placing
    the result in the third register

    and rd, rs1, rs2
    """

    def exec(self, hart: Hart) -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] & hart.rf[self.rs2]


def bselect(bits: int, msb: int, lsb: int) -> int:
    """
    Return the int obtained by slicing `bits` from `msb` to `lsb`.
    """
    s = msb - lsb + 1
    mask = (1 << s) - 1
    return mask & (bits >> lsb)


def decode_instr(instr: int) -> Instruction:
    op = bselect(instr, 6, 0)
    funct3 = bselect(instr, 14, 12)
    funct7 = bselect(instr, 31, 25)
    match op:
        case 0b0000011:  # loads
            pass
        case 0b0100011:  # stores:
            pass
        case 0b0010011:  # immediate arithmetic
            pass
        case 0b0110011:  # register arithmetic
            pass
        case 0b1100011:  # branches
            pass
        case 0b1100111:  # jalr
            pass
        case 0b1101111:  # jal
            pass
        case 0b0110111:  # lui
            pass
        case 0b0010111:  # auipc
            pass
        case 0b0001111:  # fence
            pass
        case 0b1110011:  # env
            pass


OP2INSTR = {
    "addi": AddImmediate,
    "slti": SetOnLessThanImmediate,
    "sltiu": SetOnLessThanImmediateU,
    "andi": AndImmediate,
    "ori": OrImmediate,
    "xori": ExclusiveOrImmediate,
    "slli": ShiftLeftLogicalImmediate,
    "srli": ShiftRightLogicalImmediate,
    "srai": ShiftRightArithemeticImmediate,
    "add": Add,
    "sub": Sub,
    "slt": SetOnLessThan,
    "sltu": SetOnLessThanU,
    "and": And,
    "or": Or,
    "xor": ExclusiveOr,
    "sll": ShiftLeftLogical,
    "srl": ShiftRightLogical,
    "sra": ShiftRightArithemetic,
    "auipc": AddUpperImmediateToPc,
    "lui": LoadUpperImmediate,
    "jal": JumpAndLink,
    "jalr": JumpAndLinkRegister,
    "lw": LoadWord,
    "lh": LoadHalfword,
    "lb": LoadByte,
    "sw": StoreWord,
    "sh": StoreHalfword,
    "sb": StoreByte,
}

ITYPE_OPS = (
    "addi",
    "slti",
    "sltiu",
    "andi",
    "ori",
    "xori",
    "slli",
    "srli",
    "srai",
    "lw",
    "lh",
    "lb",
    "jalr",
)
RTYPE_OPS = (
    "add",
    "sub",
    "slt",
    "sltu",
    "and",
    "or",
    "xor",
    "sll",
    "srl",
    "sra",
)
UTYPE_OPS = ("lui", "auipc")
JTYPE_OPS = ("jal",)
STYPE_OPS = ("sw", "sh", "sb")
