from __future__ import annotations

from collections.abc import Callable
import heapq
import itertools
import uuid

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority

Handler = EventHandler | Callable[[Event], None]


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self._dlq = dlq
        self._subscribers: dict[str, list[Handler]] = {}
        # Heap de pendências: (-prioridade, timestamp, seq, evento).
        # `seq` desempata eventos com o mesmo timestamp, mantendo FIFO.
        self._pending: list[tuple[int, float, int, Event]] = []
        self._history: list[Event] = []
        self._seq = itertools.count()

    def subscribe(self, topic: str, handler: Handler) -> None:
        handlers = self._subscribers.setdefault(topic, [])
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(self, topic: str, handler: Handler) -> None:
        handlers = self._subscribers.get(topic)
        if handlers and handler in handlers:
            handlers.remove(handler)
            if not handlers:
                del self._subscribers[topic]

    def publish(self, topic: str, payload: dict, priority: Priority = Priority.NORMAL) -> Event:
        event = Event(id=str(uuid.uuid4()), topic=topic, payload=payload, priority=priority)
        heapq.heappush(
            self._pending,
            (-int(event.priority), event.timestamp, next(self._seq), event),
        )
        self._history.append(event)
        return event

    def dispatch_next(self) -> bool:
        if not self._pending:
            return False

        _, _, _, event = heapq.heappop(self._pending)
        # Cópia: handlers que (des)inscrevem durante o despacho não afetam esta iteração.
        for handler in list(self._subscribers.get(event.topic, [])):
            try:
                if isinstance(handler, EventHandler):
                    handler.handle(event)
                else:
                    handler(event)
            except Exception as e:
                if self._dlq is None:
                    raise
                self._dlq.add(event, str(e))
        return True

    def dispatch_all(self) -> int:
        count = 0
        while self.dispatch_next():
            count += 1
        return count

    def get_history(self, topic: str | None = None) -> list[Event]:
        if topic is None:
            return list(self._history)
        return [event for event in self._history if event.topic == topic]
