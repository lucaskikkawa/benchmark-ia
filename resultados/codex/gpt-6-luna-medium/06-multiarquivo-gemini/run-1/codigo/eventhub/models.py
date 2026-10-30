"""Core event types used by :mod:`eventhub`."""

from dataclasses import dataclass, field
from enum import IntEnum
import time


class Priority(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3


@dataclass
class Event:
    id: str
    topic: str
    payload: dict
    priority: Priority = Priority.NORMAL
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
