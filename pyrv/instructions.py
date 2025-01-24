"""
Contains object definitions for supported instructions and data frames,
as well as utilities for working with these.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, TypedDict, TypeVar, get_args

from pyrv.helpers import InvalidInstructionError, se
from pyrv.models import RegisterFile

if TYPE_CHECKING:
    from pyrv.harts import Hart


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


T = TypeVar("T", IType, RType, SType, BType, UType, JType)


class Instruction[T: Mapping](ABC):
    def __init__(self, frame: T):
        self._frame = frame

    @abstractmethod
    def exec(self, hart: "Hart"):
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

    @property
    def frame_type(self):
        """
        Extract the type of frame used (`IType`, `RType`, etc) from the Generics
        data of the parent
        """

        return get_args(type(self).__orig_bases__[0])[0]  # type: ignore

    def to_asm(self) -> str:
        instr_frame = self.frame_type
        instr = INSTR2OP[type(self)]
        asm = ""

        def a(i: int):
            return RegisterFile.REVALIASES[i]

        if instr_frame == IType:
            if instr.startswith("l"):  # cheeky hck load instructions which are IType
                asm = f"{instr} {a(self.rd)}, {self.imm}({a(self.rs1)})"
            else:
                asm = f"{instr} {a(self.rd)}, {a(self.rs1)}, {self.imm}"
        elif instr_frame == RType:
            asm = f"{instr} {a(self.rd)}, {a(self.rs1)}, {a(self.rs2)}"
        elif instr_frame == SType:
            asm = f"{instr} {a(self.rs1)}, {self.imm}({a(self.rs2)})"
        elif instr_frame in (UType, JType):
            asm = f"{instr} {a(self.rd)}, {self.imm}"
        elif instr_frame == BType:
            asm = f"{instr} {a(self.rs1)}, {a(self.rs2)}, {self.imm}"
        else:
            raise InvalidInstructionError

        return asm

    def __eq__(self, other):
        return self._frame == other._frame and self.frame_type == other.frame_type

    def __repr__(self) -> str:
        return self.to_asm()


# --- Control Flow instructions --- #


class JumpAndLink(Instruction[JType]):
    """
    Set the program counter to the address formed by adding the sign-extended
    20-bit immediate offset to this instruction's address.
    Store the address of the next instruction in rd.

    Note: the immediate encodes 2 bytes (half words)

    jal rd, imm
    """

    def exec(self, hart: "Hart"):
        hart.rf[self.rd] = hart.pc + 4
        hart.pc += self.imm


class JumpAndLinkRegister(Instruction[IType]):
    """
    Set the program counter to the address formed by adding the sign-extended
    12-bit immediate offset to rs1 and setting the LSB to 0.
    Store the address of the next instruction in rd.

    jalr rd, rs1, imm
    """

    def exec(self, hart: "Hart"):
        hart.rf[self.rd] = hart.pc + 4
        val = hart.rf[self.rs1] + self.imm
        hart.pc.write(val & 0xFFFF_FFFE)


class BranchEqual(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 equals rs2.

    Note: the immediate encodes 2 bytes (half words)

    beq rs1, rs2, imm
    """

    def exec(self, hart: "Hart"):
        if hart.rf[self.rs1] == hart.rf[self.rs2]:
            hart.pc += self.imm


