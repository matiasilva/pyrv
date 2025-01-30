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
- C runtime support
- loads native ELF files or binary files

Under the hood, `pyrv` lays the groundwork for streamlined future ISA support
with flexible and reusable components. Since no CPU exists in isolation, there
are also SoC-level compoennts (SystemBus, Memory, Peripheral, and so on) that
allow you to mix-and-match peripherals to build a custom Hart.

typical Peripheral with registers and a declarative API to trigger callbacks on
specific field changes.

## Getting started

`pyrv` exposes a CLI as part of its package. To access it, install `pyrv`
system-wide or in a virtual environment by running `pip install .` in a cloned
version of this repository.

A simple demo:

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
