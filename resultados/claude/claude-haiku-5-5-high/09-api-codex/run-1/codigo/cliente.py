"""Cliente com retry e backoff exponencial para a API local."""
import math
import time

from fake_api import ErroTemporario


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Obtém `chave` da API, repetindo apenas falhas transitórias.

    `tentativas` é o número máximo de chamadas, incluindo a primeira. Após a falha
    de índice i (0, 1, ...), espera `backoff * 2**i` segundos antes da próxima.
    """
    _validar(tentativas, timeout, backoff)
    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
        dormir(backoff * 2 ** indice)


def _validar(tentativas, timeout, backoff):
    if not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError(f"tentativas deve ser inteiro >= 1: {tentativas!r}")
    if not (_real_finito(timeout) and timeout > 0):
        raise ValueError(f"timeout deve ser real finito > 0: {timeout!r}")
    if not (_real_finito(backoff) and backoff >= 0):
        raise ValueError(f"backoff deve ser real finito >= 0: {backoff!r}")


def _real_finito(valor) -> bool:
    return isinstance(valor, int) or math.isfinite(valor)
