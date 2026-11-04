"""Cliente resiliente com retry e backoff exponencial para API local."""
import math
import time

import fake_api


def buscar_com_retry(
    api,
    chave: str,
    *,
    tentativas: int = 3,
    timeout: float = 1.0,
    backoff: float = 0.1,
    dormir=time.sleep,
) -> dict:
    """Busca ``chave`` em ``api`` com repetição em falhas transitórias."""
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError("tentativas deve ser um inteiro >= 1")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not (math.isfinite(timeout) and timeout > 0):
        raise ValueError("timeout deve ser um número real finito > 0")
    if isinstance(backoff, bool) or not isinstance(backoff, (int, float)) or not (math.isfinite(backoff) and backoff >= 0):
        raise ValueError("backoff deve ser um número real finito >= 0")

    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (fake_api.ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
        dormir(backoff * 2**indice)
