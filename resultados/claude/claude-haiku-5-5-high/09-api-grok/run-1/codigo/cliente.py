"""Cliente de baixa de pedidos com timeout, retry e backoff exponencial.

Só biblioteca padrão. A chamada à API roda numa thread daemon para que o
timeout seja imposto de verdade: se passar do prazo, a espera é abandonada
e a thread continua sozinha, sem segurar o processo.
"""

import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """A chamada à API passou de timeout_s segundos."""


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    _validar(ids, max_tentativas, backoff_s, timeout_s)
    return [
        _baixar_um(api, pedido_id, max_tentativas, backoff_s, timeout_s)
        for pedido_id in ids
    ]


def _validar(ids, max_tentativas, backoff_s, timeout_s) -> None:
    if not isinstance(ids, list):
        raise TypeError("ids deve ser list")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")
    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if not backoff_s >= 0:
        raise ValueError("backoff_s deve ser >= 0")
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if not timeout_s > 0:
        raise ValueError("timeout_s deve ser > 0")


def _baixar_um(api, pedido_id, max_tentativas, backoff_s, timeout_s) -> dict:
    for i in range(1, max_tentativas + 1):
        try:
            return _chamar_com_prazo(api, pedido_id, timeout_s)
        except (LojaIndisponivel, TempoEsgotado):
            if i == max_tentativas:
                raise
            espera = backoff_s * 2 ** (i - 1)
            if espera > 0:
                time.sleep(espera)
    raise AssertionError("inalcançável: max_tentativas >= 1")


def _chamar_com_prazo(api, pedido_id, timeout_s) -> dict:
    resultado = {}

    def alvo() -> None:
        try:
            resultado["pedido"] = api.obter_pedido(pedido_id)
        except BaseException as erro:
            resultado["erro"] = erro

    thread = threading.Thread(target=alvo, daemon=True)
    thread.start()
    # TIMEOUT_MAX limita o join; inf ou valores enormes viram o máximo aceito.
    thread.join(min(timeout_s, threading.TIMEOUT_MAX))
    if thread.is_alive():
        raise TempoEsgotado(f"{pedido_id} passou de {timeout_s}s")
    if "erro" in resultado:
        raise resultado["erro"]
    return resultado["pedido"]
