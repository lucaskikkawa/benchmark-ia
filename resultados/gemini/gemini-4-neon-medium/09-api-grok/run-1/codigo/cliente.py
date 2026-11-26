"""Cliente com retry, backoff exponencial e timeout para LojaAPI."""

from __future__ import annotations

import threading
import time
from typing import Any

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """Levantada quando todas as tentativas de um pedido expiram por timeout."""


def _validar_parametros(
    ids: Any,
    max_tentativas: Any,
    backoff_s: Any,
    timeout_s: Any,
) -> None:
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente uma list")

    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")

    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if not (backoff_s >= 0):
        raise ValueError("backoff_s deve ser >= 0")

    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if not (timeout_s > 0):
        raise ValueError("timeout_s deve ser > 0")


def _chamar_com_timeout(api: Any, pedido_id: Any, timeout_s: float) -> dict:
    concluido = threading.Event()
    resultado: list[dict] = []
    erro: list[BaseException] = []

    def _executar() -> None:
        try:
            resultado.append(api.obter_pedido(pedido_id))
        except BaseException as exc:
            erro.append(exc)
        finally:
            concluido.set()

    thread = threading.Thread(target=_executar, daemon=True)
    thread.start()

    if not concluido.wait(timeout=timeout_s):
        raise TempoEsgotado(
            f"Tempo esgotado ao obter pedido {pedido_id!r} após {timeout_s}s"
        )

    if erro:
        raise erro[0]

    return resultado[0]


def _baixar_um_pedido(
    api: Any,
    pedido_id: Any,
    *,
    max_tentativas: int,
    backoff_s: float,
    timeout_s: float,
) -> dict:
    for tentativa in range(1, max_tentativas + 1):
        try:
            return _chamar_com_timeout(api, pedido_id, timeout_s)
        except LojaErroCliente:
            raise
        except (LojaIndisponivel, TempoEsgotado):
            if tentativa == max_tentativas:
                raise

        if backoff_s > 0:
            time.sleep(backoff_s * (2 ** (tentativa - 1)))

    raise AssertionError("Estado inalcançável")


def baixar_pedidos(
    api: Any,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    _validar_parametros(ids, max_tentativas, backoff_s, timeout_s)

    resultados: list[dict] = []
    for pedido_id in ids:
        resultados.append(
            _baixar_um_pedido(
                api,
                pedido_id,
                max_tentativas=max_tentativas,
                backoff_s=backoff_s,
                timeout_s=timeout_s,
            )
        )
    return resultados
