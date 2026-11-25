
"""
Workload Generator
Project: Segmentation-Based Memory Management
"""

from typing import List

from src.models import AccessRequest, AccessType


class WorkloadGenerator:
    """Generates memory access requests for benchmarking."""

    @staticmethod
    def generate_mixed_workload() -> List[AccessRequest]:
        """Generate valid and invalid memory requests."""

        return [
            # Valid accesses
            AccessRequest(1, 64, AccessType.EXECUTE),
            AccessRequest(2, 128, AccessType.WRITE),
            AccessRequest(3, 64, AccessType.READ),

            # Boundary violations
            AccessRequest(1, 300, AccessType.READ),
            AccessRequest(3, -4, AccessType.WRITE),

            # Permission violations
            AccessRequest(1, 16, AccessType.WRITE),
            AccessRequest(2, 10, AccessType.EXECUTE),

            # Invalid segment
            AccessRequest(9, 0, AccessType.READ),
        ]

    @staticmethod
    def generate_valid_workload(count: int = 100) -> List[AccessRequest]:
        """Generate valid memory requests."""

        if count < 0:
            raise ValueError("Count cannot be negative")

        segments = [
            (1, AccessType.READ),
            (1, AccessType.EXECUTE),
            (2, AccessType.READ),
            (2, AccessType.WRITE),
            (3, AccessType.READ),
            (3, AccessType.WRITE),
        ]

        return [
            AccessRequest(
                seg_id=segments[i % len(segments)][0],
                offset=i % 100,
                access_type=segments[i % len(segments)][1]
            )
            for i in range(count)
        ]

    @staticmethod
    def generate_fault_workload(count: int = 100) -> List[AccessRequest]:
        """Generate requests that intentionally cause faults."""

        if count < 0:
            raise ValueError("Count cannot be negative")

        faults = [
            AccessRequest(1, 300, AccessType.READ),
            AccessRequest(1, 10, AccessType.WRITE),
            AccessRequest(2, 10, AccessType.EXECUTE),
            AccessRequest(9, 0, AccessType.READ),
            AccessRequest(3, -5, AccessType.READ),
        ]

        return [faults[i % len(faults)] for i in range(count)]

    @staticmethod
    def generate_workload(count: int = 100) -> List[AccessRequest]:
        """Generate a combination of valid and invalid requests."""

        if count < 0:
            raise ValueError("Count cannot be negative")

        mixed = WorkloadGenerator.generate_mixed_workload()

        return [
            mixed[i % len(mixed)]
            for i in range(count)
        ]
