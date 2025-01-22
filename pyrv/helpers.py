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


# TODO: consider subclassing Sequence, Mapping (tried but was a mypy PITA)
class RegisterFile:
    def __init__(self) -> None:
        self._items: tuple = (Register(),) + tuple(MutableRegister() for _ in range(31))

        self._aliases = {
            "zero": 0,
            "ra": 1,
            "sp": 2,
            "gp": 3,
            "tp": 4,
            "t0": 5,
            "t1": 6,
            "t2": 7,
            "fp": 8,
            "s0": 8,
            "s1": 9,
            "a0": 10,
            "a1": 11,
            "a2": 12,
            "a3": 13,
            "a4": 14,
            "a5": 15,
            "a6": 16,
            "a7": 17,
            "s2": 18,
            "s3": 19,
            "s4": 20,
            "s5": 21,
            "s6": 22,
            "s7": 23,
            "s8": 24,
            "s9": 25,
            "s10": 26,
            "s11": 27,
            "t3": 28,
            "t4": 29,
            "t5": 30,
            "t6": 31,
        }
        self._aliases |= {f"x{i}": i for i in range(32)}  # add x0, x1, ... aliases

    def __getitem__(self, key: int | str) -> Register:
        match key:
            case int():
                idx = key
            case str():
                idx = self._aliases[key]
            case _:
                raise KeyError(f"Alias {key} not bound")
        return self._items[idx]

    def __setitem__(self, key: int | str, value: int | Register) -> None:
        r = self[key]
        i_val = value if isinstance(value, int) else value.read()
        r.write(i_val)

    def __len__(self) -> int:
        return len(self._items)

    def __getattr__(self, attr: str) -> Register:
        return self[attr]


def se(value: int, bits: int = 32) -> int:
    """
    Sign extend a binary integer of size `bits`

    Reference: Henry S. Warren, Jr., Hacker's Delight (2e), Ch. 2, Addison-Wesley, 2012
    """
    sign_bit = 1 << bits - 1
    return (value ^ sign_bit) - sign_bit


class AddressMisalignedException(Exception):
    pass


class AccessFaultException(Exception):
    pass


class InvalidInstructionError(Exception):
    pass
