from dataclasses import is_dataclass
from enum import IntEnum

import pytest
from eventhub import (
    DeadLetterQueue,
    Event,
    EventBus,
    EventHandler,
    Priority,
)


class CustomHandler(EventHandler):
    def __init__(self):
        self.recebidos = []

    def handle(self, event: Event) -> None:
        self.recebidos.append(event)


class FailingHandler(EventHandler):
    def handle(self, event: Event) -> None:
        raise RuntimeError("Falha proposital de processamento")


def test_publicacao_e_inscricao_basica():
    bus = EventBus()
    handler = CustomHandler()
    bus.subscribe("usuarios.criados", handler)

    ev = bus.publish("usuarios.criados", {"id": 1, "nome": "Maria"})
    assert ev.topic == "usuarios.criados"
    assert ev.payload["id"] == 1

    despachados = bus.dispatch_all()
    assert despachados == 1
    assert len(handler.recebidos) == 1
    assert handler.recebidos[0].id == ev.id


def test_prioridades_despacho():
    bus = EventBus()
    ordem_execucao = []

    def coletor(event: Event):
        ordem_execucao.append(event.payload["tag"])

    bus.subscribe("tarefas", coletor)

    bus.publish("tarefas", {"tag": "baixa"}, priority=Priority.LOW)
    bus.publish("tarefas", {"tag": "alta"}, priority=Priority.HIGH)
    bus.publish("tarefas", {"tag": "normal"}, priority=Priority.NORMAL)

    bus.dispatch_all()
    assert ordem_execucao == ["alta", "normal", "baixa"]


def test_fifo_mesma_prioridade():
    bus = EventBus()
    ordem_execucao = []

    def coletor(event: Event):
        ordem_execucao.append(event.payload["indice"])

    bus.subscribe("logs", coletor)

    eventos = [bus.publish("logs", {"indice": i}, priority=Priority.NORMAL) for i in (1, 2, 3)]

    bus.dispatch_all()
    assert ordem_execucao == [e.payload["indice"] for e in sorted(eventos, key=lambda e: e.timestamp)]


def test_unsubscribe():
    bus = EventBus()
    handler = CustomHandler()
    bus.subscribe("alerta", handler)
    bus.publish("alerta", {"msg": "alerta 1"})
    bus.dispatch_all()
    assert len(handler.recebidos) == 1

    bus.unsubscribe("alerta", handler)
    bus.publish("alerta", {"msg": "alerta 2"})
    bus.dispatch_all()
    assert len(handler.recebidos) == 1


def test_dead_letter_queue_captura_erro():
    dlq = DeadLetterQueue()
    bus = EventBus(dlq=dlq)

    failing = FailingHandler()
    bus.subscribe("pedidos", failing)

    ev = bus.publish("pedidos", {"pedido_id": 99})
    assert bus.dispatch_next() is True

    falhas = dlq.get_failed_events()
    assert len(falhas) == 1
    falha_ev, msg = falhas[0]
    assert falha_ev.id == ev.id
    assert "Falha proposital" in msg


def test_dead_letter_queue_limpeza():
    dlq = DeadLetterQueue()
    ev = Event(id="1", topic="teste", payload={})
    dlq.add(ev, "erro teste")
    assert len(dlq.get_failed_events()) == 1
    dlq.clear()
    assert len(dlq.get_failed_events()) == 0


def test_historico_com_e_sem_filtro():
    bus = EventBus()
    bus.publish("topico.a", {"val": 1})
    bus.publish("topico.b", {"val": 2})
    bus.publish("topico.a", {"val": 3})

    todos = bus.get_history()
    assert len(todos) == 3

    filtrados = bus.get_history("topico.a")
    assert len(filtrados) == 2
    assert [e.payload["val"] for e in filtrados] == [1, 3]


def test_fila_vazia_dispatch():
    bus = EventBus()
    assert bus.dispatch_next() is False
    assert bus.dispatch_all() == 0


def test_multiplos_handlers_para_mesmo_topico():
    bus = EventBus()
    contador = {"chamadas": 0}

    def h1(ev):
        contador["chamadas"] += 1

    def h2(ev):
        contador["chamadas"] += 10

    bus.subscribe("notificacao", h1)
    bus.subscribe("notificacao", h2)

    bus.publish("notificacao", {"msg": "oi"})
    bus.dispatch_all()
    assert contador["chamadas"] == 11


