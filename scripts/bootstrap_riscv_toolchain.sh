#!/usr/bin/env bash

set -euo pipefail

DOWNLOAD_PATH="toolchain.tar.gz"

mkdir build
cd build
wget -nv ${RISCV_TOOLCHAIN_URL} -O ${DOWNLOAD_PATH}
tar -xzf ${DOWNLOAD_PATH} bin
rm bin/riscv32-unknown-elf-gdb bin/riscv32-unknown-elf-lto-dump # remove unnecessarily large utils

