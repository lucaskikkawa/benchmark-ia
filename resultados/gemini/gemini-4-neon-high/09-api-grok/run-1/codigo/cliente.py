"""Cliente de pedidos com retry, backoff exponencial e timeout por tentativa."""

import math
import threading
import time

from loja_api import LojaIndisponivel


class TempoEsgotado(Exception):
    """Levantada quando uma tentativa excede timeout_s na última chance."""


def _validar_argumentos(
    ids: list[str],
    max_tentativas: int,
    backoff_s: float,
    timeout_s: float,
) -> None:
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente list")

    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")

    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if not math.isfinite(backoff_s) or backoff_s < 0:
        raise ValueError("backoff_s deve ser um número finito >= 0")

    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if not math.isfinite(timeout_s) or timeout_s <= 0:
        raise ValueError("timeout_s deve ser um número finito > 0")


def _chamar_com_timeout(api, pedido_id: str, timeout_s: float) -> dict:
    iniciado = threading.Event()
    concluido = threading.Event()
    resultado = None
    erro: BaseException | None = None

    def _executar() -> None:
        nonlocal resultado, erro
        iniciado.set()
        try:
            resultado = api.obter_pedido(pedido_id)
        except BaseException as exc:
            erro = exc
        finally:
            concluido.set()

    thread = threading.Thread(target=_executar, daemon=True)
    thread.start()
    iniciado.wait()

    if not concluido.wait(timeout_s):
        raise TempoEsgotado(f"tempo esgotado ({timeout_s}s) para pedido {pedido_id!r}")

    if erro is not None:
        raise erro

    return resultado


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    _validar_argumentos(ids, max_tentativas, backoff_s, timeout_s)

    pedidos: list[dict] = []
    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            try:
                pedido = _chamar_com_timeout(api, pedido_id, timeout_s)
                break
            except (LojaIndisponivel, TempoEsgotado):
                if tentativa == max_tentativas:
                    raise
                if backoff_s > 0:
                    time.sleep(backoff_s * (2 ** (tentativa - 1)))
        pedidos.append(pedido)

    return pedidos
