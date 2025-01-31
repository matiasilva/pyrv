"""
Contains models of different hardware blocks, including the Hart.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, NamedTuple

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


class Addressable(ABC):
    @abstractmethod
    def read(self, addr: int, n_bytes: int) -> int:
        """
        Read a `n_bytes` at address `addr` from the peripheral.

        If the peripheral is a memory, accesses of narrower width than the memory's
        contents return unknown data.
        """
        ...

    @abstractmethod
    def write(self, addr: int, data: int, n_bytes: int) -> None:
        """
        Write `n_bytes` of `data` to address `addr` in the peripheral.

        If the peripheral is a memory, writes of narrower width than the memory's
        contents will write to invalid locations.
        """
        ...

    def read_byte(self, addr: int) -> int:
        return self.read(addr, 1)

    def read_halfword(self, addr: int) -> int:
        return self.read(addr, 2)

    def read_word(self, addr: int) -> int:
        return self.read(addr, 4)

    def write_byte(self, addr: int, data: int) -> None:
        return self.write(addr, data, 1)

    def write_halfword(self, addr: int, data: int) -> None:
        return self.write(addr, data, 2)

    def write_word(self, addr: int, data: int) -> None:
        return self.write(addr, data, 4)

    # def read_burst(self, addr: int, burst_size: int, beat_count: int):
    #     return self._read(addr, burst_size * beat_count)


class Peripheral(Addressable):
    pass


class Memory(Peripheral):
    """Generic Memory class, implementing a few basic methods"""

    width2dtype = {1: numpy.uint8, 2: numpy.uint16, 4: numpy.uint32}

    def __init__(self, size: int, width: int = 1):
        """
        Initializes the Memory class with size and width args.

        Args:
            size: the size of the memory in KiB
            width: the width of the memory in multiples of bytes
        """
        self._size = size
        """The size of the memory in KiB"""

        self._contents: npt.NDArray = numpy.zeros(
            self._size * 1024, self.width2dtype[width]
        )
        """Internal container for our memory"""

    def _read(self, addr: int, n: int) -> npt.NDArray:
        """Read `n` bytes from the memory, starting at address `addr`"""
        return self._contents[addr : addr + n]

    def _write_bytes(self, addr: int, data: bytes) -> None:
        """Write `data` bytes to memory, starting at address `addr`"""
        self._contents[addr : addr + len(data)] = memoryview(data)

    def read(self, addr, n_bytes) -> int:
        return self._read(addr, n_bytes).astype(self.width2dtype[n_bytes]).item(0)

    def write(self, addr, data, n_bytes):
        self._write_bytes(addr, data.to_bytes(n_bytes, byteorder="little"))


class InstructionMemory(Memory):
    def __init__(self):
        super().__init__(2 * 1024, 4)


class DataMemory(Memory):
    def __init__(self):
        super().__init__(6 * 1024)


class UnallocatedAddressException(Exception):
    pass


class TriggerKey(NamedTuple):
    addr: int
    test_func: Callable[[int, int], bool]


class MemoryMappedPeripheral(Peripheral):
    """
    Generic class for a peripheral with registers with side effects when accessed.

    An incoming byte address is mapped to a word address, which is then used to look up
    the index of the register value. The index is a location in the `_register_values`
    array. There is a memory usage penalty to pay for the O(1) lookup complexity. But
    as Amdahl's law says: make the common case fast! Register lookups are far more
    common than allocation.
    """

    def __init__(self) -> None:
        self._word_size = 8
        self._byte_size = self._word_size << 2
        assert self._word_size < 256  # only 255 values allowed, 0 reserved
        self._register_values = numpy.zeros(self._word_size, dtype=numpy.uint32)
        self._register_lookup = numpy.zeros(self._word_size, dtype=numpy.uint8)
        """0 is a sentinel value, offset all indices by 1 and decode accordingly"""
        self._triggers: dict[TriggerKey, Callable] = {}
        """Indexes triggers using a tuple of address and test function"""

        self.set_register(0x0, 0x0)

    def get_register(self, addr: int) -> int | None:
        """Return the index matching this address if the register exists, else None"""
        idx = self._register_lookup[addr >> 2]
        return None if idx == 0 else idx

    def alloc_register(self, addr: int) -> int:
        """
        Find the next available location in the register values map and assign the
        address `addr` to this location in the register lookup table.
        """
        next_idx = self._register_lookup.max() + 1
        self._register_lookup[addr >> 2] = next_idx
        return next_idx

    def set_register(self, addr: int, val: int) -> None:
        """
        Set register at address `addr` to `val`, allocating one in the address
        space if it does not exist.
        """
        idx = self.get_register(addr)
        idx = self.alloc_register(addr) if idx is None else idx
        self._register_values[idx] = val

    def read(self, addr: int, n_bytes: int) -> int:
        key = self.get_register(addr)
        if key is None:
            raise UnallocatedAddressException
        value = self._register_values.item(key - 1)
        match n_bytes:
            case 1:
                shift = (addr & 3) << 3
                return value >> shift & 0xFF
            case 2:
                shift = (addr & 2) << 2
                return value >> shift & 0xFFFF
            case _:
                return value

    def write(self, addr: int, data: int, n_bytes: int):
        """
        Write `n_bytes` of `data` to the correct byte lanes. Data is taken
        from the lower bits.

        Example: a byte write of data takes the lowest 8 bits and writes them
        to the byte lane implied by the address.
        """
        idx = self.get_register(addr)
        if idx is None:
            raise UnallocatedAddressException
        old_value = self._register_values.item(idx)

        mask = 1 << (n_bytes * 8) - 1
        lane = addr & 0xFF
        value = (data & mask) << lane
        mask <<= addr & lane  # move mask to correct byte lane
        # clear and set new value
        self._register_values[idx] = old_value & ~mask | value

        for (trigger_addr, test_func), callback in self._triggers.items():
            if trigger_addr == addr and test_func(value, old_value):
                callback(value, old_value)

    def add_trigger(
        self,
        addr: int,
        test_func: Callable[[int, int], bool],
        callback: Callable[[int, int], None],
    ):
        """
        Attach a callback function to a register that is called when a triggering
        condition is met.

        Some triggering conditions that could be used:
            - `lambda new, old: new & BIT_MASK` to see if a bit is set
            - `lambda new, old: (new & BIT_MASK) and not (old & BIT_MASK)` transition
            - `lambda new, old: new == TARGET_VALUE`
            - `lambda new, old: MIN_VALUE <= new <= MAX_VALUE` for a value in a range
            - `lambda new, old: new != old`
            - `lambda new, old: True` always trigger

        Args:
            addr: byte address of register to watch, this is internally decoded
            to the correct register index in the lookup table
            test_func: a function that takes two args, `new` and `old`, and compares
            them
            callback: a function to call when trigger condition is met
        """
        self._triggers[TriggerKey(addr, test_func)] = callback


class SimControl(MemoryMappedPeripheral):
    """
    Controls interaction with the simulator, like stopping the simulation.
    """

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


class ValidAccess(NamedTuple):
    peripheral: Peripheral
    offset: int


class SystemBus(Addressable):
    """
    Dispatches load/store instructions

    A load/store instruction moves data to/from registers and
    ports (memory + peripherals) on the system address map
    """

    def __init__(self, hart: "Hart"):
        self._hart = hart
        self._slave_ports: dict[str, tuple[AddressRange, Peripheral]] = {}

    def read(self, addr, n_bytes):
        peripheral, offset = self.get_access(addr, n_bytes)
        return peripheral.read(offset, n_bytes)

    def write(self, addr, data, n_bytes):
        peripheral, offset = self.get_access(addr, n_bytes)
        return peripheral.write(offset, data, n_bytes)

    def add_slave_port(
        self, name: str, start_addr: int, size: int, peripheral: Peripheral
    ):
        """
        Add a slave port to the address map.

        A slave port links together the notion of an address range and a peripheral.
        A peripheral implements read/write methods while an address range designates a
        region of the system address space to this peripheral.

        Args:
            name: Identifier for the peripheral, purely informative
            start_addr: Base address
            size: Size in bytes
            peripheral: Reference to peripheral object
        """
        new_range = AddressRange(start_addr, size)

        # check for overlaps with existing peripherals
        for existing_name, (existing_range, _) in self._slave_ports.items():
            if new_range.overlaps(existing_range):
                raise ValueError(
                    f"Address range 0x{start_addr:x}-0x{start_addr + size - 1:x} "
                    f"overlaps with existing peripheral {existing_name}"
                )

        self._slave_ports[name] = (new_range, peripheral)

    def check_access(self, addr: int, n_bytes: int) -> ValidAccess | None:
        """
        Check if an access to address + n_bytes is valid.

        Validity checks:
            - n_bytes must be a power of 2
            - n_bytes must be <= 4
            - alignment of `addr` on an `n_bytes` boundary
            - addr maps onto a valid peripheral in the system address map
            - addr + n_bytes is within a peripheral's address range

        Returns:
            A `ValidAccess` if the access is valid, else None
        """
        if (n_bytes & (n_bytes - 1) != 0) or n_bytes == 0:
            raise AddressMisalignedException
        if n_bytes > 4:
            raise AddressMisalignedException
        if addr % n_bytes != 0:
            raise AddressMisalignedException
        for _, (addr_range, peripheral) in self._slave_ports.items():
            if addr_range.contains(addr, n_bytes):
                return ValidAccess(peripheral, addr - addr_range.start)

    def get_access(self, addr: int, n_bytes: int = 1) -> ValidAccess:
        """
        Get a `ValidAccess` tuple containing the peripheral and start offset
        for this access.

        The access occurs at address `addr` and has an extent of `n_bytes`. If this
        access is invalid, then no peripheral is returned.
        """
        valid_access = self.check_access(addr, n_bytes)
        if not valid_access:
            raise AccessFaultException(
                f"No peripheral for access of {n_bytes} at address 0x{addr:x}"
            )
        return valid_access
