"""Cliente de LojaAPI com retry, backoff exponencial e timeout por chamada."""

import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """A última tentativa de um id passou de timeout_s."""


_TIMEOUT = object()


def _validar(ids, max_tentativas, backoff_s, timeout_s) -> None:
    if type(ids) is not list:
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


def _chamar_com_prazo(api, pedido_id, timeout_s):
    """Roda obter_pedido numa thread daemon; devolve _TIMEOUT se passar do prazo."""
    caixa: dict = {}

    def alvo() -> None:
        try:
            caixa["valor"] = api.obter_pedido(pedido_id)
        except BaseException as exc:  # repassada à thread chamadora
            caixa["erro"] = exc

    t = threading.Thread(target=alvo, daemon=True)
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        return _TIMEOUT
    if "erro" in caixa:
        raise caixa["erro"]
    return caixa["valor"]


def _baixar_um(api, pedido_id, max_tentativas, backoff_s, timeout_s) -> dict:
    for i in range(1, max_tentativas + 1):
        try:
            resultado = _chamar_com_prazo(api, pedido_id, timeout_s)
        except LojaErroCliente:
            raise
        except LojaIndisponivel:
            if i == max_tentativas:
                raise
        else:
            if resultado is not _TIMEOUT:
                return resultado
            if i == max_tentativas:
                raise TempoEsgotado(
                    f"{pedido_id!r} excedeu {timeout_s}s em {max_tentativas} tentativas"
                )
        if backoff_s > 0:
            time.sleep(backoff_s * 2 ** (i - 1))
    raise AssertionError("inalcançável")


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
