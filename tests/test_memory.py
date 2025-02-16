"""Test reads/writes to a memory model"""

from random import randint

import pytest

from pyrv.helpers import bmask
from pyrv.models import Memory


@pytest.fixture
def mem():
    return Memory(16)


@pytest.mark.parametrize("size", [16, 64, 128])
@pytest.mark.parametrize("n", [1, 2, 4])
def test_memory_smoke(size: int, n: int):
    m = Memory(size)
    assert m.read(8, n) == 0
    lim = bmask(n)
    to_write = randint(0, lim)
    m.write(8, to_write, n)
    assert m.read(8, to_write & lim)