class BranchNotEqual(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is not equal to
    rs2.

    Note: the immediate encodes 2 bytes (half words)

    bne rs1, rs2, imm
    """

    def exec(self, hart: "Hart"):
        if hart.rf[self.rs1] != hart.rf[self.rs2]:
            hart.pc += self.imm


class BranchOnLessThan(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is less than
    rs2 (signed).

    blt rs1, rs2, imm
    """

    def exec(self, hart: "Hart"):
        a = se(hart.rf[self.rs1].read())
        b = se(hart.rf[self.rs2].read())
        if a < b:
            hart.pc += self.imm


class BranchOnLessThanU(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is less than
    rs2.

    bltu rs1, rs2, imm
    """

    def exec(self, hart: "Hart"):
        if hart.rf[self.rs1] < hart.rf[self.rs2]:
            hart.pc += self.imm & 0xFFFF_FFFF


class BranchOnGreaterThanEqual(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is >=
    rs2 (signed).

    bge rs1, rs2, imm
    """

    def exec(self, hart: "Hart"):
        a = se(hart.rf[self.rs1].read())
        b = se(hart.rf[self.rs2].read())
        if a >= b:
            hart.pc += self.imm


class BranchOnGreaterThanEqualU(Instruction[BType]):
    """
    Add the sign-extended 12-bit immediate offset to the pc value if rs1 is >=
    rs2.

    bgeu rs1, rs2, imm
    """

    def exec(self, hart: "Hart"):
        if hart.rf[self.rs1] >= hart.rf[self.rs2]:
            hart.pc += self.imm & 0xFFFF_FFFF


# --- Load/Store instructions ---


class LoadWord(Instruction[IType]):
    """
    Set rd to the word retrieved from the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate

    lw rd, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        hart.rf[self.rd] = hart.system_bus.read(self.rs1 + self.imm, 4)


class LoadHalfwordU(Instruction[IType]):
    """
    Set rd to the zero-extended halfword retrieved from the system bus at the
    address obtained by adding rs1 to the sign-extended 12-bit immediate

    lhu rd, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        hart.rf[self.rd] = hart.system_bus.read(self.rs1 + self.imm, 2)


class LoadByteU(Instruction[IType]):
    """
    Set rd to the zero-extended byte retrieved from the system bus at the
    address obtained by adding rs1 to the sign-extended 12-bit immediate

    lbu rd, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        hart.rf[self.rd] = hart.system_bus.read(self.rs1 + self.imm, 1)


class LoadHalfword(Instruction[IType]):
    """
    Set rd to the sign-extended halfword retrieved from the system bus at the
    address obtained by adding rs1 to the sign-extended 12-bit immediate

    lh rd, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        hart.rf[self.rd] = se(hart.system_bus.read(self.rs1 + self.imm, 2), 16)


class LoadByte(Instruction[IType]):
    """
    Set rd to the sign-extended byte retrieved from the system bus at the
    address obtained by adding rs1 to the sign-extended 12-bit immediate

    lb rd, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        hart.rf[self.rd] = se(hart.system_bus.read(self.rs1 + self.imm, 1), 8)


class StoreWord(Instruction[SType]):
    """
    Write the word in rs2 to the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate.

    sw rs2, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        addr = self.rs1 + self.imm
        hart.system_bus.write(addr, self.rs2, 4)


class StoreHalfword(Instruction[SType]):
    """
    Write the lower 16 bits of rs2 to the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate.

    sh rs2, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        addr = self.rs1 + self.imm
        hart.system_bus.write(addr, self.rs2, 2)


class StoreByte(Instruction[SType]):
    """
    Write the lower 8 bits of rs2 to the system bus at the address obtained by
    adding rs1 to the sign-extended 12-bit immediate.

    sb rs2, imm(rs1)
    """

    def exec(self, hart: "Hart"):
        assert hart.system_bus is not None
        addr = self.rs1 + self.imm
        hart.system_bus.write(addr, self.rs2, 1)


# --- Integer-Register immediate operations ---


class AddImmediate(Instruction[IType]):
    """
    Add the source register to the sign-extended 12-bit immediate, placing the
    result in the destination register

    addi rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] + self.imm


class SetOnLessThanImmediate(Instruction[IType]):
    """
    Write 1 to the destination register if the signed source register is less than the
    sign-extended 12-bit immediate

    slti rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = int(se(hart.rf[self.rs1].read()) < self.imm)


class SetOnLessThanImmediateU(Instruction[IType]):
    """
    Write 1 to the destination register if the source register is less than the
    sign-extended 12-bit immediate

    sltiu rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = int(hart.rf[self.rs1] < (self.imm & 0xFFFF_FFFF))


class ExclusiveOrImmediate(Instruction[IType]):
    """
    Perform a bitwise XOR operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination register

    xori rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] ^ self.imm


class OrImmediate(Instruction[IType]):
    """
    Perform a bitwise OR operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination register

    ori rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] | self.imm


class AndImmediate(Instruction[IType]):
    """
    Perform a bitwise AND operation on the source register with the sign-extended
    12-bit immediate, placing the result in the destination register

    addi rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] & self.imm


class ShiftLeftLogicalImmediate(Instruction[IType]):
    """
    Shift the source register left by the lower 5 bits of the immediate,
    placing the result in the destination register

    slli rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] << self.imm


class ShiftRightLogicalImmediate(Instruction[IType]):
    """
    Shift the source register right by the lower 5 bits of the immediate,
    placing the result in the destination register

    srli rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] >> self.imm


class ShiftRightArithmeticImmediate(Instruction[IType]):
    """
    Shift the source register right by the lower 5 bits of the immediate, preserving the
    sign bit into fresh bits and placing the result in the destination register

    srai rd, rs1, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = se(hart.rf[self.rs1].read()) >> self.imm


