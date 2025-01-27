"""
Contains models of different hardware blocks, including the Hart.
"""

from typing import TYPE_CHECKING

import numpy
import numpy.typing as npt

from pyrv.helpers import (
    AccessFaultException,
    AddressMisalignedException,
    MutableRegister,
    Register,
)

if TYPE_CHECKING:
    from pyrv.harts import Hart


class RegisterFile:
    ALIASES = {
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
    REVALIASES = {v: k for k, v in ALIASES.items()}
    ALIASES |= {f"x{i}": i for i in range(32)}  # add x0, x1, ... aliases

    def __init__(self) -> None:
        self._items: tuple = (Register(),) + tuple(MutableRegister() for _ in range(31))

    def __getitem__(self, key: int | str) -> Register:
        match key:
            case int():
                idx = key
            case str():
                idx = self.ALIASES[key]
        return self._items[idx]

    def __setitem__(self, key: int | str, value: int | Register) -> None:
        r = self[key]
        i_val = value if isinstance(value, int) else value.read()
        r.write(i_val)

    def __len__(self) -> int:
        return len(self._items)

    def __getattr__(self, attr: str) -> Register:
        return self[attr]


class Peripheral:
    pass


class Memory(Peripheral):
    """Generic Memory class, implementing a few basic methods"""

    def __init__(self, size: int, width: int = 1):
        """
        Initializes the Memory class with size and width args.

        Args:
            size: the size of the memory in KiB
            width: the width of the memory in multiples of bytes
        """
        self._size = size
        """The size of the memory in KiB"""

        match width:
            case 4:
                dtype = numpy.uint32
            case 1:
                dtype = numpy.uint8
            case _:
                raise ValueError("Unsupported memory size")
        self._contents: npt.NDArray = numpy.zeros(self._size * 1024, dtype)
        """Internal container for our memory"""

    def _read(self, addr: int, n: int) -> npt.NDArray:
        """Read `n` bytes from the memory, starting at address `addr`"""
        return self._contents[addr : addr + n]

    def _write_bytes(self, addr: int, data: bytes) -> None:
        """Write `data` bytes to memory, starting at address `addr`"""
        self._contents[addr : addr + len(data)] = memoryview(data)

    def _write(self, addr: int, data: int, n: int) -> None:
        """Write `n` bytes from `data` into memory, starting at address `addr`"""
        self._write_bytes(addr, data.to_bytes(n, byteorder="little"))

    # AHB-like intf
    def read_byte(self, addr: int):
        return self._read(addr, 1)

    def read_halfword(self, addr: int):
        return self._read(addr, 2)

    def read_word(self, addr: int):
        return self._read(addr, 4)

    def read_burst(self, addr: int, burst_size: int, beat_count: int):
        return self._read(addr, burst_size * beat_count)

    def write_byte(self, addr: int, data: int):
        return self._write(addr, data, 1)

    def write_halfword(self, addr: int, data: int):
        return self._write(addr, data, 2)

    def write_word(self, addr: int, data: int):
        return self._write(addr, data, 4)


class InstructionMemory(Memory):
    def __init__(self):
        super().__init__(2 * 1024, 4)


class DataMemory(Memory):
    def __init__(self):
        super().__init__(6 * 1024, 4)


class SimControl(Peripheral):
    """Controls interaction with the simulator, like stopping the simulation"""

    def __init__(self) -> None:
        pass

    def read(self, addr: int, n: int):
        pass

    def write(self, addr: int, data: int, n: int):
        pass


class AddressRange:
    def __init__(self, start: int, size: int):
        self.start = start
        self.end = start + size - 1
        self.size = size

    def contains(self, addr: int, n_bytes: int = 1) -> bool:
        """Check if an address + n_bytes falls within this AddressRange"""
        access_end = addr + n_bytes - 1
        return self.start <= addr and access_end <= self.end

    def overlaps(self, other: "AddressRange") -> bool:
        """Check if this range overlaps with another range"""
        return not (self.end < other.start or other.end < self.start)


class SystemBus:
    """
    Dispatches load/store instructions

    A load/store instruction moves data to/from registers and
    ports (memory + peripherals) on the system address map
    """

    def __init__(self, hart: "Hart"):
        self._hart = hart

    def _check_addr(self, addr: int, n: int):
        if (n & (n - 1) != 0) or n == 0:
            raise AddressMisalignedException
        if addr % n != 0:
            raise AddressMisalignedException
        # check addr beyond range
        if addr > self._contents.size:
            raise AccessFaultException

    def write(self, addr: int, data: int, n: int):
        pass

    def read(self, addr: int, n: int) -> int:
        """Read `n` bytes from the system bus"""
        port = self.get_port(addr, n)
        self._check_addr(addr, n)
        return port.read(addr, n)

    def addr2port(self, addr: int) -> InstructionMemory | DataMemory | SimControl:
        """
        Map an address to a memory-mapped device port.

        This is in effect the bus fabric.
        """

        if 0 <= addr < 0x0200_0000:
            return self._hart.instruction_memory
        elif 0x0200_0000 <= addr < 0x0800_0000:
            return self._hart.data_memory
        elif 0xFFFF_FFEF <= addr < 0xFFFF_FFFF:
            return self._hart.sim_control
        else:
            raise AccessFaultException

    def add_peripheral(self, name: str, start_addr: int, size: int, peripheral=None):
        """
        Add a peripheral to the address map.
        Args:
            name: Identifier for the peripheral
            start_addr: Base address
            size: Size in bytes
            peripheral: Optional reference to peripheral object
        """
        new_range = AddressRange(start_addr, size)

        # Check for overlaps with existing peripherals
        for existing_name, (existing_range, _) in self.peripherals.items():
            if new_range.overlaps(existing_range):
                raise ValueError(
                    f"Address range 0x{start_addr:x}-0x{start_addr + size - 1:x} "
                    f"overlaps with existing peripheral {existing_name}"
                )

        self.peripherals[name] = (new_range, peripheral)

    def check_access(self, addr: int, n_bytes: int) -> Peripheral:
        """
        Check if an access to address + n_bytes is valid.

        Validity checks:
            - n_bytes must be a power of 2
            - alignment of `addr` on an `n_bytes` boundary
            - addr + n_bytes is contained in the address map

        Returns:
            A valid peripheral if an address is valid, else None
        """
        for name, (addr_range, peripheral) in self.peripherals.items():
            if addr_range.contains(addr, n_bytes):
                return True, name, peripheral

        return False, None, None

    def get_peripheral(self, addr: int, n_bytes: int = 1) -> Peripheral:
        """
        Get the peripheral at address `addr` in the system address map.

        The access occurs at address `addr` and has an extent of `n_bytes`. If this
        access is invalid, then no peripheral is returned.

        Returns:
            A peripheral object if the access is valid, else None
        """
        peripheral = self.check_access(addr, n_bytes)
        if not peripheral:
            raise AccessFaultException(f"No peripheral at address 0x{addr:x}")
        return peripheral
