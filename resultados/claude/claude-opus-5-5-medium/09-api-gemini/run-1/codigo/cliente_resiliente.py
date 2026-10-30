"""Cliente resiliente de API com retry e exponential backoff."""

from __future__ import annotations

import math
import time
from typing import Callable

from fake_api import (
    ApiResponse,
    FakeApiServer,
    SimulatedNetworkError,
    SimulatedTimeoutError,
)


class ApiError(Exception):
    """Erro definitivo (ou por esgotamento de tentativas) ao chamar a API."""

    def __init__(self, mensagem: str = "", status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.message = mensagem
        self.status_code = status_code


def _validar_positivo(nome: str, valor: object) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser numérico, recebido {valor!r}")
    if math.isnan(valor) or valor <= 0:
        raise ValueError(f"{nome} deve ser > 0, recebido {valor!r}")
    return valor


class ClienteResiliente:
    """Cliente que repete requisições em falhas transitórias com backoff exponencial."""

    ERROS_TRANSITORIOS = (SimulatedNetworkError, SimulatedTimeoutError)

    def __init__(
        self,
        servidor: FakeApiServer,
        max_tentativas: int = 3,
        backoff_base: float = 0.05,
        backoff_fator: float = 2.0,
        timeout: float = 2.0,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        if type(max_tentativas) is not int or max_tentativas < 1:
            raise ValueError(
                f"max_tentativas deve ser um inteiro >= 1, recebido {max_tentativas!r}"
            )
        self.backoff_base = _validar_positivo("backoff_base", backoff_base)
        self.backoff_fator = _validar_positivo("backoff_fator", backoff_fator)
        self.timeout = _validar_positivo("timeout", timeout)
        if not callable(sleep_fn):
            raise ValueError("sleep_fn deve ser chamável")

        self.servidor = servidor
        self.max_tentativas = max_tentativas
        self.sleep_fn = sleep_fn

    @staticmethod
    def _status_retentavel(status: int) -> bool:
        return status == 429 or 500 <= status <= 599

    def _calcular_delay(self, tentativa: int) -> float:
        return self.backoff_base * (self.backoff_fator ** (tentativa - 1))

    def get(self, rota: str) -> dict:
        return self.executar("GET", rota)

    def post(self, rota: str, payload: dict) -> dict:
        return self.executar("POST", rota, payload)

    def executar(self, metodo: str, rota: str, payload: dict | None = None) -> dict:
        for tentativa in range(1, self.max_tentativas + 1):
            try:
                resposta: ApiResponse = self.servidor.requisicao(
                    metodo=metodo, rota=rota, payload=payload, timeout=self.timeout
                )
            except self.ERROS_TRANSITORIOS as exc:
                if tentativa >= self.max_tentativas:
                    raise ApiError(
                        f"{metodo} {rota} falhou após {tentativa} tentativa(s): "
                        f"{type(exc).__name__}: {exc}",
                        status_code=None,
                    ) from exc
                self.sleep_fn(self._calcular_delay(tentativa))
                continue

            status = resposta.status_code
            if 200 <= status <= 299:
                return resposta.data

            if not self._status_retentavel(status):
                raise ApiError(
                    f"{metodo} {rota} retornou erro definitivo HTTP {status}",
                    status_code=status,
                )

            if tentativa >= self.max_tentativas:
                raise ApiError(
                    f"{metodo} {rota} falhou após {tentativa} tentativa(s): HTTP {status}",
                    status_code=status,
                )
            self.sleep_fn(self._calcular_delay(tentativa))

        # Inalcançável: max_tentativas >= 1 garante retorno ou exceção no laço.
        raise ApiError(f"{metodo} {rota} falhou")  # pragma: no cover
