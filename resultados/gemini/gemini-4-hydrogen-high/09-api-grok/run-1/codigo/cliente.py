"""Cliente de pedidos com retry, backoff exponencial e timeout."""

from __future__ import annotations

import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """Levantada quando a última tentativa de um pedido excede o timeout."""


class _TimeoutTentativa(Exception):
    """Sinal interno para uma tentativa que excedeu timeout_s."""


def _validar_parametros(
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
    if not (backoff_s >= 0):
        raise ValueError("backoff_s deve ser >= 0")
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if not (timeout_s > 0):
        raise ValueError("timeout_s deve ser > 0")


def _obter_pedido_com_timeout(api, pedido_id: str, timeout_s: float) -> dict:
    """Chama api.obter_pedido(pedido_id) abandonando a espera após timeout_s."""
    concluido = threading.Event()
    resultado: dict | None = None
    erro: BaseException | None = None

    def _executar() -> None:
        nonlocal resultado, erro
        try:
            resultado = api.obter_pedido(pedido_id)
        except BaseException as exc:
            erro = exc
        finally:
            concluido.set()

    thread = threading.Thread(target=_executar, daemon=True)
    thread.start()

    if not concluido.wait(timeout=timeout_s):
        raise _TimeoutTentativa()
    if erro is not None:
        raise erro
    return resultado  # type: ignore[return-value]


def _baixar_um_pedido(
    api,
    pedido_id: str,
    max_tentativas: int,
    backoff_s: float,
    timeout_s: float,
) -> dict:
    for tentativa in range(1, max_tentativas + 1):
        try:
            return _obter_pedido_com_timeout(api, pedido_id, timeout_s)
        except LojaErroCliente:
            raise
        except LojaIndisponivel:
            if tentativa == max_tentativas:
                raise
        except _TimeoutTentativa:
            if tentativa == max_tentativas:
                raise TempoEsgotado(
                    f"Tempo esgotado ({timeout_s}s) ao obter pedido {pedido_id!r}"
                ) from None
        if backoff_s > 0:
            time.sleep(backoff_s * (2 ** (tentativa - 1)))
    raise AssertionError("unreachable")


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    """Baixa os pedidos em ordem, aplicando timeout, retry e backoff exponencial."""
    _validar_parametros(ids, max_tentativas, backoff_s, timeout_s)
    return [
        _baixar_um_pedido(api, pedido_id, max_tentativas, backoff_s, timeout_s)
        for pedido_id in ids
    ]
