"""Handler interface and storage for failed deliveries."""

from abc import ABC, abstractmethod

from .models import Event


class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: Event) -> None:
        """Process an event."""


class DeadLetterQueue:
    def __init__(self) -> None:
        self._failed_events: list[tuple[Event, str]] = []

    def add(self, event: Event, error: str) -> None:
        self._failed_events.append((event, str(error)))

    def get_failed_events(self) -> list[tuple[Event, str]]:
        return self._failed_events.copy()

    def clear(self) -> None:
        self._failed_events.clear()
