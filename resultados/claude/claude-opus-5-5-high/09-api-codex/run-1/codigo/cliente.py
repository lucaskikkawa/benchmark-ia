"""Cliente com retry e backoff exponencial para APIs com interface ``get``."""
import math
import time

from fake_api import ErroTemporario

_TRANSITORIAS = (ErroTemporario, TimeoutError)


def _finito(valor) -> bool:
    if isinstance(valor, int):
        return True
    return math.isfinite(valor)


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Chame ``api.get`` até ``tentativas`` vezes, repetindo só falhas transitórias."""
    if tentativas < 1:
        raise ValueError(f'tentativas deve ser >= 1, recebido {tentativas!r}')
    if not _finito(timeout) or not timeout > 0:
        raise ValueError(f'timeout deve ser finito e > 0, recebido {timeout!r}')
    if not _finito(backoff) or not backoff >= 0:
        raise ValueError(f'backoff deve ser finito e >= 0, recebido {backoff!r}')

    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except _TRANSITORIAS:
            if indice == tentativas - 1:
                raise
        # Fora do bloco except: erros de ``dormir`` propagam sem serem tratados
        # como falhas da API.
        dormir(backoff * 2 ** indice)
    raise AssertionError('inalcançável')
