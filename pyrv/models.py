import numpy

from pyrv.helpers import (
    AccessFaultException,
    AddressMisalignedException,
    MutableRegister,
    Register,
)
from pyrv.instructions import decode_instr


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


type Address = int | Register


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

    def write(self, addr: int, data: int, n: int):
        pass

    def read(self, addr: int, n: int) -> int:
        """Read `n` bytes from the system bus"""
        port = self.addr2port(addr)
        self._check_addr(addr, n)
        return port.read(addr, n)

    def addr2port(self, addr: int):
        """
        Map an address to a memory-mapped device port.

        This is in effect the bus fabric.
        """

        if 0 <= addr < 0x0010_0000:
            return self._hart.instruction_memory
        elif 0x0010_0000 <= addr < 0x0050_0000:
            return self._hart.data_memory
        elif 0xFFFF_FFEF <= addr < 0xFFFF_FFFF:
            return self._hart.sim_control
        else:
            raise AccessFaultException


class InstructionMemory:
    def __init__(self):
        self.SIZE = 1 * 1024
        """The size of the memory in kiB"""
        self._contents = numpy.zeros(self.SIZE * 1024, numpy.uint8)

    def _check_addr(self, addr: int, n: int) -> None:
        if addr > self._contents.size:
            raise AccessFaultException

    def read(self, addr: int) -> tuple:
        """Read `n` words from the memory starting at address `addr`"""
        self._check_addr(addr, 4)
        return self._contents[addr : addr + 4]


class DataMemory:
    def __init__(self):
        self.SIZE = 4 * 1024
        """The size of the memory in kiB"""
        self._contents = numpy.zeros(self.SIZE * 1024, numpy.uint8)

    def _check_addr(self, addr: int, n: int) -> None:
        if addr > self._contents.size:
            raise AccessFaultException

    def write(self, addr: int, data: int, n: int) -> None:
        """Write `n` bytes of `data` to the memory starting at address `addr`"""
        self._check_addr(addr, n)
        self._contents[addr : addr + n] = data

    def read(self, addr: int, n: int) -> tuple:
        """Read `n` bytes from the memory starting at address `addr`"""
        self._check_addr(addr, n)
        return self._contents[addr : addr + n]


class SimControl:
    """Controls interaction with the simulator, like stopping the simulation"""

    def __init__(self) -> None:
        pass

    def read(self, addr: int, n: int):
        pass

    def write(self, addr: int, data: int, n: int):
        pass


class Hart:
    """Barebones hart used for tests where a full hart is deliberately omitted"""

    def __init__(self) -> None:
        self.pc: MutableRegister = MutableRegister()
        self.register_file: RegisterFile = RegisterFile()
        self.data_memory: DataMemory | None = None
        self.instruction_memory: InstructionMemory | None = None
        self.system_bus: SystemBus | None = None
        self.sim_control: SimControl | None = None

        self.rf = self.register_file  # alias


class BasicHart(Hart):
    def __init__(self):
        super().__init__()
        # this should really be inside a SoC object
        self.system_bus = SystemBus(self)

        # memories
        self.data_memory = DataMemory()
        self.instruction_memory = InstructionMemory()

        # peripherals
        self.sim_control = SimControl()

    def step(self):
        """Step the simulator forward by one iteration"""
        assert self.system_bus is not None
        # fetch
        instr_word = self.system_bus.read(self.pc.read(), 4)
        # decode
        instr = decode_instr(instr_word)
        # execute
        instr.exec(self)
