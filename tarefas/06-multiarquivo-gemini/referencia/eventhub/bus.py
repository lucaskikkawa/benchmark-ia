from collections import defaultdict
from typing import Callable, Union
import uuid

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority

HandlerType = Union[EventHandler, Callable[[Event], None]]


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self.dlq = dlq
        self._subscribers: dict[str, list[HandlerType]] = defaultdict(list)
        self._queue: list[Event] = []
        self._history: list[Event] = []

    def subscribe(self, topic: str, handler: HandlerType) -> None:
        if handler not in self._subscribers[topic]:
            self._subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: HandlerType) -> None:
        if topic in self._subscribers and handler in self._subscribers[topic]:
            self._subscribers[topic].remove(handler)

    def publish(
        self, topic: str, payload: dict, priority: Priority = Priority.NORMAL
    ) -> Event:
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        event = Event(id=event_id, topic=topic, payload=payload, priority=priority)
        self._queue.append(event)
        self._history.append(event)
        return event

    def dispatch_next(self) -> bool:
        if not self._queue:
            return False

        # Ordena para pegar maior prioridade (HIGH > NORMAL > LOW) e menor timestamp (FIFO)
        # Priority HIGH = 3, NORMAL = 2, LOW = 1
        self._queue.sort(key=lambda ev: (-int(ev.priority), ev.timestamp))
        event = self._queue.pop(0)

        handlers = list(self._subscribers.get(event.topic, []))
        for handler in handlers:
            try:
                if isinstance(handler, EventHandler):
                    handler.handle(event)
                else:
                    handler(event)
            except Exception as exc:
                if self.dlq is not None:
                    self.dlq.add(event, str(exc))

        return True

    def dispatch_all(self) -> int:
        count = 0
        while self.dispatch_next():
            count += 1
        return count

    def get_history(self, topic: str | None = None) -> list[Event]:
        if topic is None:
            return list(self._history)
        return [ev for ev in self._history if ev.topic == topic]
