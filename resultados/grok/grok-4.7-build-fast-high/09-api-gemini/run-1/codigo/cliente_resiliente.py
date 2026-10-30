"""Cliente de API com retentativas e exponential backoff."""

from __future__ import annotations

import time
from typing import Callable

from fake_api import FakeApiServer, SimulatedNetworkError, SimulatedTimeoutError

__all__ = ["ApiError", "ClienteResiliente"]

# 501 (Not Implemented) e demais 5xx fora desta lista não são transitórios.
_CODIGOS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})


class ApiError(Exception):
    """Falha definitiva de API, com o status HTTP quando a resposta existiu."""

    def __init__(self, message: str = "", status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ClienteResiliente:
    """Executa requisições em um FakeApiServer, repetindo só falhas transitórias."""

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
            raise ValueError("max_tentativas deve ser um int >= 1.")
        _validar_positivo(backoff_base, "backoff_base")
        _validar_positivo(backoff_fator, "backoff_fator")
        _validar_positivo(timeout, "timeout")

        self.servidor = servidor
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_fator = backoff_fator
        self.timeout = timeout
        self.sleep_fn = sleep_fn

    def get(self, rota: str) -> dict:
        return self.executar("GET", rota)

    def post(self, rota: str, payload: dict) -> dict:
        return self.executar("POST", rota, payload)

    def executar(self, metodo: str, rota: str, payload: dict | None = None) -> dict:
        for tentativa in range(1, self.max_tentativas + 1):
            try:
                resposta = self.servidor.requisicao(
                    metodo=metodo,
                    rota=rota,
                    payload=payload,
                    timeout=self.timeout,
                )
            except (SimulatedNetworkError, SimulatedTimeoutError) as erro:
                if tentativa == self.max_tentativas:
                    raise ApiError(str(erro), status_code=None) from erro
                self._aguardar(tentativa)
                continue

            status = resposta.status_code
            if 200 <= status < 300:
                return resposta.data

            if status in _CODIGOS_RETENTAVEIS and tentativa < self.max_tentativas:
                self._aguardar(tentativa)
                continue

            raise ApiError(_descrever_http(status, resposta.data), status_code=status)

        raise ApiError("Falha na requisição.", status_code=None)

    def _aguardar(self, tentativa: int) -> None:
        delay = self.backoff_base * (self.backoff_fator ** (tentativa - 1))
        self.sleep_fn(delay)


def _validar_positivo(valor: object, nome: str) -> None:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser um número maior que zero.")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser um número maior que zero.")


def _descrever_http(status_code: int, data: object) -> str:
    if isinstance(data, dict):
        erro = data.get("erro")
        if isinstance(erro, str) and erro:
            return f"Erro HTTP {status_code}: {erro}"
    return f"Erro HTTP {status_code}"
