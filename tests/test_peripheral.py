"""Tests the register functionality of a memory-mapped peripheral"""

import pytest

from pyrv.helpers import bselect
from pyrv.models import MemoryMappedPeripheral, UnallocatedAddressException


@pytest.fixture
def peri():
    return MemoryMappedPeripheral(128)


@pytest.mark.parametrize("addr", [0, 24, 36, 72])
def test_read(addr: int, peri: MemoryMappedPeripheral):
    peri.set_register(addr, 0xAABBCCDD)

    # byte reads
    assert peri.read(addr + 0x0, 1) == 0xDD
    assert peri.read(addr + 0x1, 1) == 0xCC
    assert peri.read(addr + 0x2, 1) == 0xBB
    assert peri.read(addr + 0x3, 1) == 0xAA

    # halfword reads
    assert peri.read(addr + 0x0, 2) == 0xCCDD
    assert peri.read(addr + 0x2, 2) == 0xAABB

    # word reads
    assert peri.read(addr + 0x0, 4) == 0xAABBCCDD


def test_read_unallocated(peri: MemoryMappedPeripheral):
    with pytest.raises(UnallocatedAddressException):
        peri.read(0x0, 1)


def test_write_unallocated(peri: MemoryMappedPeripheral):
    with pytest.raises(UnallocatedAddressException):
        peri.write(0x0, 0xAABBDDCC, 1)


@pytest.mark.parametrize("addr", [0, 24, 36, 72])
@pytest.mark.parametrize("n_bytes", [1, 2, 3, 4])
def test_write(addr: int, n_bytes: int, peri: MemoryMappedPeripheral):
    test_val = 0xAABBCCDD
    peri.alloc_register(addr)
    peri.write(addr, test_val, n_bytes)
    exp_val = bselect(test_val, n_bytes * 8 - 1, 0)
    # byte reads
    for i in range(4):
        assert peri.read(addr + i, 1) == bselect(exp_val, (i + 1) * 8 - 1, i * 8)

    # halfword reads
    assert peri.read(addr + 0x0, 2) == bselect(exp_val, 15, 0)
    assert peri.read(addr + 0x2, 2) == bselect(exp_val, 31, 16)
    # ^ always reads 0 as writes take from lower bits

    # word reads
    assert peri.read(addr, 4) == exp_val


def test_triggers(peri: MemoryMappedPeripheral):
    peri.alloc_register(0x0)

    flag = False

    def set_flag(new, old):
        nonlocal flag
        flag = True

    peri.add_trigger(0x0, lambda new, old: new == 0xAABB, set_flag)
    peri.write(0x0, 0xAABB, 4)
    assert flag
