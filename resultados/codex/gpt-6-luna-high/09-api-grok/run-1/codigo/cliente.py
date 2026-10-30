"""Cliente da LojaAPI com novas tentativas, backoff e prazo por chamada."""

from __future__ import annotations

import queue
import threading
import time
from typing import Any

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """A chamada da API não terminou dentro do prazo configurado."""


def _validar_numero(nome: str, valor: Any, *, estritamente_positivo: bool) -> None:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nome} deve ser int ou float")
    if estritamente_positivo:
        if not valor > 0:
            raise ValueError(f"{nome} deve ser maior que zero")
    elif not valor >= 0:
        raise ValueError(f"{nome} deve ser maior ou igual a zero")


def _obter_com_timeout(api: Any, pedido_id: str, timeout_s: float) -> dict:
    """Executa uma chamada sem deixar o chamador bloqueado após o prazo."""
    resultado: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)

    def chamar() -> None:
        try:
            resultado.put((True, api.obter_pedido(pedido_id)))
        except BaseException as erro:
            resultado.put((False, erro))

    # Uma thread daemon permite abandonar a espera sem que ela impeça o
    # encerramento do processo caso a implementação da API continue bloqueada.
    thread = threading.Thread(target=chamar, daemon=True)
    thread.start()
    try:
        if timeout_s > threading.TIMEOUT_MAX:
            terminou, valor = resultado.get()
        else:
            terminou, valor = resultado.get(timeout=timeout_s)
    except queue.Empty:
        raise TempoEsgotado(f"tempo esgotado ao obter {pedido_id!r}") from None
    if terminou:
        return valor
    raise valor


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    """Baixa pedidos em ordem, repetindo falhas transitórias e timeouts."""
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente uma lista")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser um int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser pelo menos 1")
    _validar_numero("backoff_s", backoff_s, estritamente_positivo=False)
    _validar_numero("timeout_s", timeout_s, estritamente_positivo=True)

    pedidos: list[dict] = []
    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            try:
                pedido = _obter_com_timeout(api, pedido_id, timeout_s)
            except LojaErroCliente:
                raise
            except (LojaIndisponivel, TempoEsgotado):
                if tentativa == max_tentativas:
                    raise
                atraso = backoff_s * (2 ** (tentativa - 1))
                if atraso:
                    if atraso > threading.TIMEOUT_MAX:
                        threading.Event().wait()
                    else:
                        time.sleep(atraso)
            else:
                pedidos.append(pedido)
                break
    return pedidos
