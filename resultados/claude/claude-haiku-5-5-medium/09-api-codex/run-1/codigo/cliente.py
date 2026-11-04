import math
import time

import fake_api


def _validar(tentativas, timeout, backoff):
    if tentativas < 1:
        raise ValueError('tentativas deve ser inteiro >= 1')
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('timeout deve ser real finito > 0')
    if not math.isfinite(backoff) or backoff < 0:
        raise ValueError('backoff deve ser real finito >= 0')


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    _validar(tentativas, timeout, backoff)
    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (fake_api.ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
        dormir(backoff * 2 ** indice)
