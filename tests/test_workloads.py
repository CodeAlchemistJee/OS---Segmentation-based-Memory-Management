
import pytest

from src.workloads import WorkloadGenerator
from src.metrics import MetricsEvaluator
from src.memory_management import MemoryManager
from src.translator import AddressTranslator
from src.models import AccessType


def test_mixed_workload():
    requests = WorkloadGenerator.generate_mixed_workload()

    assert len(requests) == 8
    assert all(request.seg_id > 0 for request in requests)


def test_valid_workload():
    requests = WorkloadGenerator.generate_valid_workload(50)

    assert len(requests) == 50
    assert all(request.offset >= 0 for request in requests)


def test_fault_workload():
    requests = WorkloadGenerator.generate_fault_workload(20)

    assert len(requests) == 20
    assert any(request.seg_id == 9 for request in requests)


def test_empty_workload():
    assert WorkloadGenerator.generate_valid_workload(0) == []
    assert WorkloadGenerator.generate_fault_workload(0) == []


def test_negative_workload_count():
    with pytest.raises(ValueError):
        WorkloadGenerator.generate_valid_workload(-1)

    with pytest.raises(ValueError):
        WorkloadGenerator.generate_fault_workload(-1)


def test_metrics_evaluation():
    mm = MemoryManager(1024)

    mm.allocate_segment(1, "CODE", 256, {"R", "X"})
    mm.allocate_segment(2, "DATA", 256, {"R", "W"})
    mm.allocate_segment(3, "STACK", 128, {"R", "W"})

    translator = AddressTranslator(mm)
    evaluator = MetricsEvaluator(translator, mm)

    requests = [
        # Valid access
        __import__("src.models", fromlist=["AccessRequest"]).AccessRequest(
            1, 10, AccessType.EXECUTE
        ),
        # Invalid access
        __import__("src.models", fromlist=["AccessRequest"]).AccessRequest(
            1, 300, AccessType.READ
        ),
    ]

    result = evaluator.evaluate(requests)

    assert result["total_requests"] == 2
    assert result["successful_accesses"] == 1
    assert result["memory_faults"] == 1
    assert result["fault_rate"] == 50.0


def test_allocation_policy_comparison():
    mm = MemoryManager(1024)
    translator = AddressTranslator(mm)
    evaluator = MetricsEvaluator(translator, mm)

    result = evaluator.compare_allocation_policies(
        ["FIRST_FIT", "BEST_FIT", "WORST_FIT"],
        1024,
        [200, 300, 100, 150]
    )

    assert len(result) == 3
    assert "FIRST_FIT" in result
    assert "BEST_FIT" in result
    assert "WORST_FIT" in result
