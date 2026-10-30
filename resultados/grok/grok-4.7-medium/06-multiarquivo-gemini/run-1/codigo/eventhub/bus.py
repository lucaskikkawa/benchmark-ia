"""Barramento de eventos em memória."""

import uuid
from collections.abc import Callable

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self._dlq = dlq
        self._subscribers: dict[str, list[EventHandler | Callable[[Event], None]]] = {}
        self._pending: list[tuple[Event, int]] = []
        self._history: list[Event] = []
        self._seq = 0

    def subscribe(
        self, topic: str, handler: EventHandler | Callable[[Event], None]
    ) -> None:
        handlers = self._subscribers.setdefault(topic, [])
        if any(existing is handler for existing in handlers):
            return
        handlers.append(handler)

    def unsubscribe(
        self, topic: str, handler: EventHandler | Callable[[Event], None]
    ) -> None:
        handlers = self._subscribers.get(topic)
        if not handlers:
            return
        self._subscribers[topic] = [existing for existing in handlers if existing is not handler]

    def publish(
        self, topic: str, payload: dict, priority: Priority = Priority.NORMAL
    ) -> Event:
        event = Event(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            priority=priority,
        )
        self._history.append(event)
        self._pending.append((event, self._seq))
        self._seq += 1
        return event

    def _next_index(self) -> int:
        best_index = 0
        best_key: tuple[int, float, int] | None = None
        for index, (event, seq) in enumerate(self._pending):
            key = (-int(event.priority), event.timestamp, seq)
            if best_key is None or key < best_key:
                best_key = key
                best_index = index
        return best_index

    def dispatch_next(self) -> bool:
        if not self._pending:
            return False

        event, _seq = self._pending.pop(self._next_index())
        handlers = list(self._subscribers.get(event.topic, []))
        for handler in handlers:
            try:
                if isinstance(handler, EventHandler):
                    handler.handle(event)
                else:
                    handler(event)
            except Exception as exc:
                if self._dlq is None:
                    raise
                self._dlq.add(event, str(exc))
        return True

    def dispatch_all(self) -> int:
        dispatched = 0
        while self.dispatch_next():
            dispatched += 1
        return dispatched

    def get_history(self, topic: str | None = None) -> list[Event]:
        if topic is None:
            return list(self._history)
        return [event for event in self._history if event.topic == topic]
