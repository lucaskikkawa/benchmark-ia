"""Cliente resiliente com retry exponencial para API local."""

import math
import time

import fake_api


def _eh_real_finito(valor) -> bool:
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int):
        return True
    return math.isfinite(valor)


def buscar_com_retry(
    api,
    chave: str,
    *,
    tentativas: int = 3,
    timeout: float = 1.0,
    backoff: float = 0.1,
    dormir=time.sleep,
) -> dict:
    """Busca uma chave na API com retry exponencial para erros transitórios."""
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
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
        dormir(backoff * (2**indice))
