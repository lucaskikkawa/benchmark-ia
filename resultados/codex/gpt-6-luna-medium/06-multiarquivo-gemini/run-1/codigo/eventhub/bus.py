"""In-memory event bus with priority ordered dispatch."""

from collections.abc import Callable
import heapq
from itertools import count
from uuid import uuid4

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self.dlq = dlq
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
        handlers = self._handlers.get(topic)
        if handlers is None:
            return
        try:
            handlers.remove(handler)
        except ValueError:
            return
        if not handlers:
            del self._handlers[topic]

    def publish(
        self, topic: str, payload: dict, priority: Priority = Priority.NORMAL
    ) -> Event:
        event = Event(
            id=str(uuid4()), topic=topic, payload=payload, priority=priority
        )
        heapq.heappush(
            self._pending,
            (-int(event.priority), event.timestamp, next(self._sequence), event),
        )
        self._history.append(event)
        return event

    def dispatch_next(self) -> bool:
        if not self._pending:
            return False
        event = heapq.heappop(self._pending)[3]
        # A snapshot lets handlers change subscriptions during dispatch safely.
        for handler in tuple(self._handlers.get(event.topic, ())):
            try:
                if isinstance(handler, EventHandler):
                    handler.handle(event)
                else:
                    handler(event)
            except Exception as error:
                if self.dlq is None:
                    raise
                self.dlq.add(event, str(error))
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
