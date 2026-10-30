"""Cliente com retentativas para a API local."""

import math
import time

import fake_api


def _eh_inteiro_positivo(valor) -> bool:
    """Inteiro >= 1. bool é subclasse de int e não conta como contagem."""
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= 1


def _eh_real_finito(valor) -> bool:
    """Número real finito (int ou float). bool não é real aqui."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    if isinstance(valor, float):
        return math.isfinite(valor)
    return True


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Busca `chave` em `api`, repetindo só falhas transitórias.

    `tentativas` é o máximo de chamadas a `api.get`, incluindo a primeira.
    O timeout é repassado inteiro a cada tentativa. Após a falha de índice
    ``i`` (exceto a última) chama ``dormir(backoff * 2**i)``, mesmo se o
    atraso for zero. A última exceção transitória é propagada sem alteração.
    """
    if not _eh_inteiro_positivo(tentativas):
        raise ValueError("tentativas deve ser um inteiro >= 1")
    if not _eh_real_finito(timeout) or timeout <= 0:
        raise ValueError("timeout deve ser um número real finito > 0")
    if not _eh_real_finito(backoff) or backoff < 0:
        raise ValueError("backoff deve ser um número real finito >= 0")

    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (fake_api.ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
            dormir(backoff * 2**indice)
