
"""
Address Translation and Memory Protection Engine
Project: Segmentation-Based Memory Management
Developer: Aswik
"""

try:
    from src.models import (
        AccessType,
        TranslationStatus,
        TranslationResult,
        AccessRequest,
    )
except ModuleNotFoundError:
    from models import (
        AccessType,
        TranslationStatus,
        TranslationResult,
        AccessRequest,
    )


class AddressTranslator:

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def translate(self, request: AccessRequest) -> TranslationResult:
        """Translate a logical address into a physical address."""

        seg_id = request.seg_id
        offset = request.offset
        size = request.size
        access_type = request.access_type

        logical_addr = (seg_id, offset)

        # 1. Check whether the segment exists
        segment = self.memory_manager.get_segment(seg_id)

        if segment is None:
            return self._fault(
                TranslationStatus.INVALID_SEGMENT,
                logical_addr,
                "Invalid or unallocated segment."
            )

        # 2. Check whether the segment is valid
        if not segment.is_valid:
            return self._fault(
                TranslationStatus.INVALID_SEGMENT,
                logical_addr,
                "Segment is no longer valid.",
                segment.name
            )

        # 3. Validate offset and access size
        if (
            not isinstance(offset, int)
            or isinstance(offset, bool)
            or not isinstance(size, int)
            or isinstance(size, bool)
            or offset < 0
            or size <= 0
            or offset + size > segment.limit
        ):
            return self._fault(
                TranslationStatus.LIMIT_VIOLATION,
                logical_addr,
                (
                    f"Memory boundary violation. "
                    f"Offset: {offset}, Size: {size}, "
                    f"Limit: {segment.limit}."
                ),
                segment.name
            )

        # 4. Validate access type
        if not isinstance(access_type, AccessType):
            return self._fault(
                TranslationStatus.PERMISSION_VIOLATION,
                logical_addr,
                "Invalid access type. Use READ, WRITE or EXECUTE.",
                segment.name
            )

        # 5. Check access permissions
        required_permission = access_type.value

        if required_permission not in segment.permissions:
            return self._fault(
                TranslationStatus.PERMISSION_VIOLATION,
                logical_addr,
                (
                    f"{access_type.name} access denied for "
                    f"{segment.name} segment. "
                    f"Allowed permissions: "
                    f"{sorted(segment.permissions)}."
                ),
                segment.name
            )

        # 6. Calculate physical address
        physical_address = segment.base + offset

        return TranslationResult(
            status=TranslationStatus.OK,
            logical_addr=logical_addr,
            physical_addr=physical_address,
            message=(
                f"Successful {access_type.name} access "
                f"to {segment.name} segment."
            ),
            segment_name=segment.name
        )

    def translate_batch(self, requests):
        """Translate multiple memory access requests."""
        return [
            self.translate(request)
            for request in requests
        ]

    @staticmethod
    def _fault(status, logical_addr, message, segment_name=None):
        """Generate a structured memory protection fault."""

        return TranslationResult(
            status=status,
            logical_addr=logical_addr,
            physical_addr=None,
            message=message,
            segment_name=segment_name
        )


def translate_address(request, memory_manager):
    """Convenience function for address translation."""
    return AddressTranslator(memory_manager).translate(request)