class LoadUpperImmediate(Instruction[UType]):
    """
    Shift the sign-extended 20-bit immediate left by 20, storing the value in rd.

    lui rd, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = self.imm


class AddUpperImmediateToPc(Instruction[UType]):
    """
    Shift the sign-extended 20-bit immediate left by 20 and add to the pc,
    storing the value in rd.

    auipc rd, imm
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.pc + self.imm


# --- Integer Register-Register operations ----


class Add(Instruction[RType]):
    """
    Add two registers together, placing the result in a third register

    add rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] + hart.rf[self.rs2]


class Sub(Instruction[RType]):
    """
    Subtract the second register from the first, placing the result in a third register

    sub rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] - hart.rf[self.rs2]


class ShiftLeftLogical(Instruction[RType]):
    """
    Shift the first register left by the amount in the second
    register, placing the result in a third register

    sll rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] << hart.rf[self.rs2]


class SetOnLessThan(Instruction[RType]):
    """
    Write 1 to the destination register if the first register is less than the
    second

    slt rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = int(
            se(hart.rf[self.rs1].read()) < se(hart.rf[self.rs2].read())
        )


class SetOnLessThanU(Instruction[RType]):
    """
    Write 1 to the destination register if the first register is less than the
    second (unsigned)

    sltu rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = int(hart.rf[self.rs1] < hart.rf[self.rs2])


class ExclusiveOr(Instruction[RType]):
    """
    Perform a bitwise XOR operation on the first and second register, placing
    the result in the third register

    xor rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] ^ hart.rf[self.rs2]


class ShiftRightLogical(Instruction[RType]):
    """
    Shift the first register right by the amount in the second
    register, placing the result in a third register

    srl rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] >> hart.rf[self.rs2]


class ShiftRightArithmetic(Instruction[RType]):
    """
    Shift the first register right by the amount in the second
    register and preserve the sign bit, placing the result in a third register

    sra rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:  # cheeky, width of Python int >>>> 32
        hart.rf[self.rd] = se(hart.rf[self.rs1].read()) >> hart.rf[self.rs2].read()


