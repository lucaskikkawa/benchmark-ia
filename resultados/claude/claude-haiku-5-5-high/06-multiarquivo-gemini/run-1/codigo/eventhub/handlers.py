from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Event


class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: Event) -> None:
        ...


class DeadLetterQueue:
    def __init__(self) -> None:
        self._failed: list[tuple[Event, str]] = []

    def add(self, event: Event, error: str) -> None:
        self._failed.append((event, str(error)))

    def get_failed_events(self) -> list[tuple[Event, str]]:
        return list(self._failed)

    def clear(self) -> None:
        self._failed.clear()
