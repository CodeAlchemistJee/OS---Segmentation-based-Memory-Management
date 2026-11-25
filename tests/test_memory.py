import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.memory_management import MemoryManager


def test_segment_allocation_and_table():
    mm = MemoryManager(total_memory=1024, allocation_policy="FIRST_FIT")
    code = mm.allocate_segment(1, "CODE", 256, {"R", "X"})
    data = mm.allocate_segment(2, "DATA", 256, {"R", "W"})
    stack = mm.allocate_segment(3, "STACK", 128, {"R", "W"})

    assert (code.base, code.limit) == (0, 256)
    assert (data.base, data.limit) == (256, 256)
    assert (stack.base, stack.limit) == (512, 128)
    assert len(mm.get_segment_table()) == 3


def test_deallocation_and_external_fragmentation():
    mm = MemoryManager(total_memory=1024, allocation_policy="FIRST_FIT")
    mm.allocate_segment(1, "CODE", 256, {"R", "X"})
    mm.allocate_segment(2, "DATA", 256, {"R", "W"})
    mm.allocate_segment(3, "STACK", 128, {"R", "W"})

    assert mm.deallocate_segment(2) is True
    stats = mm.get_stats()
    assert stats.used_memory == 384
    assert stats.free_memory == 640
    assert stats.largest_free_block == 384
    assert stats.external_fragmentation == 0.4


def test_adjacent_hole_merging():
    mm = MemoryManager(total_memory=1024, allocation_policy="FIRST_FIT")
    mm.allocate_segment(1, "CODE", 256, {"R", "X"})
    mm.allocate_segment(2, "DATA", 256, {"R", "W"})
    mm.allocate_segment(3, "STACK", 128, {"R", "W"})

    mm.deallocate_segment(2)
    mm.deallocate_segment(3)

    assert mm.free_holes == [(256, 768)]
    assert mm.get_stats().external_fragmentation == 0.0


def test_allocation_failure_when_fragmented():
    mm = MemoryManager(total_memory=600, allocation_policy="FIRST_FIT")
    mm.allocate_segment(1, "S1", 200, {"R"})
    mm.allocate_segment(2, "S2", 200, {"R", "W"})
    mm.allocate_segment(3, "S3", 200, {"R", "W"})

    mm.deallocate_segment(1)
    mm.deallocate_segment(3)

    # Total free = 400, but largest contiguous block = 200
    with pytest.raises(MemoryError):
        mm.allocate_segment(4, "LARGE", 300, {"R", "W"})