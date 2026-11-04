"""Cliente resiliente para API local com retry e backoff exponencial."""
import math
from pathlib import Path
import sys
import time

_dir = str(Path(__file__).resolve().parent)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import fake_api
from fake_api import ErroPermanente, ErroTemporario


def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    """Busca uma chave na API com repetições em caso de falhas transitórias.

    Parâmetros:
        api: Objeto com método get(chave, *, timeout).
        chave: Chave a ser buscada.
        tentativas: Número máximo de chamadas (>= 1).
        timeout: Limite de tempo por tentativa em segundos (> 0).
        backoff: Intervalo base de espera em segundos (>= 0).
        dormir: Função de espera (padrão time.sleep).

    Retorna:
        Objeto retornado por api.get(chave, timeout=timeout).
    """
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError("tentativas deve ser um inteiro >= 1")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout deve ser um número real finito > 0")
    if isinstance(backoff, bool) or not isinstance(backoff, (int, float)) or not math.isfinite(backoff) or backoff < 0:
        raise ValueError("backoff deve ser um número real finito >= 0")

    for tentativa in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (fake_api.ErroTemporario, TimeoutError):
            if tentativa == tentativas - 1:
                raise
        dormir(backoff * (2 ** tentativa))
