"""Cliente resiliente com retry e backoff exponencial para a API local."""
import math
import time

from fake_api import ErroTemporario

_TRANSITORIAS = (ErroTemporario, TimeoutError)


def _validar(tentativas, timeout, backoff):
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError('tentativas deve ser um inteiro >= 1')
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('timeout deve ser um número real finito > 0')
    if not math.isfinite(backoff) or backoff < 0:
        raise ValueError('backoff deve ser um número real finito >= 0')


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Chame api.get com retry apenas para falhas transitórias."""
    _validar(tentativas, timeout, backoff)
    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except _TRANSITORIAS:
            if indice == tentativas - 1:
                raise
        # Fora do try: exceções de dormir propagam sem serem tratadas como retry.
        dormir(backoff * 2 ** indice)
    raise AssertionError('inalcançável')
