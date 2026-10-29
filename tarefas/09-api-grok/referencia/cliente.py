"""Cliente com retentativa, backoff exponencial e timeout."""

import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """A chamada passou de timeout_s e as tentativas se esgotaram, ou uma tentativa estourou o prazo."""


def baixar_pedidos(
    api,
    ids,
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
):
    """Baixa cada id na ordem, com retry só para falha transitória ou timeout.

    LojaErroCliente propaga na hora. Depois da última falha transitória,
    propaga LojaIndisponivel. Depois do último timeout, levanta TempoEsgotado.
    Entre tentativas i = 1, 2, ... dorme backoff_s * 2 ** (i - 1), sem dormir
    depois da última.
    """
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas")
    if max_tentativas < 1:
        raise ValueError("max_tentativas")
    if isinstance(ids, (str, bytes)) or not isinstance(ids, list):
        raise TypeError("ids")
    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s")
    if backoff_s < 0:
        raise ValueError("backoff_s")
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s")
    if timeout_s <= 0:
        raise ValueError("timeout_s")

    return [
        _baixar_um(api, pedido_id, max_tentativas, float(backoff_s), float(timeout_s))
        for pedido_id in ids
    ]


def _baixar_um(api, pedido_id, max_tentativas, backoff_s, timeout_s):
    for tentativa in range(1, max_tentativas + 1):
        try:
            return _chamar(api, pedido_id, timeout_s)
        except LojaErroCliente:
            raise
        except (LojaIndisponivel, TempoEsgotado):
            if tentativa == max_tentativas:
                raise
            espera = backoff_s * (2 ** (tentativa - 1))
            if espera:
                time.sleep(espera)
    raise TempoEsgotado(pedido_id)


def _chamar(api, pedido_id, timeout_s):
    caixa: dict = {}

    def alvo():
        try:
            caixa["valor"] = api.obter_pedido(pedido_id)
        except BaseException as exc:  # propagada para a thread principal
            caixa["erro"] = exc

    thread = threading.Thread(target=alvo, daemon=True)
    thread.start()
    thread.join(timeout_s)
    if thread.is_alive():
        raise TempoEsgotado(pedido_id)
    if "erro" in caixa:
        raise caixa["erro"]
    return caixa["valor"]
