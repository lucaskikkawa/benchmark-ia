"""Cliente com retentativa para uma API local com a interface get(chave, timeout=)."""
import math
import time

from fake_api import ErroTemporario


def _real_finito(valor) -> bool:
    """Inteiro (exceto bool) é finito; float precisa passar por math.isfinite."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    if isinstance(valor, float) and not math.isfinite(valor):
        return False
    return True


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Chama api.get até obter sucesso, repetindo só falhas transitórias.

    tentativas é o máximo de chamadas. Entre falhas de índice i espera
    backoff * 2**i via dormir, inclusive quando o atraso é zero. Não dorme
    após sucesso nem após a última falha.
    """
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError("tentativas deve ser um inteiro >= 1")
    if not _real_finito(timeout) or timeout <= 0:
        raise ValueError("timeout deve ser um número real finito > 0")
    if not _real_finito(backoff) or backoff < 0:
        raise ValueError("backoff deve ser um número real finito >= 0")

    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
        # Fora do except: falha de dormir não é falha de api.get e não é retentada.
        dormir(backoff * 2**indice)
