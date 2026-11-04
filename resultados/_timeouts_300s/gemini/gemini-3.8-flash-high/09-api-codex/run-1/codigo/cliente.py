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
    """Busca um valor na API com política de repetição exponencial."""
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError("tentativas deve ser um inteiro >= 1")
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("timeout deve ser um número real finito > 0")
    if (
        isinstance(backoff, bool)
        or not isinstance(backoff, (int, float))
        or not math.isfinite(backoff)
        or backoff < 0
    ):
        raise ValueError("backoff deve ser um número real finito >= 0")

    for tentativa in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (fake_api.ErroTemporario, TimeoutError):
            if tentativa == tentativas - 1:
                raise
        dormir(backoff * (2**tentativa))
