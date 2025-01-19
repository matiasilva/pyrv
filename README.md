# pyrv

`pyrv` is an instruction set simulator (ISS) for the RISC-V ISA.

An ISS provides a non-cycle accurate functional model of a particular RISC-V ISA
version. There is an
[official simulator](https://github.com/riscv-software-src/riscv-isa-sim) from
RISC-V International, which is much more feature-rich and should be used for any
official work.

## Features

- RV32I Base Integer ISA support, v2.1
- `.elf` and assembly support
- flexible types make future ISA support easy

## Getting started

## Development

Dependencies are managed with [uv](https://docs.astral.sh/uv/).

To run the tests:

```bash
uv run pytest
```

To run lint:

```bash
ruff --check pyrv
```

## Motivation

This is a hobby project aimed at learning more about the ISA and its design
decisions, which will in turn influence my work on my
[RV32I softcore implementation](https://github.com/matiasilva/riscv-soc). It
also provides a reference model for running RV binaries.

## License

MIT

## Author

Matias Wang Silva, 2025

## TODO

<https://github.com/sysprog21/rv32emu?tab=readme-ov-file#riscof> use numpy types
