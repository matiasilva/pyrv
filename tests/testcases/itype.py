from dataclasses import dataclass

from pyrv.instructions import IType

IMM_MASK = (1 << 12) - 1


@dataclass
class TestCaseIType:
    name: str
    frame: IType
    initial_rs1: int
    expected_rd: int
    __test__ = False


# TODO: add edge cases
ITYPE_TESTCASES = {
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
            initial_rs1=-48,
            expected_rd=1,
        ),
        TestCaseIType(
            "slti_true_np",
            {"rd": 1, "rs1": 2, "imm": 28},
            initial_rs1=-48,
            expected_rd=1,
        ),
        TestCaseIType(
            "slti_false_pn",
            {"rd": 1, "rs1": 2, "imm": (-48 & IMM_MASK)},
            initial_rs1=28,
            expected_rd=0,
        ),
        TestCaseIType(
            "slti_false_nn",
            {"rd": 1, "rs1": 2, "imm": (-8 & IMM_MASK)},
            initial_rs1=-2,
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
            initial_rs1=-8,
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
            "sltiu_seqz", {"rd": 1, "rs1": 0, "imm": 1}, initial_rs1=0, expected_rd=1
        ),
    ],
    "andi": [
        TestCaseIType(
            "andi_basic",
            {"rd": 1, "rs1": 2, "imm": 0b101},
            initial_rs1=0b111,
            expected_rd=0b101,
        ),
        TestCaseIType(
            "andi_zero", {"rd": 1, "rs1": 2, "imm": 0}, initial_rs1=0b111, expected_rd=0
        ),
        TestCaseIType(
            "andi_all_ones",
            {"rd": 1, "rs1": 2, "imm": 0b111},
            initial_rs1=0b101,
            expected_rd=0b101,
        ),
    ],
    "ori": [
        TestCaseIType(
            "ori_basic",
            {"rd": 1, "rs1": 2, "imm": 0b101},
            initial_rs1=0b110,
            expected_rd=0b111,
        ),
        TestCaseIType(
            "ori_zero",
            {"rd": 1, "rs1": 2, "imm": 0},
            initial_rs1=0b110,
            expected_rd=0b110,
        ),
        TestCaseIType(
            "ori_all_ones",
            {"rd": 1, "rs1": 2, "imm": 0b111},
            initial_rs1=0,
            expected_rd=0b111,
        ),
    ],
    "xori": [
        TestCaseIType(
            "xori_basic",
            {"rd": 1, "rs1": 2, "imm": 0b101},
            initial_rs1=0b110,
            expected_rd=0b011,
        ),
        TestCaseIType(
            "xori_zero",
            {"rd": 1, "rs1": 2, "imm": 0},
            initial_rs1=0b110,
            expected_rd=0b110,
        ),
        TestCaseIType(
            "xori_not",
            {"rd": 1, "rs1": 2, "imm": (-1 & IMM_MASK)},
            initial_rs1=0xFF00_FF00,
            expected_rd=0x00FF_00FF,
        ),
    ],
    "slli": [
        TestCaseIType(
            "slli_basic",
            {"rd": 1, "rs1": 2, "imm": 2},
            initial_rs1=0b0001,
            expected_rd=0b0100,
        ),
        TestCaseIType(
            "slli_zero",
            {"rd": 1, "rs1": 2, "imm": 0},
            initial_rs1=0b0001,
            expected_rd=0b0001,
        ),
        TestCaseIType(
            "slli_max",
            {"rd": 1, "rs1": 2, "imm": 31},
            initial_rs1=1,
            expected_rd=0x80000000,
        ),
    ],
    "srli": [
        TestCaseIType(
            "srli_basic",
            {"rd": 1, "rs1": 2, "imm": 2},
            initial_rs1=0b1100,
            expected_rd=0b0011,
        ),
        TestCaseIType(
            "srli_zero",
            {"rd": 1, "rs1": 2, "imm": 0},
            initial_rs1=0b1100,
            expected_rd=0b1100,
        ),
        TestCaseIType(
            "srli_ones",
            {"rd": 1, "rs1": 2, "imm": 1},
            initial_rs1=0xFFFFFFFF,
            expected_rd=0x7FFFFFFF,
        ),
    ],
    "srai": [
        TestCaseIType(
            "srai_basic",
            {"rd": 1, "rs1": 2, "imm": 2},
            initial_rs1=0b1100,
            expected_rd=0b0011,
        ),
        TestCaseIType(
            "srai_negative",
            {"rd": 1, "rs1": 2, "imm": 1},
            initial_rs1=0x80000000,
            expected_rd=0xC0000000,
        ),
        TestCaseIType(
            "srai_negative2",
            {"rd": 1, "rs1": 2, "imm": 4},
            initial_rs1=0xF0000000,
            expected_rd=0xFF000000,
        ),
    ],
    "lw": [],
    "lh": [],
    "lb": [],
    "lbu": [],
    "lhu": [],
    "jalr": [],
}
