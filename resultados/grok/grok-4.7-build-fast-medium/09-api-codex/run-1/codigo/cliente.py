"""Cliente com retentativas para uma API local de interface get(chave, timeout=)."""
import math
import time

from fake_api import ErroTemporario


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Chama api.get até obter sucesso, repetindo só falhas transitórias.

    tentativas é o máximo de chamadas, timeout vale por tentativa e o atraso
    antes da próxima tentativa de índice i é backoff * 2**i. A última falha
    transitória é propagada sem dormir; outras exceções interrompem na hora.
    """
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

    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
            dormir(backoff * 2**indice)
