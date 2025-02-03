"""Test reads/writes to a memory model"""

import pytest

from pyrv.models import Memory


@pytest.fixture
def mem():
    return Memory(1)


@pytest.mark.parametrize("width", [1, 2, 4])
def test_memory_width(width: int):
    m = Memory(1, width)
    # m.write()
