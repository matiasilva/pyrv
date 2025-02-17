# pyrv

`pyrv` is an instruction set simulator (ISS) for the RISC-V ISA.

An ISS provides a non-cycle accurate functional model of a CPU core. `pyrv`
simulates the operation of RISC-V hardware threads (harts) conforming to a
particular RISC-V ISA version.

The aim of `pyrv` is to model a resource-constrained bare metal environment,
with simulated on-board flash memory and SRAM. This means, for example, that
`ecall`s are not supported and instead the processor must interact with the host
through the simulator. For OS-level RISC-V work, use the official RISC-V ISA
simulator [Spike](https://github.com/riscv-software-src/riscv-isa-sim) from
RISC-V International.

## Features

- RV32I Base Integer ISA support, v2.1
- runs native ELF files and supports raw binary files
- C runtime support

`pyrv` lays the groundwork for streamlined future ISA support with flexible and
reusable components. Since no CPU exists in isolation, there are also SoC-level
components (SystemBus, Memory, Peripheral, and so on) that allow you to
mix-and-match peripherals to build a custom Hart.

## Getting started

`pyrv` exposes a CLI as part of its package. To access it, install `pyrv`
system-wide or in a virtual environment by running `pip install .` in a cloned
version of this repository.

You can run a binary by invoking the `pyrv` script:

```bash
pyrv my_binary.elf
```

Under the hood, this initializes the Hart and kicks off the instruction loop:

1. Inspect the ELF file and validate it
2. Load the correct ELF segments into memory
3. Begin the instruction loop: fetch, decode, execute

To exit the simulation environment, software must write 1 to the `CONTROL`
register of the `SimControl` block. The instruction loop polls for this bit and
exits if asserted.

## Useful tips

`pyrv` has a toolbox of components ready to be used with a Hart.

### System bus

The system bus ties all peripherals together, with built-in filtering and
validation of addresses. This is akin to the "bus fabric" on modern
microcontrollers. To add an address range to the system bus:

```python
system_bus.add_slave_port(
    "instruction memory",
    INSTRUCTION_MEMORY_BASE,
    INSTRUCTION_MEMORY_SIZE,
    instruction_memory,
)
```

### Registers

You can create a Peripheral with registers by simply subclassing the
`MemoryMappedPeripheral` class. This also adds the mixins associated with a
read/write peripheral.

Defining registers is easily done with additive functions, paving the way for
future deserialization support using a register definition language, like
SystemRDL.

There is a declarative API to trigger callbacks on specific field changes. The
below code tells the Hart to monitor the 32-bit register at address 0 for any
new values falling within the specified range.

```python
peripheral.add_trigger(0x0, lambda new, old: MIN_VALUE <= new <= MAX_VALUE,
                       callback)
```

### The simulator

The simulator creates the instruction loop and is stepped forward by calling the
`Hart`'s `.step()` method.

## Development

`pyrv` is designed to be accessible for development, with useful docstrings and
type hints included in the source code.

Dependencies are managed with [uv](https://docs.astral.sh/uv/). You can consult
the `pyproject.toml` for more detail on `pyrv`'s dependencies.

To run the tests:

```bash
uv run pytest
```

A commit to master must pass all these tests; there is robust CI infrastructure
in place to verify this.

> [!NOTE]
>
> You need a working set of binutils from the GNU Compiler Toolchain for RISC-V,
> built specifically to support the ISA you are targeting.

To run lint:

```bash
ruff --check pyrv
```

## Motivation

This is a hobby project I chipped away at in my free time aimed at learning more
about the ISA and its design decisions, which will in turn influence my work on
my [RV32I softcore implementation](https://github.com/matiasilva/riscv-soc). It
also provides a reference model for running RV binaries.

## License

MIT

## Author

Matias Wang Silva, 2025

## TODO

- [ ] Check against standard RISC-V tests:
      <https://github.com/sysprog21/rv32emu?tab=readme-ov-file#riscof>
- [ ] Add tests for load/stores
- [ ] Add tests for system bus and reads/writes of all widths
- [ ] Add tests for memories
- [ ] Add tests for SimControl
- [ ] Wrap printf, implement exit functionality, propagate exit code
- [ ] Add tests for branches, jumps and so on
- [ ] Get basic simexit, hello world, and load into memory programs working