class Or(Instruction[RType]):
    """
    Perform a bitwise OR operation on the first and second register, placing
    the result in the third register

    or rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] | hart.rf[self.rs2]


class And(Instruction[RType]):
    """
    Perform a bitwise AND operation on the first and second register, placing
    the result in the third register

    and rd, rs1, rs2
    """

    def exec(self, hart: "Hart") -> None:
        hart.rf[self.rd] = hart.rf[self.rs1] & hart.rf[self.rs2]


def bselect(bits: int, msb: int, lsb: int, shift: int = 0) -> int:
    """
    Return the int obtained by slicing `bits` from `msb` to `lsb`, optionally
    shifiting left by `shift`.
    """
    s = msb - lsb + 1
    mask = (1 << s) - 1
    return (mask & bits >> lsb) << shift


def decode_instr(instr: int) -> Instruction:
    op = bselect(instr, 6, 0)
    funct3 = bselect(instr, 14, 12)
    funct7 = bselect(instr, 31, 25)
    rd = bselect(instr, 11, 7)
    rs1 = bselect(instr, 19, 15)
    rs2 = bselect(instr, 24, 20)
    match op:
        case 0b0000011:  # loads
            imm = bselect(instr, 31, 20)
            frame = IType(rd=rd, rs1=rs1, imm=se(imm, 12))
            match funct3:
                case 0b000:
                    return LoadByte(frame)
                case 0b001:
                    return LoadHalfword(frame)
                case 0b010:
                    return LoadWord(frame)
                case 0b100:
                    return LoadByteU(frame)
                case 0b101:
                    return LoadHalfwordU(frame)
        case 0b0100011:  # stores:
            imm = bselect(instr, 31, 25, 5) | bselect(instr, 11, 7)
            frame = SType(rs1=rs1, rs2=rs2, imm=se(imm, 12))
            match funct3:
                case 0b000:
                    return StoreByte(frame)
                case 0b001:
                    return StoreHalfword(frame)
                case 0b010:
                    return StoreWord(frame)
        case 0b0010011:  # immediate arithmetic
            imm = bselect(instr, 31, 20)
            frame = IType(rd=rd, rs1=rs1, imm=se(imm, 12))
            match funct3, funct7:
                case 0b000, _:
                    return AddImmediate(frame)
                case 0b010, _:
                    return SetOnLessThanImmediate(frame)
                case 0b011, _:
                    return SetOnLessThanImmediateU(frame)
                case 0b100, _:
                    return ExclusiveOrImmediate(frame)
                case 0b110, _:
                    return OrImmediate(frame)
                case 0b111, _:
                    return AndImmediate(frame)
                case 0b001, _:
                    return ShiftLeftLogicalImmediate(frame)
                case 0b101, 0b0000000:
                    frame = IType(rd=rd, rs1=rs1, imm=bselect(instr, 24, 20))
                    return ShiftRightLogicalImmediate(frame)
                case 0b101, 0b0100000:
                    frame = IType(rd=rd, rs1=rs1, imm=bselect(instr, 24, 20))
                    return ShiftRightArithmeticImmediate(frame)
        case 0b0110011:  # register arithmetic
            frame = RType(rd=rd, rs1=rs1, rs2=rs2)
            match funct3, funct7:
                case 0b000, 0b0000000:
                    return Add(frame)
                case 0b000, 0b0100000:
                    return Sub(frame)
                case 0b001, _:
                    return ShiftLeftLogical(frame)
                case 0b010, _:
                    return SetOnLessThan(frame)
                case 0b011, _:
                    return SetOnLessThanU(frame)
                case 0b100, _:
                    return ExclusiveOr(frame)
                case 0b101, 0b0000000:
                    return ShiftRightLogical(frame)
                case 0b101, 0b0100000:
                    return ShiftRightArithmetic(frame)
                case 0b110, _:
                    return Or(frame)
                case 0b111, _:
                    return And(frame)
        case 0b1100011:  # branches
            imm = (
                bselect(instr, 31, 31, 12)
                | bselect(instr, 7, 7, 11)
                | bselect(instr, 30, 25, 5)
                | bselect(instr, 11, 8, 1)
            )
            frame = BType(rs1=rs1, rs2=rs2, imm=se(imm, 12 + 1))
            match funct3:
                case 0b000:
                    return BranchEqual(frame)
                case 0b001:
                    return BranchNotEqual(frame)
                case 0b100:
                    return BranchOnLessThan(frame)
                case 0b101:
                    return BranchOnGreaterThanEqual(frame)
                case 0b110:
                    return BranchOnLessThanU(frame)
                case 0b111:
                    return BranchOnGreaterThanEqualU(frame)
        case 0b1100111:  # jalr
            imm = bselect(instr, 31, 20)
            frame = IType(rd=rd, rs1=rs1, imm=se(imm, 12))
            return JumpAndLinkRegister(frame)
        case 0b1101111:  # jal
            imm = (
                bselect(instr, 31, 31, 20)
                | bselect(instr, 19, 12, 12)
                | bselect(instr, 20, 20, 11)
                | bselect(instr, 30, 21, 1)
            )
            frame = JType(rd=rd, imm=se(imm, 20 + 1))
            return JumpAndLink(frame)
        case 0b0110111:  # lui
            frame = UType(
                rd=rd,
                imm=bselect(instr, 31, 12, 12),
            )
            return LoadUpperImmediate(frame)
        case 0b0010111:  # auipc
            frame = UType(rd=rd, imm=bselect(instr, 31, 12, 12))
            return AddUpperImmediateToPc(frame)
        case 0b0001111:  # fence
            pass
        case 0b1110011:  # env
            pass
        case _:
            raise InvalidInstructionError

    return Add(RType(rd="x0", rs1="x0", rs2="x0"))  # nop


OP2INSTR = {
    "addi": AddImmediate,
    "slti": SetOnLessThanImmediate,
    "sltiu": SetOnLessThanImmediateU,
    "andi": AndImmediate,
    "ori": OrImmediate,
    "xori": ExclusiveOrImmediate,
    "slli": ShiftLeftLogicalImmediate,
    "srli": ShiftRightLogicalImmediate,
    "srai": ShiftRightArithmeticImmediate,
    "add": Add,
    "sub": Sub,
    "slt": SetOnLessThan,
    "sltu": SetOnLessThanU,
    "and": And,
    "or": Or,
    "xor": ExclusiveOr,
    "sll": ShiftLeftLogical,
    "srl": ShiftRightLogical,
    "sra": ShiftRightArithmetic,
    "auipc": AddUpperImmediateToPc,
    "lui": LoadUpperImmediate,
    "jal": JumpAndLink,
    "jalr": JumpAndLinkRegister,
    "lw": LoadWord,
    "lh": LoadHalfword,
    "lb": LoadByte,
    "lhu": LoadHalfwordU,
    "lbu": LoadByteU,
    "sw": StoreWord,
    "sh": StoreHalfword,
    "sb": StoreByte,
    "beq": BranchEqual,
    "bne": BranchNotEqual,
    "blt": BranchOnLessThan,
    "bltu": BranchOnLessThanU,
    "bge": BranchOnGreaterThanEqual,
    "bgeu": BranchOnGreaterThanEqualU,
}

INSTR2OP = {v: k for k, v in OP2INSTR.items()}

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
    "lbu",
    "lhu",
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
