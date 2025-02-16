"""
Contains common utilities and basic object definitions.
"""

from typing import Self


class Register:
    WIDTH = 32
    MASK = (1 << WIDTH) - 1

    def __init__(self, value: int = 0) -> None:
        self._value = value

    def _masked(self, value: int) -> int:
        return value & self.MASK

    def _int_or_reg(self, value: Self | int) -> int:
        o_val = value if isinstance(value, int) else value.read()
        return self._masked(o_val)

    def read(self) -> int:
        return self._value

    def write(self, value: int) -> None:
        # RISC-V allows writes so long as they don't take effect
        value = value  # do something silly like this so PyRight is happy

    # use a decorator here?
    def __add__(self, other: Self | int) -> int:
        return self._masked(self.read() + self._int_or_reg(other))

    def __sub__(self, other: Self | int) -> int:
        return self._masked(self.read() - self._int_or_reg(other))

    def __lshift__(self, other: Self | int) -> int:
        return self._masked(self.read() << self._int_or_reg(other))

    def __rshift__(self, other: Self | int) -> int:
        return self._masked(self.read() >> self._int_or_reg(other))

    def __xor__(self, other: Self | int) -> int:
        return self.read() ^ self._int_or_reg(other)

    def __and__(self, other: Self | int) -> int:
        return self.read() & self._int_or_reg(other)

    def __or__(self, other: Self | int) -> int:
        return self.read() | self._int_or_reg(other)

    def __gt__(self, other: Self | int) -> bool:
        return self.read() > self._int_or_reg(other)

    def __ge__(self, other: Self | int) -> bool:
        return self.read() >= self._int_or_reg(other)

    def __lt__(self, other: Self | int) -> bool:
        return self.read() < self._int_or_reg(other)

    def __eq__(self, other) -> bool:
        return self.read() == self._int_or_reg(other)

    def __ne__(self, other) -> bool:
        return self.read() != self._int_or_reg(other)

    def __iadd__(self, other: Self | int) -> Self:
        self.write(self + other)
        return self

    def __isub__(self, other: Self | int) -> Self:
        self.write(self - other)
        return self

    def __repr__(self) -> str:
        return f"{self.read():#0x}"


class MutableRegister(Register):
    def __init__(self, value: int = 0) -> None:
        super().__init__(value)

    def _masked(self, value: int) -> int:
        return value & self.MASK

    def write(self, value: int) -> None:
        self._value = self._masked(value)


def se(value: int, bits: int = 32) -> int:
    """
    Sign extend a binary integer of size `bits`

    Reference: Henry S. Warren, Jr., Hacker's Delight (2e), Ch. 2, Addison-Wesley, 2012
    """
    sign_bit = 1 << bits - 1
    return (value ^ sign_bit) - sign_bit


def bselect(bits: int, msb: int, lsb: int, shift: int = 0) -> int:
    """
    Return the int obtained by slicing `bits` from `msb` to `lsb`, optionally
    shifiting left by `shift`.
    """
    s = msb - lsb + 1
    mask = (1 << s) - 1
    return (mask & bits >> lsb) << shift


def bmask(n: int) -> int:
    """Given number of bytes `n`, return a mask for those bytes."""
    return (1 << (n * 8)) - 1


class AddressMisalignedException(Exception):
    pass


class AccessFaultException(Exception):
    pass


class InvalidInstructionError(Exception):
    pass


class UnsupportedExecutableError(Exception):
    pass
