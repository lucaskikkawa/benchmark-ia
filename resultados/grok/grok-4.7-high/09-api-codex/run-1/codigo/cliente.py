"""Cliente resiliente para a API local descrita em fake_api.py."""

import math
import time

from fake_api import ErroTemporario


def _eh_real_finito(valor):
    """True se valor é int ou float finito. bool não conta como número real."""
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int):
        return True
    if isinstance(valor, float):
        return math.isfinite(valor)
    return False


def buscar_com_retry(
    api,
    chave: str,
    *,
    tentativas: int = 3,
    timeout: float = 1.0,
    backoff: float = 0.1,
    dormir=time.sleep,
) -> dict:
    """Busca `chave` com no máximo `tentativas` chamadas a `api.get`.

    Repete apenas `ErroTemporario` e `TimeoutError` (e subclasses). Depois da
    falha de índice ``i``, e somente se ainda houver tentativa, chama
    ``dormir(backoff * 2**i)``. O timeout é o de cada chamada, não um
    orçamento global. A última falha e qualquer outro erro propagam sem dormir.
    """
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError("tentativas deve ser um inteiro >= 1")
    if not _eh_real_finito(timeout) or timeout <= 0:
        raise ValueError("timeout deve ser um número real finito > 0")
    if not _eh_real_finito(backoff) or backoff < 0:
        raise ValueError("backoff deve ser um número real finito >= 0")

    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
        dormir(backoff * (2 ** indice))
