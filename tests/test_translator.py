
import unittest

from src.models import (
    AccessType,
    TranslationStatus,
    AccessRequest,
)
from src.memory_management import MemoryManager
from src.translator import AddressTranslator


class TestAddressTranslator(unittest.TestCase):

    def setUp(self):
        self.mm = MemoryManager(
            total_memory=1024,
            allocation_policy="FIRST_FIT"
        )

        self.mm.allocate_segment(1, "CODE", 256, {"R", "X"})
        self.mm.allocate_segment(2, "DATA", 256, {"R", "W"})
        self.mm.allocate_segment(3, "STACK", 128, {"R", "W"})

        self.translator = AddressTranslator(self.mm)

    def test_valid_code_execution(self):
        request = AccessRequest(1, 120, AccessType.EXECUTE)
        result = self.translator.translate(request)

        self.assertEqual(result.status, TranslationStatus.OK)
        self.assertEqual(result.physical_addr, 120)

    def test_valid_data_write(self):
        request = AccessRequest(2, 64, AccessType.WRITE)
        result = self.translator.translate(request)

        self.assertEqual(result.status, TranslationStatus.OK)
        self.assertEqual(result.physical_addr, 320)

    def test_valid_stack_read(self):
        request = AccessRequest(3, 127, AccessType.READ)
        result = self.translator.translate(request)

        self.assertEqual(result.status, TranslationStatus.OK)
        self.assertEqual(result.physical_addr, 639)

    def test_offset_equal_to_limit(self):
        request = AccessRequest(1, 256, AccessType.READ)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.LIMIT_VIOLATION
        )

    def test_negative_offset(self):
        request = AccessRequest(3, -4, AccessType.WRITE)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.LIMIT_VIOLATION
        )

    def test_code_write_protection(self):
        request = AccessRequest(1, 32, AccessType.WRITE)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.PERMISSION_VIOLATION
        )

    def test_data_execute_protection(self):
        request = AccessRequest(2, 10, AccessType.EXECUTE)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.PERMISSION_VIOLATION
        )

    def test_invalid_segment(self):
        request = AccessRequest(5, 0, AccessType.READ)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.INVALID_SEGMENT
        )

    def test_access_crossing_segment_boundary(self):
        request = AccessRequest(1, 250, AccessType.READ, size=10)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.LIMIT_VIOLATION
        )

    def test_zero_access_size(self):
        request = AccessRequest(1, 10, AccessType.READ, size=0)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.LIMIT_VIOLATION
        )

    def test_deallocated_segment(self):
        self.mm.deallocate_segment(2)

        request = AccessRequest(2, 10, AccessType.READ)
        result = self.translator.translate(request)

        self.assertEqual(
            result.status,
            TranslationStatus.INVALID_SEGMENT
        )

    def test_valid_access_at_last_byte(self):
        request = AccessRequest(1, 255, AccessType.READ)
        result = self.translator.translate(request)

        self.assertEqual(result.status, TranslationStatus.OK)
        self.assertEqual(result.physical_addr, 255)

    def test_batch_translation(self):
        requests = [
            AccessRequest(1, 10, AccessType.READ),
            AccessRequest(2, 20, AccessType.WRITE),
            AccessRequest(1, 30, AccessType.WRITE),
        ]

        results = self.translator.translate_batch(requests)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].status, TranslationStatus.OK)
        self.assertEqual(results[1].status, TranslationStatus.OK)
        self.assertEqual(
            results[2].status,
            TranslationStatus.PERMISSION_VIOLATION
        )


if __name__ == "__main__":
    unittest.main()
