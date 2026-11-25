from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Set, Tuple


class AccessType(Enum):
    READ = "R"
    WRITE = "W"
    EXECUTE = "X"


class TranslationStatus(Enum):
    OK = "OK"
    INVALID_SEGMENT = "INVALID_SEGMENT"
    LIMIT_VIOLATION = "LIMIT_VIOLATION"
    PERMISSION_VIOLATION = "PERMISSION_VIOLATION"


@dataclass
class Segment:
    seg_id: int
    name: str
    base: int
    limit: int
    permissions: Set[str]
    is_valid: bool = True


@dataclass
class AccessRequest:
    seg_id: int
    offset: int
    access_type: AccessType
    size: int = 1


@dataclass
class TranslationResult:
    status: TranslationStatus
    logical_addr: Tuple[int, int]
    physical_addr: Optional[int]
    message: str
    segment_name: Optional[str] = None


@dataclass
class MemoryStats:
    total_memory: int
    used_memory: int
    free_memory: int
    largest_free_block: int
    external_fragmentation: float
    segments: Dict[int, Segment] = field(default_factory=dict)