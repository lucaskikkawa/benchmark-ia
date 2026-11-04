"""Cliente da LojaAPI com retry, backoff exponencial e timeout por chamada."""

import math
import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """A última tentativa de um id passou de ``timeout_s``."""


_TIMEOUT = object()


def _eh(exc: BaseException, classe: type, nome: str) -> bool:
    # Aceita também a mesma classe vinda de um módulo recarregado.
    return isinstance(exc, classe) or any(c.__name__ == nome for c in type(exc).__mro__)


def _chamar_com_prazo(api, pedido_id, timeout_s: float):
    """Chama ``api.obter_pedido`` numa thread daemon e espera no máximo ``timeout_s``.

    Devolve ``(True, dict)`` no sucesso, ``(False, exceção)`` se a API levantou
    ou ``(False, _TIMEOUT)`` se o prazo acabou. Em timeout a thread é abandonada.
    """
    pronto = threading.Event()
    caixa: list = []

    def alvo():
        try:
            caixa.append((True, api.obter_pedido(pedido_id)))
        except BaseException as exc:  # noqa: BLE001 - repassada ao chamador
            caixa.append((False, exc))
        finally:
            pronto.set()

    threading.Thread(target=alvo, name=f"obter_pedido:{pedido_id!r}", daemon=True).start()
    espera = None if math.isinf(timeout_s) else timeout_s
    if not pronto.wait(espera):
        return False, _TIMEOUT
    return caixa[0]


def _validar_numero(nome: str, valor) -> None:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nome} deve ser int ou float, não {type(valor).__name__}")


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    if type(ids) is not list:
        raise TypeError(f"ids deve ser list, não {type(ids).__name__}")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")
    _validar_numero("backoff_s", backoff_s)
    if not backoff_s >= 0:  # também rejeita NaN
        raise ValueError("backoff_s deve ser >= 0")
    _validar_numero("timeout_s", timeout_s)
    if not timeout_s > 0:  # também rejeita NaN
        raise ValueError("timeout_s deve ser > 0")

    resultado: list[dict] = []
    for pedido_id in ids:
        for i in range(1, max_tentativas + 1):
            ok, valor = _chamar_com_prazo(api, pedido_id, timeout_s)
            if ok:
                resultado.append(valor)
                break
            ultima = i == max_tentativas
            if valor is _TIMEOUT:
                if ultima:
                    raise TempoEsgotado(
                        f"{pedido_id!r}: {i} tentativa(s), prazo de {timeout_s}s esgotado"
                    )
            elif _eh(valor, LojaErroCliente, "LojaErroCliente"):
                raise valor
            elif _eh(valor, LojaIndisponivel, "LojaIndisponivel"):
                if ultima:
                    raise valor
            else:
                raise valor
            if backoff_s > 0:
                time.sleep(backoff_s * 2 ** (i - 1))
    return resultado
