#!/usr/bin/env bash

set -euo pipefail

DOWNLOAD_PATH="toolchain.tar.gz"

wget ${RISCV_TOOLCHAIN_URL} -O ${DOWNLOAD_PATH}
tar -xzf ${DOWNLOAD_PATH} bin
rm riscv32-unknown-elf-gdb riscv32-unknown-elf-lto-dump # remove unnecessarily large utils

