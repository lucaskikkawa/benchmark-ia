import math
import time
import fake_api

__all__ = ["buscar_com_retry"]


def buscar_com_retry(
    api,
    chave: str,
    *,
    tentativas: int = 3,
    timeout: float = 1.0,
    backoff: float = 0.1,
    dormir=time.sleep,
) -> dict:
    """Busca uma chave na API com repetição para falhas transitórias.

    Parâmetros:
        api: Objeto que fornece o método `get(chave, *, timeout)`.
        chave: Chave a ser consultada.
        tentativas: Número máximo de chamadas (>= 1).
        timeout: Limite de tempo por tentativa em segundos (> 0, finito).
        backoff: Tempo base de espera para recuo exponencial em segundos (>= 0, finito).
        dormir: Função de espera, chamada com os segundos calculados.

    Retorna:
        dict retornado pela API sem transformações.
    """
    if isinstance(tentativas, bool) or not isinstance(tentativas, int) or tentativas < 1:
        raise ValueError("tentativas deve ser um número inteiro >= 1")

    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or (isinstance(timeout, float) and not math.isfinite(timeout))
        or timeout <= 0
    ):
        raise ValueError("timeout deve ser um número real finito > 0")

    if (
        isinstance(backoff, bool)
        or not isinstance(backoff, (int, float))
        or (isinstance(backoff, float) and not math.isfinite(backoff))
        or backoff < 0
    ):
        raise ValueError("backoff deve ser um número real finito >= 0")

    for indice in range(tentativas):
        try:
            return api.get(chave, timeout=timeout)
        except (fake_api.ErroTemporario, TimeoutError):
            if indice == tentativas - 1:
                raise
        dormir(backoff * (2**indice))
