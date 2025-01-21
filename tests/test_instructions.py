import pytest

from pyrv.helpers import HartState, Register
from pyrv.instructions import ITYPE_OPS, OP2INSTR, RTYPE_OPS, Instruction, IType, RType
from tests.testcases.itype import ITYPE_TESTCASES, TestCaseIType
from tests.testcases.rtype import RTYPE_TESTCASES, TestCaseRType

WIDTH = Register.WIDTH


@pytest.fixture
def hs():
    return HartState()


def test_register_bank_aliases(hs: HartState):
    assert hs.rf.x0 == 0
    assert hs.rf["x0"] == 0
    assert hs.rf.zero == 0
    assert hs.rf["zero"] == 0

    hs.rf.t0 += 0xF
    assert hs.rf["t0"] == 0xF
    assert hs.rf[5] == 0xF


@pytest.mark.parametrize(
    "instr,tc", [(OP2INSTR[op], tc) for op in ITYPE_OPS for tc in ITYPE_TESTCASES[op]]
)
def test_itype(instr: type[Instruction[IType]], tc: TestCaseIType, hs: HartState):
    # setup
    hs.rf[tc.frame["rs1"]] = tc.initial_rs1
    # execute
    instr(tc.frame).exec(hs)
    # verify
    assert hs.rf[tc.frame["rd"]] == tc.expected_rd


@pytest.mark.parametrize(
    "instr,tc", [(OP2INSTR[op], tc) for op in RTYPE_OPS for tc in RTYPE_TESTCASES[op]]
)
def test_rtype(instr: type[Instruction[RType]], tc: TestCaseRType, hs: HartState):
    # setup
    hs.rf[tc.frame["rs1"]] = tc.initial_rs1
    hs.rf[tc.frame["rs2"]] = tc.initial_rs2
    # execute
    instr(tc.frame).exec(hs)
    # verify
    assert hs.rf[tc.frame["rd"]] == tc.expected_rd
