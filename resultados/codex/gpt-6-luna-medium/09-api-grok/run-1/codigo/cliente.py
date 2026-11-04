"""Cliente para a API local da loja, com retry, backoff e timeout."""

from __future__ import annotations

import queue
import threading
import time
from typing import Any

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """A chamada à API excedeu o prazo configurado."""


def _chamar_com_timeout(api: Any, pedido_id: str, timeout_s: float) -> dict:
    """Executa a chamada em thread daemon para poder abandonar a espera."""
    resultado: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)

    def executar() -> None:
        try:
            resultado.put((True, api.obter_pedido(pedido_id)))
        except BaseException as erro:
            resultado.put((False, erro))

    thread = threading.Thread(target=executar, daemon=True)
    thread.start()
    try:
        sucesso, valor = resultado.get(timeout=timeout_s)
    except queue.Empty:
        raise TempoEsgotado(f"tempo esgotado ao obter {pedido_id!r}") from None

    if sucesso:
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
    """Baixa pedidos em ordem, repetindo falhas transitórias até o limite."""
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente uma lista")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")
    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if backoff_s < 0:
        raise ValueError("backoff_s deve ser >= 0")
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if timeout_s <= 0:
        raise ValueError("timeout_s deve ser > 0")

    pedidos: list[dict] = []
    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            try:
                pedido = _chamar_com_timeout(api, pedido_id, timeout_s)
            except LojaErroCliente:
                raise
            except (LojaIndisponivel, TempoEsgotado):
                if tentativa == max_tentativas:
                    raise
                atraso = backoff_s * 2 ** (tentativa - 1)
                if atraso:
                    time.sleep(atraso)
            else:
                pedidos.append(pedido)
                break
    return pedidos
