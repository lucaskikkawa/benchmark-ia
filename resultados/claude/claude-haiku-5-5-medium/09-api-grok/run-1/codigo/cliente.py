import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    ...


def _validar(ids, max_tentativas, backoff_s, timeout_s):
    if type(ids) is not list:
        raise TypeError("ids deve ser list")
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


def _chamar_com_prazo(api, pedido_id, timeout_s):
    # A API é síncrona e pode dormir; a chamada roda numa thread daemon para
    # que a espera possa ser abandonada após timeout_s.
    resultado = {}

    def alvo():
        try:
            resultado["ok"] = api.obter_pedido(pedido_id)
        except BaseException as erro:
            resultado["erro"] = erro

    thread = threading.Thread(target=alvo, daemon=True)
    thread.start()
    thread.join(timeout_s)
    if thread.is_alive():
        raise TempoEsgotado(pedido_id)
    if "erro" in resultado:
        raise resultado["erro"]
    return resultado["ok"]


def _baixar_um(api, pedido_id, max_tentativas, backoff_s, timeout_s):
    for i in range(1, max_tentativas + 1):
        try:
            return _chamar_com_prazo(api, pedido_id, timeout_s)
        except LojaErroCliente:
            raise
        except (LojaIndisponivel, TempoEsgotado):
            if i == max_tentativas:
                raise
        atraso = backoff_s * 2 ** (i - 1)
        if atraso > 0:
            time.sleep(atraso)


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
