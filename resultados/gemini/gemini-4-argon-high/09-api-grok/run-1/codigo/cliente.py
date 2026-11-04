"""Cliente com retry, backoff exponencial e timeout para LojaAPI."""

import math
import threading
import time
from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """Exceção levantada quando a última tentativa de obter um pedido esgota o timeout."""


def _chamar_com_timeout(api, pedido_id: str, timeout_s: float) -> dict:
    concluido = False
    resultado: dict | None = None
    erro: BaseException | None = None

    def _alvo() -> None:
        nonlocal concluido, resultado, erro
        try:
            resultado = api.obter_pedido(pedido_id)
        except BaseException as exc:
            erro = exc
        finally:
            concluido = True

    thread = threading.Thread(target=_alvo, daemon=True)
    thread.start()
    thread.join(timeout=timeout_s)

    if not concluido:
        raise TempoEsgotado(f"Timeout ao obter pedido {pedido_id!r}")
    if erro is not None:
        raise erro
    return resultado  # type: ignore[return-value]


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente list")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")
    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if math.isnan(backoff_s) or backoff_s < 0:
        raise ValueError("backoff_s deve ser >= 0")
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if math.isnan(timeout_s) or timeout_s <= 0:
        raise ValueError("timeout_s deve ser > 0")

    pedidos: list[dict] = []

    for pedido_id in ids:
        for tentativa in range(1, max_tentativas + 1):
            try:
                pedido = _chamar_com_timeout(api, pedido_id, timeout_s)
                pedidos.append(pedido)
                break
            except LojaErroCliente:
                raise
            except (LojaIndisponivel, TempoEsgotado):
                if tentativa == max_tentativas:
                    raise
                if backoff_s > 0:
                    time.sleep(backoff_s * (2 ** (tentativa - 1)))

    return pedidos
