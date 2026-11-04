"""Cliente da loja com tentativas limitadas e timeout por chamada."""

import math
import queue
import threading
import time

from loja_api import LojaIndisponivel


class TempoEsgotado(Exception):
    """Uma chamada à API excedeu o prazo de espera."""


def _chamar_com_timeout(api, pedido_id, timeout_s):
    resultado = queue.Queue(maxsize=1)

    def executar():
        try:
            pedido = api.obter_pedido(pedido_id)
        except BaseException as erro:
            resultado.put((False, erro))
        else:
            resultado.put((True, pedido))

    # A chamada abandonada pode terminar em segundo plano, sem bloquear a
    # próxima tentativa nem impedir o encerramento do processo.
    threading.Thread(target=executar, daemon=True).start()
    prazo = None if timeout_s == math.inf else timeout_s
    try:
        sucesso, valor = resultado.get(timeout=prazo)
    except queue.Empty:
        raise TempoEsgotado(f"Tempo esgotado ao obter {pedido_id!r}") from None
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
    """Baixa os pedidos em ordem, repetindo falhas transitórias e timeouts."""
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente uma list")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser pelo menos 1")
    for nome, valor in (("backoff_s", backoff_s), ("timeout_s", timeout_s)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError(f"{nome} deve ser int ou float")
    if not backoff_s >= 0:
        raise ValueError("backoff_s deve ser não negativo")
    if not timeout_s > 0:
        raise ValueError("timeout_s deve ser positivo")

    pedidos = []
    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            try:
                pedido = _chamar_com_timeout(api, pedido_id, timeout_s)
            except (LojaIndisponivel, TempoEsgotado):
                if tentativa == max_tentativas:
                    raise
                if backoff_s:
                    time.sleep(backoff_s * 2 ** (tentativa - 1))
            else:
                pedidos.append(pedido)
                break
    return pedidos
