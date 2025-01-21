from dataclasses import dataclass

from pyrv.instructions import RType


@dataclass
class TestCaseRType:
    name: str
    frame: RType
    initial_rs1: int
    initial_rs2: int
    expected_rd: int
    __test__ = False


RTYPE_TESTCASES = {
    "add": [
        TestCaseRType(
            name="add_positive",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=5,
            initial_rs2=7,
            expected_rd=12,
        ),
        TestCaseRType(
            name="add_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-5,
            initial_rs2=-7,
            expected_rd=-12,
        ),
        TestCaseRType(
            name="add_overflow",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0xFFFFFFFF,
            initial_rs2=1,
            expected_rd=-0x0000_0000,
        ),
    ],
    "sub": [
        TestCaseRType(
            name="sub_positive",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=10,
            initial_rs2=7,
            expected_rd=3,
        ),
        TestCaseRType(
            name="sub_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-5,
            initial_rs2=7,
            expected_rd=-12,
        ),
        TestCaseRType(
            name="sub_underflow",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-0x00000000,
            initial_rs2=1,
            expected_rd=0xFFFFFFFF,
        ),
    ],
    "slt": [
        TestCaseRType(
            name="slt_true",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-5,
            initial_rs2=7,
            expected_rd=1,
        ),
        TestCaseRType(
            name="slt_false",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=10,
            initial_rs2=7,
            expected_rd=0,
        ),
        TestCaseRType(
            name="slt_equal",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=7,
            initial_rs2=7,
            expected_rd=0,
        ),
    ],
    "sltu": [
        TestCaseRType(
            name="sltu_true",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=5,
            initial_rs2=7,
            expected_rd=1,
        ),
        TestCaseRType(
            name="sltu_false_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-1,
            initial_rs2=1,
            expected_rd=0,
        ),
        TestCaseRType(
            name="sltu_equal",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=7,
            initial_rs2=7,
            expected_rd=0,
        ),
    ],
    "and": [
        TestCaseRType(
            name="and_basic",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0b1100,
            initial_rs2=0b1010,
            expected_rd=0b1000,
        ),
        TestCaseRType(
            name="and_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-1,  # All 1s
            initial_rs2=0x0F,
            expected_rd=0x0F,
        ),
        TestCaseRType(
            name="and_zero",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0xFFFFFFFF,
            initial_rs2=0,
            expected_rd=0,
        ),
    ],
    "or": [
        TestCaseRType(
            name="or_basic",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0b1100,
            initial_rs2=0b1010,
            expected_rd=0b1110,
        ),
        TestCaseRType(
            name="or_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-1,  # All 1s
            initial_rs2=0x0F,
            expected_rd=-1,  # Still all 1s
        ),
        TestCaseRType(
            name="or_zero",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0,
            initial_rs2=0,
            expected_rd=0,
        ),
    ],
    "xor": [
        TestCaseRType(
            name="xor_basic",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0b1100,
            initial_rs2=0b1010,
            expected_rd=0b0110,
        ),
        TestCaseRType(
            name="xor_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-1,  # All 1s
            initial_rs2=-1,  # All 1s
            expected_rd=0,  # XOR with same value gives 0
        ),
        TestCaseRType(
            name="xor_zero",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0x12345678,
            initial_rs2=0,
            expected_rd=0x12345678,
        ),
    ],
    "sll": [
        TestCaseRType(
            name="sll_basic",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0b1,
            initial_rs2=4,
            expected_rd=0b10000,
        ),
        TestCaseRType(
            name="sll_zero_shift",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0x12345678,
            initial_rs2=0,
            expected_rd=0x12345678,
        ),
        TestCaseRType(
            name="sll_large_shift",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=1,
            initial_rs2=31,
            expected_rd=0x80000000,
        ),
    ],
    "srl": [
        TestCaseRType(
            name="srl_basic",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0b10000,
            initial_rs2=4,
            expected_rd=0b1,
        ),
        TestCaseRType(
            name="srl_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-1,  # all 1s
            initial_rs2=4,
            expected_rd=0x0FFFFFFF,
        ),
        TestCaseRType(
            name="srl_zero_shift",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0x12345678,
            initial_rs2=0,
            expected_rd=0x12345678,
        ),
    ],
    "sra": [
        TestCaseRType(
            name="sra_basic_positive",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0b10000,
            initial_rs2=4,
            expected_rd=0b1,
        ),
        TestCaseRType(
            name="sra_negative",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=-1024,  # negative number
            initial_rs2=4,
            expected_rd=-64,  # sign extended
        ),
        TestCaseRType(
            name="sra_zero_shift",
            frame={"rd": "x1", "rs1": "x2", "rs2": "x3"},
            initial_rs1=0x12345678,
            initial_rs2=0,
            expected_rd=0x12345678,
        ),
    ],
}
