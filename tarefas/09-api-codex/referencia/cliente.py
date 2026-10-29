import math
import time
from fake_api import ErroTemporario


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Busque com timeout por tentativa e backoff exponencial entre falhas transitórias."""
    if tentativas < 1 or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("tentativas e timeout devem ser positivos")
    if not math.isfinite(backoff) or backoff < 0:
        raise ValueError("backoff deve ser finito e não negativo")
    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
            dormir(backoff * 2 ** indice)
