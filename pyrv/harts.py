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

    def __init__(self):
        self.pc: MutableRegister = MutableRegister()
        self.register_file: RegisterFile = RegisterFile()
        self.rf = self.register_file  # alias

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
                    self.instruction_memory.load(seg.data())
                else:
                    self.data_memory.load(seg.data())
