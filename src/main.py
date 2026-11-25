import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.memory_management import MemoryManager


def print_state(mm: MemoryManager, title: str) -> None:
    print(f"\n=== {title} ===")
    stats = mm.get_stats()
    print(f"Policy: {mm.allocation_policy}")
    print(
        f"Total: {stats.total_memory} | Used: {stats.used_memory} | "
        f"Free: {stats.free_memory} | Largest Hole: {stats.largest_free_block} | "
        f"External Fragmentation: {stats.external_fragmentation * 100:.2f}%"
    )
    print("Free Holes (start, size):", mm.free_holes)
    print("Segment Table:")
    print(f"{'ID':<4} {'Name':<8} {'Base':<6} {'Limit':<6} {'Perms':<10} {'Valid'}")
    for seg in mm.get_segment_table():
        perms = ",".join(sorted(seg.permissions))
        print(f"{seg.seg_id:<4} {seg.name:<8} {seg.base:<6} {seg.limit:<6} {perms:<10} {seg.is_valid}")


def run_demo() -> None:
    mm = MemoryManager(total_memory=1024, allocation_policy="FIRST_FIT")
    mm.allocate_segment(1, "CODE", 256, {"R", "X"})
    mm.allocate_segment(2, "DATA", 256, {"R", "W"})
    mm.allocate_segment(3, "STACK", 128, {"R", "W"})
    print_state(mm, "Initial CODE, DATA, STACK Allocation")

    mm.deallocate_segment(2)
    print_state(mm, "After Deallocating DATA (Segment 2)")

    mm.deallocate_segment(3)
    print_state(mm, "After Deallocating STACK (Segment 3) & Hole Merging")


if __name__ == "__main__":
    run_demo()