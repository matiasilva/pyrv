import logging
from pathlib import Path

from elftools.elf.constants import P_FLAGS
from elftools.elf.elffile import ELFFile

from pyrv.adapters import check_elf
from pyrv.helpers import MutableRegister
from pyrv.instructions import decode_instr
from pyrv.models import (
    DataMemory,
    InstructionMemory,
    RegisterFile,
    SimControl,
    SystemBus,
)


class Hart:
    """
    A hart containing the minimum necessary components for code execution.
    """

    INSTRUCTION_MEMORY_BASE = 0x0
    INSTRUCTION_MEMORY_SIZE = 2 * 1024 * 1024
    DATA_MEMORY_BASE = INSTRUCTION_MEMORY_BASE + INSTRUCTION_MEMORY_SIZE
    DATA_MEMORY_SIZE = 6 * 1024 * 1024

    def __init__(self):
        self.pc: MutableRegister = MutableRegister()
        self.register_file: RegisterFile = RegisterFile()
        self.rf = self.register_file  # alias

        # memories
        self.data_memory = DataMemory(self.DATA_MEMORY_SIZE)
        self.instruction_memory = InstructionMemory(self.INSTRUCTION_MEMORY_SIZE)

        self.system_bus = SystemBus(self)
        self.system_bus.add_slave_port(
            "instruction memory",
            self.INSTRUCTION_MEMORY_BASE,
            self.INSTRUCTION_MEMORY_SIZE,
            self.instruction_memory,
        )
        self.system_bus.add_slave_port(
            "data memory",
            self.DATA_MEMORY_BASE,
            self.DATA_MEMORY_SIZE,
            self.data_memory,
        )

        # peripherals
        self.sim_control = SimControl()

        self._log = logging.getLogger(__name__)

    def step(self):
        """Step the simulator forward by one iteration"""
        assert self.system_bus is not None
        # fetch
        instr_word = self.read(self.pc.read(), 4)
        self._log.debug(f"Fetching instruction: {self.pc=}")
        # decode
        instr = decode_instr(instr_word)
        self._log.debug(f"Decoded instruction: {instr=}")
        # execute
        instr.exec(self)

    def load(self, elf_path: Path | str):
        """
        Load an ELF file directly into instruction and data memory, via the simulator

        This does not emulate the traditional word-by-word writing
        of bytes to memory over QSPI -> AHB -> memory, and instead
        sets the internal memory array immediately.
        """
        elf_path = Path(elf_path)
        if not elf_path.is_file():
            raise FileNotFoundError

        with open(elf_path, "rb") as f:
            elf_file = ELFFile(f)
            check_elf(elf_file)
            for seg in elf_file.iter_segments("PT_LOAD"):
                if seg["p_flags"] & P_FLAGS.PF_X:
                    self.instruction_memory._write_bytes(0, seg.data())
                else:
                    self.data_memory._write_bytes(0, seg.data())

    def read(self, addr: int, n_bytes: int) -> int:
        return self.system_bus.read(addr, n_bytes)

    def write(self, addr: int, data: int, n_bytes: int):
        self.system_bus.write(addr, data, n_bytes)
