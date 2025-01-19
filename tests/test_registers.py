import pytest

import pyrv.helpers
from pyrv.helpers import MutableRegister, Register

WIDTH = Register.WIDTH


@pytest.fixture
def reg():
    return MutableRegister(0x12345678)


@pytest.fixture
def max_reg():
    return MutableRegister((1 << WIDTH) - 1)


def test_basic():
    reg = Register()
    assert reg.read() == 0

    reg = Register(42)
    assert reg.read() == 42


def test_immutable_register():
    r = Register(3)
    r.write(3)
    assert r.read() == 3


def test_mutable_register(reg):
    reg.write(3)
    assert reg.read() == 3


def test_masked_register(max_reg):
    assert max_reg.read() == (1 << WIDTH) - 1
    max_reg += 1
    assert max_reg.read() == 0

    max_reg.write(0xF_FFFF_FFF)
    assert max_reg.read() == 0xFFFF_FFFF

    assert MutableRegister(0) - 1 == 0xFFFFFFFF


@pytest.mark.parametrize(
    "value, bits, expected",
    [
        # 32 bits
        (0x0, 32, 0),  # Zero remains zero
        (0x1, 32, 1),  # Small positive value
        (0x7FFFFFFF, 32, 2147483647),  # Maximum positive value
        (0x80000000, 32, -2147483648),  # Minimum negative value
        (0xFFFFFFFF, 32, -1),  # All bits set for 32 bits
        # 16 bits
        (0x0, 16, 0),  # Zero remains zero
        (0x1, 16, 1),  # Small positive value
        (0x7FFF, 16, 32767),  # Maximum positive value
        (0x8000, 16, -32768),  # Minimum negative value
        (0xFFFF, 16, -1),  # All bits set for 16 bits
        # 8 bits
        (0x0, 8, 0),  # Zero remains zero
        (0x1, 8, 1),  # Small positive value
        (0x7F, 8, 127),  # Maximum positive value
        (0x80, 8, -128),  # Minimum negative value
        (0xFF, 8, -1),  # All bits set for 8 bits
    ],
)
def test_as_signed(value: int, bits: int, expected: int):
    assert pyrv.helpers.as_signed(value, bits) == expected


def test_arithmetic_operations(reg: MutableRegister):
    """Test sub and add with both ints and `MutableRegister`s"""

    assert reg + 1 == 0x12345679
    assert reg + MutableRegister(1) == 0x12345679

    assert reg - 0x1234 == 0x12344444
    assert reg - MutableRegister(0x1234) == 0x12344444


def test_bitwise_operations(reg: Register):
    assert (reg & 0xFFFF) == 0x5678
    assert (reg & Register(0xFFFF)) == 0x5678

    assert (reg | 0xFF000000) == 0xFF345678
    assert (reg | Register(0xFF000000)) == 0xFF345678

    assert (reg ^ 0xFFFFFFFF) == 0xEDCBA987
    assert (reg ^ Register(0xFFFFFFFF)) == 0xEDCBA987


def test_shift_operations(reg: Register):
    assert (reg << 4) == 0x23456780
    assert (reg << Register(4)) == 0x23456780

    assert (reg >> 4) == 0x01234567
    assert (reg >> Register(4)) == 0x01234567

    # shift by full width
    assert (reg << WIDTH) == 0
    assert (reg >> WIDTH) == 0


def test_comparison_operations(reg: Register):
    assert (reg > 0x12345677) == 1
    assert (reg > 0x12345679) == 0
    assert (reg > Register(0x12345677)) == 1

    assert (reg < 0x12345679) == 1
    assert (reg < 0x12345677) == 0
    assert (reg < Register(0x12345679)) == 1


def test_edge_cases(max_reg):
    # test operations with maximum values
    print(max_reg + 1)
    assert max_reg + 1 == 0
    assert max_reg - 0xFFFFFFFF == 0
    assert max_reg & 0 == 0
    assert max_reg | 0 == 0xFFFFFFFF
    assert max_reg ^ 0xFFFFFFFF == 0

    # test operations with zero
    zero_reg = Register(0)
    assert zero_reg - 1 == 0xFFFFFFFF
    assert zero_reg << 1 == 0
    assert zero_reg >> 1 == 0


def test_invalid_types(reg):
    invalid_values = ["string", None, 3.14, [], {}]
    for invalid_value in invalid_values:
        with pytest.raises((TypeError, AttributeError)):
            reg + invalid_value  # type: ignore
        with pytest.raises((TypeError, AttributeError)):
            reg - invalid_value  # type: ignore
        with pytest.raises((TypeError, AttributeError)):
            reg & invalid_value  # type: ignore
        with pytest.raises((TypeError, AttributeError)):
            reg | invalid_value  # type: ignore
        with pytest.raises((TypeError, AttributeError)):
            reg ^ invalid_value  # type: ignore
        with pytest.raises((TypeError, AttributeError)):
            reg << invalid_value  # type: ignore
        with pytest.raises((TypeError, AttributeError)):
            reg >> invalid_value  # type: ignore
