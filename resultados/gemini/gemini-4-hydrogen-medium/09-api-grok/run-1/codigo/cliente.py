"""Cliente com retry, backoff exponencial e timeout para LojaAPI."""

from __future__ import annotations

import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """Levantada quando a última tentativa de obter um pedido excede timeout_s."""


def _validar_parametros(
    ids: list[str],
    max_tentativas: int,
    backoff_s: float,
    timeout_s: float,
) -> None:
    if type(ids) is not list:
        raise TypeError("ids deve ser uma list")
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


def _chamar_com_timeout(api, pedido_id: str, timeout_s: float) -> dict:
    resultado: dict | None = None
    erro: BaseException | None = None
    concluido = threading.Event()

    def _alvo() -> None:
        nonlocal resultado, erro
        try:
            resultado = api.obter_pedido(pedido_id)
        except BaseException as exc:
            erro = exc
        finally:
            concluido.set()

    thread = threading.Thread(target=_alvo, daemon=True)
    thread.start()
    if not concluido.wait(timeout=timeout_s):
        raise TempoEsgotado(f"tempo esgotado ({timeout_s}s) para {pedido_id!r}")
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
            return _chamar_com_timeout(api, pedido_id, timeout_s)
        except LojaErroCliente:
            raise
        except (LojaIndisponivel, TempoEsgotado):
            if tentativa == max_tentativas:
                raise
            if backoff_s > 0:
                time.sleep(backoff_s * (2 ** (tentativa - 1)))
    raise AssertionError("inacessível")


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    """Baixa os pedidos na ordem de ``ids`` aplicando timeout, retry e backoff."""
    _validar_parametros(ids, max_tentativas, backoff_s, timeout_s)
    return [
        _baixar_um_pedido(api, pedido_id, max_tentativas, backoff_s, timeout_s)
        for pedido_id in ids
    ]
