from dataclasses import dataclass

from pyrv.helpers import Register
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
    "add": [],
    "sub": [],
    "slt": [],
    "sltu": [],
    "and": [],
    "or": [],
    "xor": [],
    "sll": [],
    "srl": [],
    "sra": [],
}
