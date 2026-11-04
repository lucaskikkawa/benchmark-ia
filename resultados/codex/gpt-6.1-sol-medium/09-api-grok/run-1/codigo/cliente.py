"""Download sequencial de pedidos com timeout e tentativas limitadas."""

from queue import Empty, Queue
from threading import Thread
from time import sleep

from loja_api import LojaIndisponivel


class TempoEsgotado(Exception):
    """A tentativa não terminou dentro do prazo permitido."""


def _obter_com_timeout(api, pedido_id, timeout_s):
    resposta = Queue(maxsize=1)

    def executar():
        try:
            pedido = api.obter_pedido(pedido_id)
        except BaseException as erro:
            resposta.put((False, erro))
        else:
            resposta.put((True, pedido))

    # Uma chamada expirada pode continuar executando, mas não deve impedir
    # o retorno do cliente nem o encerramento do processo.
    Thread(target=executar, daemon=True).start()
    try:
        sucesso, valor = resposta.get(
            timeout=None if timeout_s == float("inf") else timeout_s
        )
    except Empty:
        raise TempoEsgotado(
            f"Prazo de {timeout_s} segundos esgotado para {pedido_id!r}"
        ) from None
    if sucesso:
        return valor
    raise valor


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    """Baixa cada ocorrência de id, interrompendo no primeiro erro definitivo.

    Timeouts abandonam a espera; a chamada em processo pode terminar depois.
    Cada tentativa possui sua própria fila para descartar esses resultados.
    """
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente list")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser pelo menos 1")
    for nome, valor in (("backoff_s", backoff_s), ("timeout_s", timeout_s)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError(f"{nome} deve ser int ou float")
    if not backoff_s >= 0:
        raise ValueError("backoff_s deve ser maior ou igual a zero")
    if not timeout_s > 0:
        raise ValueError("timeout_s deve ser maior que zero")

    pedidos = []
    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            try:
                pedido = _obter_com_timeout(api, pedido_id, timeout_s)
            except (LojaIndisponivel, TempoEsgotado):
                if tentativa == max_tentativas:
                    raise
                if backoff_s != 0:
                    sleep(backoff_s * 2 ** (tentativa - 1))
            else:
                pedidos.append(pedido)
                break
    return pedidos
