"""In-memory priority event bus."""

import heapq
from collections.abc import Callable
from itertools import count
from uuid import uuid4

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self._dlq = dlq
        self._handlers: dict[str, list[EventHandler | Callable[[Event], None]]] = {}
        self._pending: list[tuple[int, float, int, Event]] = []
        self._sequence = count()
        self._history: list[Event] = []

    def subscribe(
        self, topic: str, handler: EventHandler | Callable[[Event], None]
    ) -> None:
        handlers = self._handlers.setdefault(topic, [])
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(
        self, topic: str, handler: EventHandler | Callable[[Event], None]
    ) -> None:
        handlers = self._handlers.get(topic, [])
        if handler in handlers:
            handlers.remove(handler)
        if not handlers:
            self._handlers.pop(topic, None)

    def publish(
        self, topic: str, payload: dict, priority: Priority = Priority.NORMAL
    ) -> Event:
        event = Event(id=str(uuid4()), topic=topic, payload=payload, priority=priority)
        heapq.heappush(
            self._pending,
            (-event.priority, event.timestamp, next(self._sequence), event),
        )
        self._history.append(event)
        return event

    def dispatch_next(self) -> bool:
        if not self._pending:
            return False
        _, _, _, event = heapq.heappop(self._pending)
        # Snapshot subscriptions so handlers can safely change them during delivery.
        for handler in list(self._handlers.get(event.topic, [])):
            try:
                if isinstance(handler, EventHandler):
                    handler.handle(event)
                else:
                    handler(event)
            except Exception as error:
                if self._dlq is None:
                    raise
                self._dlq.add(event, str(error))
        return True

    def dispatch_all(self) -> int:
        dispatched = 0
        while self.dispatch_next():
            dispatched += 1
        return dispatched

    def get_history(self, topic: str | None = None) -> list[Event]:
        if topic is None:
            return self._history.copy()
        return [event for event in self._history if event.topic == topic]
