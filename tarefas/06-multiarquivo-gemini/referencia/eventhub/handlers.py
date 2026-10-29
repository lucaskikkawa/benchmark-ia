from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Event


class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: "Event") -> None:
        """Processa o evento recebido."""
        pass


class DeadLetterQueue:
    """Fila de armazenamento para eventos que falharam durante o processamento."""

    def __init__(self) -> None:
        self._failed: list[tuple["Event", str]] = []

    def add(self, event: "Event", error: str) -> None:
        self._failed.append((event, str(error)))

    def get_failed_events(self) -> list[tuple["Event", str]]:
        return list(self._failed)

    def clear(self) -> None:
        self._failed.clear()
