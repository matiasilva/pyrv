import pytest

from pyrv.helpers import Register, RegisterBank
from pyrv.instructions import ITYPE_OPS, OP2INSTR, Instruction, IType, RType
from tests.testcases.itype import ITYPE_TESTCASES, TestCaseIType

WIDTH = Register.WIDTH
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


@pytest.mark.parametrize(
    "instr,tc", [(OP2INSTR[op], tc) for op in ITYPE_OPS for tc in ITYPE_TESTCASES[op]]
)
def test_itype(instr: type[Instruction[IType]], tc: TestCaseIType, rb):
    # setup
    rb[tc.frame["rs1"]] = tc.initial_rs1
    # execute
    instr(tc.frame).exec(rb)
    # verify
    assert rb[tc.frame["rd"]] == tc.expected_rd