def test_modelos_e_exports_dos_modulos():
    from eventhub.models import Event as ModelEvent, Priority as ModelPriority
    from eventhub.handlers import DeadLetterQueue as HandlerDLQ, EventHandler as HandlerABC
    from eventhub.bus import EventBus as Bus

    assert (Event, Priority, DeadLetterQueue, EventHandler, EventBus) == (
        ModelEvent, ModelPriority, HandlerDLQ, HandlerABC, Bus,
    )
    assert issubclass(Priority, IntEnum)
    assert (Priority.LOW.value, Priority.NORMAL.value, Priority.HIGH.value) == (1, 2, 3)
    assert is_dataclass(Event)
    ev = Event(id="x", topic="t", payload={})
    assert ev.priority == Priority.NORMAL
    assert ev.retry_count == 0
    assert isinstance(ev.timestamp, (int, float))
    assert Event(id="y", topic="t", payload={}, timestamp=123.0).timestamp == 123.0
    with pytest.raises(TypeError):
        EventHandler()


def test_nao_duplica_inscricoes_e_unsubscribe_ausente():
    bus = EventBus()
    recebidos = []
    handler = recebidos.append
    bus.unsubscribe("ausente", handler)
    bus.subscribe("t", handler)
    bus.subscribe("t", handler)
    bus.publish("t", {})
    assert bus.dispatch_all() == 1
    assert len(recebidos) == 1
    bus.unsubscribe("t", handler)
    bus.unsubscribe("t", handler)
    bus.publish("t", {})
    assert bus.dispatch_all() == 1
    assert len(recebidos) == 1


def test_isolamento_de_topicos_e_historico_antes_e_apos_despacho():
    bus = EventBus()
    recebidos = []
    bus.subscribe("a", recebidos.append)
    a = bus.publish("a", {"a": 1})
    b = bus.publish("b", {"b": 1})
    assert isinstance(a, Event)
    assert bus.get_history() == [a, b]
    assert bus.get_history("ausente") == []
    assert bus.dispatch_all() == 2
    assert recebidos == [a]
    assert bus.get_history() == [a, b]
    assert bus.dispatch_next() is False


def test_dlq_retorna_copia_e_converte_erro():
    dlq = DeadLetterQueue()
    ev = Event(id="x", topic="t", payload={})
    dlq.add(ev, RuntimeError("falhou"))
    copia = dlq.get_failed_events()
    assert copia == [(ev, "falhou")]
    copia.clear()
    assert dlq.get_failed_events() == [(ev, "falhou")]


def test_falha_com_dlq_nao_impede_outros_handlers():
    dlq = DeadLetterQueue()
    bus = EventBus(dlq=dlq)
    recebidos = []
    bus.subscribe("t", FailingHandler())
    bus.subscribe("t", recebidos.append)
    ev = bus.publish("t", {})
    assert bus.dispatch_all() == 1
    assert recebidos == [ev]
    assert dlq.get_failed_events() == [(ev, "Falha proposital de processamento")]


def test_falha_sem_dlq_propaga_excecao():
    bus = EventBus(dlq=None)
    bus.subscribe("t", FailingHandler())
    bus.publish("t", {})
    with pytest.raises(RuntimeError) as exc_info:
        bus.dispatch_next()
    assert "Falha proposital" in str(exc_info.value)


def test_despacho_topico_sem_handlers():
    bus = EventBus()
    ev = bus.publish("sem_inscritos", {"msg": "perdido"})
    assert bus.dispatch_next() is True
    assert bus.dispatch_next() is False
    assert bus.get_history() == [ev]


def test_handler_publica_novo_evento_durante_despacho():
    bus = EventBus()
    ordem = []

    def primeiro_handler(ev):
        ordem.append("primeiro")
        bus.publish("segundo_topico", {}, priority=Priority.HIGH)

    def segundo_handler(ev):
        ordem.append("segundo")

    bus.subscribe("primeiro_topico", primeiro_handler)
    bus.subscribe("segundo_topico", segundo_handler)

    bus.publish("primeiro_topico", {})
    total = bus.dispatch_all()
    assert total == 2
    assert ordem == ["primeiro", "segundo"]


def test_get_history_imutabilidade():
    bus = EventBus()
    bus.publish("topico", {"item": 1})
    historico = bus.get_history()
    historico.clear()
    assert len(bus.get_history()) == 1
