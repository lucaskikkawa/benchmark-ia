"""Cliente HTTP resiliente com retry e exponential backoff."""

from __future__ import annotations

import numbers
import time
from collections.abc import Callable

from fake_api import (
    ApiResponse,
    FakeApiServer,
    SimulatedNetworkError,
    SimulatedTimeoutError,
)

# 501 (Not Implemented) fica de fora: é definitivo. Os demais 5xx listados
# no enunciado, mais 429, são transitórios.
_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})


class ApiError(Exception):
    """Falha definitiva ou esgotamento das tentativas de chamada à API."""

    status_code: int | None = None

    def __init__(self, mensagem: str = "", status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.status_code = status_code


class ClienteResiliente:
    """Executa requisições no FakeApiServer com retentativas e backoff."""

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
            raise ValueError("max_tentativas deve ser um inteiro >= 1")
        _validar_positivo("backoff_base", backoff_base)
        _validar_positivo("backoff_fator", backoff_fator)
        _validar_positivo("timeout", timeout)

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
            except (SimulatedNetworkError, SimulatedTimeoutError) as exc:
                if tentativa == self.max_tentativas:
                    raise ApiError(str(exc), status_code=None) from exc
                self.sleep_fn(self._delay(tentativa))
                continue

            if 200 <= resposta.status_code < 300:
                return resposta.data

            if resposta.status_code in _STATUS_RETENTAVEIS:
                if tentativa == self.max_tentativas:
                    raise ApiError(
                        _mensagem_http(resposta),
                        status_code=resposta.status_code,
                    )
                self.sleep_fn(self._delay(tentativa))
                continue

            raise ApiError(
                _mensagem_http(resposta),
                status_code=resposta.status_code,
            )

        raise ApiError("Tentativas esgotadas", status_code=None)

    def _delay(self, tentativa: int) -> float:
        return self.backoff_base * (self.backoff_fator ** (tentativa - 1))


def _validar_positivo(nome: str, valor: object) -> None:
    if isinstance(valor, bool) or not isinstance(valor, numbers.Real):
        raise ValueError(f"{nome} deve ser um número positivo")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser um número positivo")


def _mensagem_http(resposta: ApiResponse) -> str:
    dados = resposta.data
    if isinstance(dados, dict) and "erro" in dados:
        return str(dados["erro"])
    return f"HTTP {resposta.status_code}"
