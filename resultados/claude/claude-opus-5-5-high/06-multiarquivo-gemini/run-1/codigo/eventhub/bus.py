from __future__ import annotations

import heapq
import itertools
import uuid
from typing import Callable, Union

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority

Handler = Union[EventHandler, Callable[[Event], None]]


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self.dlq = dlq
        self._subscribers: dict[str, list[Handler]] = {}
        self._queue: list[tuple[int, float, int, Event]] = []
        self._history: list[Event] = []
        self._counter = itertools.count()

    def subscribe(self, topic: str, handler: Handler) -> None:
        handlers = self._subscribers.setdefault(topic, [])
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(self, topic: str, handler: Handler) -> None:
        handlers = self._subscribers.get(topic)
        if not handlers:
            return
        if handler in handlers:
            handlers.remove(handler)
        if not handlers:
            del self._subscribers[topic]

    def publish(
        self, topic: str, payload: dict, priority: Priority = Priority.NORMAL
    ) -> Event:
        event = Event(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            priority=Priority(priority),
        )
        heapq.heappush(
            self._queue,
            (-int(event.priority), event.timestamp, next(self._counter), event),
        )
        self._history.append(event)
        return event

    def dispatch_next(self) -> bool:
        if not self._queue:
            return False
        event = heapq.heappop(self._queue)[-1]
        # Snapshot so handlers may (un)subscribe during dispatch safely.
        for handler in list(self._subscribers.get(event.topic, ())):
            try:
                if isinstance(handler, EventHandler):
                    handler.handle(event)
                else:
                    handler(event)
            except Exception as e:
                if self.dlq is None:
                    raise
                self.dlq.add(event, str(e))
        return True

    def dispatch_all(self) -> int:
        count = 0
        while self.dispatch_next():
            count += 1
        return count

    def get_history(self, topic: str | None = None) -> list[Event]:
        if topic is None:
            return list(self._history)
        return [e for e in self._history if e.topic == topic]
