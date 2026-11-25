try:
    from src.models import MemoryStats, Segment
except ModuleNotFoundError:
    from models import MemoryStats, Segment

from typing import Dict, List, Optional, Set, Tuple

class MemoryManager:
    def __init__(self, total_memory: int = 1024, allocation_policy: str = "FIRST_FIT"):
        if total_memory <= 0:
            raise ValueError("total_memory must be positive")

        policy = allocation_policy.upper()
        if policy not in {"FIRST_FIT", "BEST_FIT", "WORST_FIT"}:
            raise ValueError(f"Unsupported allocation policy: {allocation_policy}")

        self.total_memory = total_memory
        self.allocation_policy = policy
        self.segments: Dict[int, Segment] = {}
        # Free holes stored as (start_address, size), kept sorted by start_address
        self.free_holes: List[Tuple[int, int]] = [(0, total_memory)]

    def _select_hole_index(self, size: int) -> Optional[int]:
        fitting = [
            (idx, start, hole_size)
            for idx, (start, hole_size) in enumerate(self.free_holes)
            if hole_size >= size
        ]
        if not fitting:
            return None

        if self.allocation_policy == "BEST_FIT":
            selected = min(fitting, key=lambda item: item[2])
        elif self.allocation_policy == "WORST_FIT":
            selected = max(fitting, key=lambda item: item[2])
        else:  # FIRST_FIT
            selected = fitting[0]

        return selected[0]

    def _merge_adjacent_holes(self) -> None:
        if not self.free_holes:
            return

        self.free_holes.sort(key=lambda hole: hole[0])
        merged: List[Tuple[int, int]] = [self.free_holes[0]]

        for start, size in self.free_holes[1:]:
            prev_start, prev_size = merged[-1]
            if prev_start + prev_size == start:
                merged[-1] = (prev_start, prev_size + size)
            else:
                merged.append((start, size))

        self.free_holes = merged

    def allocate_segment(
        self,
        seg_id: int,
        name: str,
        limit: int,
        permissions: Set[str],
    ) -> Segment:
        if seg_id in self.segments and self.segments[seg_id].is_valid:
            raise ValueError(f"Active segment with ID {seg_id} already exists")
        if limit <= 0:
            raise ValueError("Segment limit must be greater than 0")

        hole_idx = self._select_hole_index(limit)
        if hole_idx is None:
            raise MemoryError(
                f"Cannot allocate segment '{name}' (limit={limit}): no single free block large enough"
            )

        hole_start, hole_size = self.free_holes.pop(hole_idx)
        base_addr = hole_start

        leftover = hole_size - limit
        if leftover > 0:
            self.free_holes.insert(hole_idx, (base_addr + limit, leftover))
            self._merge_adjacent_holes()

        segment = Segment(
            seg_id=seg_id,
            name=name.upper(),
            base=base_addr,
            limit=limit,
            permissions={perm.upper() for perm in permissions},
            is_valid=True,
        )
        self.segments[seg_id] = segment
        return segment

    def deallocate_segment(self, seg_id: int) -> bool:
        segment = self.segments.get(seg_id)
        if not segment or not segment.is_valid:
            return False

        segment.is_valid = False
        self.free_holes.append((segment.base, segment.limit))
        self._merge_adjacent_holes()
        return True

    def get_segment(self, seg_id: int) -> Optional[Segment]:
        segment = self.segments.get(seg_id)
        if segment and segment.is_valid:
            return segment
        return None

    def get_segment_table(self) -> List[Segment]:
        return [seg for seg in self.segments.values() if seg.is_valid]

    def get_stats(self) -> MemoryStats:
        active_segments = self.get_segment_table()
        used_memory = sum(seg.limit for seg in active_segments)
        free_memory = self.total_memory - used_memory
        largest_free = max((size for _, size in self.free_holes), default=0)

        external_frag = (
            round((free_memory - largest_free) / free_memory, 4)
            if free_memory > 0
            else 0.0
        )

        return MemoryStats(
            total_memory=self.total_memory,
            used_memory=used_memory,
            free_memory=free_memory,
            largest_free_block=largest_free,
            external_fragmentation=external_frag,
            segments={seg.seg_id: seg for seg in active_segments},
        )