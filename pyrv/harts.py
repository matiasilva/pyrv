from pyrv.helpers import MutableRegister
from pyrv.models import (
    DataMemory,
    InstructionMemory,
    RegisterFile,
    SimControl,
    SystemBus,
)
from pyrv.instructions import decode_instr


class Hart:
    """
    Barebones hart used for tests where a full system bus and memories are unnecessary
    """

    def __init__(self) -> None:
        self.pc: MutableRegister = MutableRegister()
        self.register_file: RegisterFile = RegisterFile()
        self.data_memory: DataMemory | None = None
        self.instruction_memory: InstructionMemory | None = None
        self.system_bus: SystemBus | None = None
        self.sim_control: SimControl | None = None

        self.rf = self.register_file  # alias


class BasicHart(Hart):
    """
    A hart containing the minimum necessary components for code execution.
    """

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
