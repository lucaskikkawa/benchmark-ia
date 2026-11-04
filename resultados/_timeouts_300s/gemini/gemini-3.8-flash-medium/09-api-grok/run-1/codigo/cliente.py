"""Cliente de pedidos com suporte a retry, backoff e timeout."""

import threading
import time

from loja_api import LojaErroCliente, LojaIndisponivel

__all__ = ["TempoEsgotado", "baixar_pedidos"]


class TempoEsgotado(Exception):
    """Exceção levantada quando o tempo limite de uma chamada é esgotado."""


def _e_loja_indisponivel(exc: BaseException) -> bool:
    """Verifica se a exceção representa indisponibilidade da loja (retentável)."""
    if isinstance(exc, LojaIndisponivel):
        return True
    return any(cls.__name__ == "LojaIndisponivel" for cls in type(exc).__mro__)


def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    """Baixa os pedidos fornecidos por ID, respeitando retry, backoff e timeout."""
    # Validações antes de qualquer chamada
    if type(ids) is not list:
        raise TypeError(f"ids deve ser exatamente list, obtido {type(ids).__name__}")
    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError(f"max_tentativas deve ser int, obtido {type(max_tentativas).__name__}")
    if max_tentativas < 1:
        raise ValueError(f"max_tentativas deve ser >= 1, obtido {max_tentativas}")
    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError(f"backoff_s deve ser int ou float, obtido {type(backoff_s).__name__}")
    if not (backoff_s >= 0):
        raise ValueError(f"backoff_s deve ser >= 0, obtido {backoff_s}")
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError(f"timeout_s deve ser int ou float, obtido {type(timeout_s).__name__}")
    if not (timeout_s > 0):
        raise ValueError(f"timeout_s deve ser > 0, obtido {timeout_s}")

    pedidos: list[dict] = []

    for pedido_id in ids:
        pedido_obtido = None
        for tentativa in range(1, max_tentativas + 1):
            resultado = []
            erro = []
            iniciado = threading.Event()
            concluido = threading.Event()

            def executar():
                iniciado.set()
                try:
                    resultado.append(api.obter_pedido(pedido_id))
                except BaseException as exc:
                    erro.append(exc)
                finally:
                    concluido.set()

            t = threading.Thread(target=executar, daemon=True)
            t.start()
            iniciado.wait()
            sucesso_tempo = concluido.wait(timeout=timeout_s)

            if not sucesso_tempo:
                # Timeout
                if tentativa == max_tentativas:
                    raise TempoEsgotado(f"Timeout ao obter pedido {pedido_id!r}")
                if backoff_s > 0:
                    time.sleep(backoff_s * (2 ** (tentativa - 1)))
                continue

            if erro:
                exc = erro[0]
                if _e_loja_indisponivel(exc):
                    if tentativa == max_tentativas:
                        raise exc
                    if backoff_s > 0:
                        time.sleep(backoff_s * (2 ** (tentativa - 1)))
                    continue
                else:
                    # LojaErroCliente ou outro erro definitivo: propaga imediatamente
                    raise exc

            # Sucesso
            pedido_obtido = resultado[0]
            break

        pedidos.append(pedido_obtido)

    return pedidos
