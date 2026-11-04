"""Cliente para LojaAPI com retry, backoff exponencial e timeout."""

from __future__ import annotations

import math
import threading
import time


class TempoEsgotado(Exception):
    """Exceção levantada quando as tentativas de um pedido esgotam por timeout."""


def _eh_loja_indisponivel(exc: BaseException) -> bool:
    """Verifica se a exceção é LojaIndisponivel ou subclasse."""
    return any(cls.__name__ == "LojaIndisponivel" for cls in type(exc).__mro__)


def _executar_com_timeout(api, pedido_id: str, timeout_s: float):
    """Executa api.obter_pedido(pedido_id) com prazo limite de timeout_s segundos.

    Devolve uma tupla (resultado, excecao, timed_out). Se timeout_s expirar
    antes da chamada terminar, abandona a espera e devolve (None, None, True).
    """
    resultado = None
    excecao = None
    terminou = threading.Event()

    def worker():
        nonlocal resultado, excecao
        try:
            resultado = api.obter_pedido(pedido_id)
        except BaseException as exc:
            excecao = exc
        finally:
            terminou.set()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    if not terminou.wait(timeout=timeout_s):
        return None, None, True

    return resultado, excecao, False


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    """Baixa pedidos na ordem informada com retry, backoff e timeout."""
    # Validações antes de qualquer chamada
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente do tipo list")

    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")

    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if math.isnan(backoff_s) or math.isinf(backoff_s) or backoff_s < 0:
        raise ValueError("backoff_s deve ser >= 0")

    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if math.isnan(timeout_s) or math.isinf(timeout_s) or timeout_s <= 0:
        raise ValueError("timeout_s deve ser > 0")

    pedidos: list[dict] = []

    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            resultado, excecao, timed_out = _executar_com_timeout(api, pedido_id, timeout_s)

            if timed_out:
                if tentativa == max_tentativas:
                    raise TempoEsgotado()
                if backoff_s > 0:
                    time.sleep(backoff_s * (2 ** (tentativa - 1)))
                continue

            if excecao is not None:
                if _eh_loja_indisponivel(excecao):
                    if tentativa == max_tentativas:
                        raise excecao
                    if backoff_s > 0:
                        time.sleep(backoff_s * (2 ** (tentativa - 1)))
                    continue
                # LojaErroCliente ou qualquer outro erro propaga na hora
                raise excecao

            # Sucesso
            pedidos.append(resultado)
            break

    return pedidos


__all__ = ["TempoEsgotado", "baixar_pedidos"]
