"""Cliente da LojaAPI com retry, backoff exponencial e timeout por chamada."""

import math
import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(TimeoutError):
    """A última tentativa de um pedido passou de ``timeout_s``."""


_TIMEOUT = object()


def _validar_numero(nome, valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nome} deve ser int ou float")


def _validar(ids, max_tentativas, backoff_s, timeout_s):
    if type(ids) is not list:
        raise TypeError("ids deve ser list")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")
    _validar_numero("backoff_s", backoff_s)
    if not backoff_s >= 0:
        raise ValueError("backoff_s deve ser >= 0")
    _validar_numero("timeout_s", timeout_s)
    if not timeout_s > 0:
        raise ValueError("timeout_s deve ser > 0")


def _chamar_com_prazo(api, pedido_id, timeout_s):
    """Roda ``api.obter_pedido`` numa thread daemon e espera até ``timeout_s``.

    Devolve o dict, levanta a exceção da API ou devolve ``_TIMEOUT``. Em caso
    de timeout a thread é abandonada (daemon, não segura a saída do processo).
    """
    caixa = {}
    pronto = threading.Event()

    def alvo():
        try:
            caixa["resultado"] = api.obter_pedido(pedido_id)
        except BaseException as exc:  # repassada à thread chamadora
            caixa["erro"] = exc
        finally:
            pronto.set()

    threading.Thread(target=alvo, name=f"obter_pedido:{pedido_id!r}", daemon=True).start()
    if not pronto.wait(None if math.isinf(timeout_s) else timeout_s):
        return _TIMEOUT
    if "erro" in caixa:
        raise caixa["erro"]
    return caixa["resultado"]


def _baixar_um(api, pedido_id, max_tentativas, backoff_s, timeout_s):
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
                    f"{pedido_id!r}: {max_tentativas} tentativa(s) passaram de {timeout_s}s"
                )
        espera = backoff_s * 2 ** (i - 1)
        if espera > 0:
            time.sleep(espera)
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
