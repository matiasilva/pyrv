# pyrv

`pyrv` is an instruction set simulator (ISS) for the RISC-V ISA.

An ISS provides a non-cycle accurate functional model of a CPU core. `pyrv`
models RISC-V hardware threads (harts) of a particular RISC-V ISA version.

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
- optimizes performance with numpy integration
- flexible and reusable types simplifies future ISA support
- mix-and-match peripherals to build a custom Hart

## Getting started

`pyrv` exposes a CLI, which is available once the package is installed. You can
install `pyrv` system-wide or in a virtual environment by running
`pip install .` in a cloned version of this repository.

A simple demo:

## Development

Dependencies are managed with [uv](https://docs.astral.sh/uv/). You can consult
the `pyproject.toml` for more detail on `pyrv`'s dependencies.

To run the tests:

```bash
uv run pytest
```

> [!WARNING] You need a working set of the GNU Compiler Toolchain for RISC-V,
> built specifically for the ISA you are targeting. It doesn't matter if you
> specify `-march`; if your compiler isn't built for it, it won't work!

There is robust CI infrastructure in place to run all tests on each pull request
/ commit to master.

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

<https://github.com/sysprog21/rv32emu?tab=readme-ov-file#riscof>
