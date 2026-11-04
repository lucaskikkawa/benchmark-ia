from __future__ import annotations

import heapq
import itertools
import uuid
from collections.abc import Callable

from .handlers import DeadLetterQueue, EventHandler
from .models import Event, Priority

HandlerType = EventHandler | Callable[[Event], None]


class EventBus:
    def __init__(self, dlq: DeadLetterQueue | None = None) -> None:
        self._dlq = dlq
        self._subscribers: dict[str, list[HandlerType]] = {}
        # Heap ordenado por (-prioridade, timestamp, sequência): maior prioridade
        # primeiro e, empatando, FIFO. A sequência desempata timestamps iguais.
        self._queue: list[tuple[int, float, int, Event]] = []
        self._counter = itertools.count()
        self._history: list[Event] = []

    def subscribe(self, topic: str, handler: HandlerType) -> None:
        handlers = self._subscribers.setdefault(topic, [])
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(self, topic: str, handler: HandlerType) -> None:
        handlers = self._subscribers.get(topic)
        if handlers is None or handler not in handlers:
            return
        handlers.remove(handler)
        if not handlers:
            del self._subscribers[topic]

    def publish(
        self, topic: str, payload: dict, priority: Priority = Priority.NORMAL
    ) -> Event:
        event = Event(
            id=uuid.uuid4().hex,
            topic=topic,
            payload=payload,
            priority=priority,
        )
        seq = next(self._counter)
        heapq.heappush(self._queue, (-int(event.priority), event.timestamp, seq, event))
        self._history.append(event)
        return event

    def dispatch_next(self) -> bool:
        if not self._queue:
            return False

        _, _, _, event = heapq.heappop(self._queue)

        # Cópia: handlers inscritos/removidos durante o despacho não afetam esta rodada.
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
