from dataclasses import dataclass

import pytest

import pyrv.helpers
from pyrv import instructions
from pyrv.helpers import MutableRegister, Register, RegisterBank
from pyrv.instructions import ITYPE_OPS, OP2INSTR, IType, Instruction, RType

WIDTH = Register.WIDTH
IMM_MASK = (1 << 12) - 1
REG_MASK = Register.MASK


@pytest.fixture
def rb():
    return RegisterBank()


def test_register_bank_aliases(rb):
    assert rb.x0 == 0
    assert rb["x0"] == 0
    assert rb.zero == 0
    assert rb["zero"] == 0

    rb.t0 += 0xF
    assert rb["t0"] == 0xF
    assert rb[5] == 0xF


# @pytest.mark.parametrize("rd,rs1,imm", [()])
def test_itype(rb):
    rd = "t0"
    rs1 = "t1"
    imm = 9
    frame: IType = {"rd": rd, "rs1": rs1, "imm": imm}
    instr = instructions.AddImmediate(frame)
    instr.exec(rb)
    assert rb[rd] == imm


# test pseudoinstructions
#


@dataclass
class TestCaseIType:
    name: str
    frame: IType
    initial_rs1: int
    expected_rd: int

    __test__ = False


testcases = {
    "addi": [
        TestCaseIType(
            "addi_pos",
            {"rd": 1, "rs1": 2, "imm": 5},
            initial_rs1=10,
            expected_rd=15,
        ),
        TestCaseIType(
            "addi_neg",
            {"rd": 1, "rs1": 2, "imm": (-5 & IMM_MASK)},
            initial_rs1=10,
            expected_rd=5,
        ),
        TestCaseIType(
            "addi_zero", {"rd": 1, "rs1": 2, "imm": 0}, initial_rs1=10, expected_rd=10
        ),
        TestCaseIType(
            "addi_overflow",
            {"rd": 1, "rs1": 2, "imm": 1},
            initial_rs1=0xFFFF_FFFF,
            expected_rd=0,
        ),
        TestCaseIType(
            "addi_to_x0", {"rd": 0, "rs1": 2, "imm": 5}, initial_rs1=10, expected_rd=0
        ),
    ],
    "slti": [
        TestCaseIType(
            "slti_true_nn",
            {"rd": 1, "rs1": 2, "imm": (-8 & IMM_MASK)},
            initial_rs1=(-48 & REG_MASK),
            expected_rd=1,
        ),
        TestCaseIType(
            "slti_false_nn",
            {"rd": 1, "rs1": 2, "imm": (-8 & IMM_MASK)},
            initial_rs1=(-2 & REG_MASK),
            expected_rd=0,
        ),
        TestCaseIType(
            "slti_false", {"rd": 1, "rs1": 2, "imm": 10}, initial_rs1=12, expected_rd=0
        ),
        TestCaseIType(
            "slti_equal_p", {"rd": 1, "rs1": 2, "imm": 5}, initial_rs1=5, expected_rd=0
        ),
        TestCaseIType(
            "slti_equal_n",
            {"rd": 1, "rs1": 2, "imm": (-8 & IMM_MASK)},
            initial_rs1=(-8 & REG_MASK),
            expected_rd=0,
        ),
    ],
    "sltiu": [
        TestCaseIType(
            "sltiu_true", {"rd": 1, "rs1": 2, "imm": 4}, initial_rs1=5, expected_rd=0
        ),
        TestCaseIType(
            "sltiu_false", {"rd": 1, "rs1": 2, "imm": 12}, initial_rs1=10, expected_rd=1
        ),
        TestCaseIType(
            "sltiu_equal", {"rd": 1, "rs1": 2, "imm": 5}, initial_rs1=5, expected_rd=0
        ),
        TestCaseIType(
            "sltiu_snez", {"rd": 1, "rs1": 0, "imm": 0}, initial_rs1=1, expected_rd=0
        ),
    ],
    "andi": [],
    "ori": [],
    "xori": [],
}


# def generate_parameters():
#     params = []
#     for op in ITYPE_OPS:
#         instr = OP2INSTR[op]
#         params += [(instr, tc) for tc in testcases[op]]


@pytest.mark.parametrize(
    "instr,tc", [(OP2INSTR[op], tc) for op in ITYPE_OPS for tc in testcases[op]]
)
def test_addi(instr: type[Instruction[IType]], tc: TestCaseIType, rb):
    # setup
    rb[tc.frame["rs1"]] = tc.initial_rs1
    # execute
    instr(tc.frame).exec(rb)
    # verify
    assert rb[tc.frame["rd"]] == tc.expected_rd
