"""Cliente com retry, backoff exponencial e timeout para LojaAPI."""

import math
import threading
import time
from loja_api import LojaIndisponivel


class TempoEsgotado(Exception):
    """Exceção levantada quando a última tentativa excede o timeout."""


def _chamar_com_timeout(api, pedido_id: str, timeout_s: float):
    resultado = []
    erro = []
    concluido = threading.Event()

    def _executar():
        try:
            resultado.append(api.obter_pedido(pedido_id))
        except BaseException as exc:
            erro.append(exc)
        finally:
            concluido.set()

    thread = threading.Thread(target=_executar, daemon=True)
    thread.start()

    if not concluido.wait(timeout=timeout_s):
        raise TempoEsgotado(f"Timeout ao obter pedido {pedido_id!r}")

    if erro:
        raise erro[0]

    return resultado[0]


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    if type(ids) is not list:
        raise TypeError("ids deve ser uma list")

    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")

    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if backoff_s < 0 or math.isnan(backoff_s):
        raise ValueError("backoff_s deve ser >= 0")

    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if timeout_s <= 0 or math.isnan(timeout_s):
        raise ValueError("timeout_s deve ser > 0")

    pedidos: list[dict] = []

    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            try:
                pedido = _chamar_com_timeout(api, pedido_id, timeout_s)
                pedidos.append(pedido)
                break
            except (LojaIndisponivel, TempoEsgotado):
                if tentativa == max_tentativas:
                    raise
                if backoff_s > 0:
                    time.sleep(backoff_s * (2 ** (tentativa - 1)))

    return pedidos
