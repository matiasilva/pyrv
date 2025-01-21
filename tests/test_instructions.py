import pytest

from pyrv.helpers import Hart, Register
from pyrv.instructions import ITYPE_OPS, OP2INSTR, RTYPE_OPS, Instruction, IType, RType
from tests.testcases.itype import ITYPE_TESTCASES, TestCaseIType
from tests.testcases.rtype import RTYPE_TESTCASES, TestCaseRType

WIDTH = Register.WIDTH


@pytest.fixture
def hart():
    return Hart()


def test_register_bank_aliases(hart: Hart):
    assert hart.rf.x0 == 0
    assert hart.rf["x0"] == 0
    assert hart.rf.zero == 0
    assert hart.rf["zero"] == 0

    hart.rf.t0 += 0xF
    assert hart.rf["t0"] == 0xF
    assert hart.rf[5] == 0xF


@pytest.mark.parametrize(
    "instr,tc", [(OP2INSTR[op], tc) for op in ITYPE_OPS for tc in ITYPE_TESTCASES[op]]
)
def test_itype(instr: type[Instruction[IType]], tc: TestCaseIType, hart: Hart):
    # setup
    hart.rf[tc.frame["rs1"]] = tc.initial_rs1
    # execute
    instr(tc.frame).exec(hart)
    # verify
    assert hart.rf[tc.frame["rd"]] == tc.expected_rd


@pytest.mark.parametrize(
    "instr,tc", [(OP2INSTR[op], tc) for op in RTYPE_OPS for tc in RTYPE_TESTCASES[op]]
)
def test_rtype(instr: type[Instruction[RType]], tc: TestCaseRType, hart: Hart):
    # setup
    hart.rf[tc.frame["rs1"]] = tc.initial_rs1
    hart.rf[tc.frame["rs2"]] = tc.initial_rs2
    # execute
    instr(tc.frame).exec(hart)
    # verify
    assert hart.rf[tc.frame["rd"]] == tc.expected_rd
