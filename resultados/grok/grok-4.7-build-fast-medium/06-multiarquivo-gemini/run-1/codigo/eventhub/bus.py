import heapq
import uuid
from collections.abc import Callable

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self._dlq = dlq
        self._handlers: dict[str, list[EventHandler | Callable[[Event], None]]] = {}
        self._pending: list[tuple[int, float, int, Event]] = []
        self._history: list[Event] = []
        self._seq = 0

    def subscribe(
        self,
        topic: str,
        handler: EventHandler | Callable[[Event], None],
    ) -> None:
        handlers = self._handlers.setdefault(topic, [])
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(
        self,
        topic: str,
        handler: EventHandler | Callable[[Event], None],
    ) -> None:
        handlers = self._handlers.get(topic)
        if not handlers:
            return
        try:
            handlers.remove(handler)
        except ValueError:
            return

    def publish(
        self,
        topic: str,
        payload: dict,
        priority: Priority = Priority.NORMAL,
    ) -> Event:
        event = Event(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            priority=priority,
        )
        self._history.append(event)
        heapq.heappush(
            self._pending,
            (-int(event.priority), event.timestamp, self._seq, event),
        )
        self._seq += 1
        return event

    def dispatch_next(self) -> bool:
        if not self._pending:
            return False

        _, _, _, event = heapq.heappop(self._pending)
        handlers = list(self._handlers.get(event.topic, ()))
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
