import threading
import time
from loja_api import LojaErroCliente, LojaIndisponivel


class TempoEsgotado(Exception):
    """Exceção levantada quando todas as tentativas esgotam por timeout."""
    pass


def _is_erro_cliente(exc: BaseException) -> bool:
    if isinstance(exc, LojaErroCliente):
        return True
    return any(cls.__name__ == "LojaErroCliente" for cls in type(exc).__mro__)


def _is_indisponivel(exc: BaseException) -> bool:
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
    # Validação dos argumentos antes de qualquer chamada
    if type(ids) is not list:
        raise TypeError("ids deve ser exatamente do tipo list")

    if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int):
        raise TypeError("max_tentativas deve ser int")
    if max_tentativas < 1:
        raise ValueError("max_tentativas deve ser >= 1")

    if isinstance(backoff_s, bool) or not isinstance(backoff_s, (int, float)):
        raise TypeError("backoff_s deve ser int ou float")
    if backoff_s < 0:
        raise ValueError("backoff_s deve ser >= 0")

    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (int, float)):
        raise TypeError("timeout_s deve ser int ou float")
    if timeout_s <= 0:
        raise ValueError("timeout_s deve ser > 0")

    if not ids:
        return []

    resultados: list[dict] = []

    for pedido_id in ids:
        for i in range(1, max_tentativas + 1):
            started = threading.Event()
            done = threading.Event()
            res = None
            err = None

            def worker() -> None:
                nonlocal res, err
                started.set()
                try:
                    res = api.obter_pedido(pedido_id)
                except BaseException as exc:
                    err = exc
                finally:
                    done.set()

            t = threading.Thread(target=worker, daemon=True)
            t.start()
            started.wait()

            timed_out = not done.wait(timeout=timeout_s)

            if timed_out:
                if i == max_tentativas:
                    raise TempoEsgotado()
                if backoff_s > 0:
                    time.sleep(backoff_s * (2 ** (i - 1)))
                continue

            if err is not None:
                if _is_erro_cliente(err):
                    raise err
                if _is_indisponivel(err):
                    if i == max_tentativas:
                        raise err
                    if backoff_s > 0:
                        time.sleep(backoff_s * (2 ** (i - 1)))
                    continue
                # Outras exceções não retentáveis propagam na hora
                raise err

            # Sucesso
            resultados.append(res)
            break

    return resultados
