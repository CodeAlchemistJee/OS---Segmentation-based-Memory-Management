
"""
Metrics Evaluator
Project: Segmentation-Based Memory Management
"""

from typing import Dict, List

from src.models import TranslationStatus


class MetricsEvaluator:
    """Evaluates memory access and memory utilization metrics."""

    def __init__(self, translator, memory_manager):
        self.translator = translator
        self.memory_manager = memory_manager

    def evaluate(self, requests: List) -> Dict:
        """Evaluate a batch of memory access requests."""

        results = self.translator.translate_batch(requests)

        total = len(results)
        successful = sum(
            result.status == TranslationStatus.OK
            for result in results
        )
        faults = total - successful

        fault_breakdown = {}
        for result in results:
            if result.status != TranslationStatus.OK:
                status = result.status.value
                fault_breakdown[status] = (
                    fault_breakdown.get(status, 0) + 1
                )

        stats = self.memory_manager.get_stats()

        fault_rate = (
            round((faults / total) * 100, 2)
            if total else 0.0
        )

        success_rate = (
            round((successful / total) * 100, 2)
            if total else 0.0
        )

        utilization = (
            round(
                (stats.used_memory / stats.total_memory) * 100,
                2
            )
            if stats.total_memory else 0.0
        )

        return {
            "total_requests": total,
            "successful_accesses": successful,
            "memory_faults": faults,
            "success_rate": success_rate,
            "fault_rate": fault_rate,
            "fault_breakdown": fault_breakdown,
            "total_memory": stats.total_memory,
            "used_memory": stats.used_memory,
            "free_memory": stats.free_memory,
            "memory_utilization": utilization,
            "external_fragmentation": stats.external_fragmentation,
            "largest_free_block": stats.largest_free_block,
        }

    def compare_allocation_policies(
        self,
        policies: List[str],
        total_memory: int,
        segment_sizes: List[int]
    ) -> Dict:
        """Compare memory utilization across allocation policies."""

        from src.memory_management import MemoryManager

        comparison = {}

        for policy in policies:
            manager = MemoryManager(
                total_memory=total_memory,
                allocation_policy=policy
            )

            for index, size in enumerate(segment_sizes, start=1):
                try:
                    manager.allocate_segment(
                        index,
                        f"SEGMENT_{index}",
                        size,
                        {"R", "W"}
                    )
                except MemoryError:
                    break

            stats = manager.get_stats()

            comparison[policy] = {
                "used_memory": stats.used_memory,
                "free_memory": stats.free_memory,
                "memory_utilization": round(
                    (stats.used_memory / stats.total_memory) * 100,
                    2
                ),
                "external_fragmentation": stats.external_fragmentation,
                "largest_free_block": stats.largest_free_block,
            }

        return comparison
