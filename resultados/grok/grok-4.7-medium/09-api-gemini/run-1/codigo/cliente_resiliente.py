"""Cliente HTTP resiliente com retry e exponential backoff."""

from __future__ import annotations

import time
from typing import Callable

from fake_api import (
    ApiResponse,
    FakeApiServer,
    SimulatedNetworkError,
    SimulatedTimeoutError,
)

# Status HTTP transitórios que justificam nova tentativa.
_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})


class ApiError(Exception):
    """Falha definitiva de chamada à API.

    ``status_code`` fica preenchido quando a falha veio de uma resposta HTTP.
    Permanece ``None`` quando a causa foi erro de rede ou timeout.
    """

    def __init__(self, mensagem: str = "", status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.status_code = status_code
        self.mensagem = mensagem


class ClienteResiliente:
    """Executa requisições no ``FakeApiServer`` com retentativas e backoff."""

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

        _exigir_positivo("backoff_base", backoff_base)
        _exigir_positivo("backoff_fator", backoff_fator)
        _exigir_positivo("timeout", timeout)

        self.backoff_base = backoff_base
        self.backoff_fator = backoff_fator
        self.timeout = timeout

        self.servidor = servidor
        self.max_tentativas = max_tentativas
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

            if _sucesso(resposta.status_code):
                return resposta.data

            if resposta.status_code in _STATUS_RETENTAVEIS:
                if tentativa == self.max_tentativas:
                    raise ApiError(_mensagem_http(resposta), status_code=resposta.status_code)
                self.sleep_fn(self._delay(tentativa))
                continue

            raise ApiError(_mensagem_http(resposta), status_code=resposta.status_code)

        # Inalcançável: o laço sempre retorna ou levanta na última tentativa.
        raise ApiError("Tentativas esgotadas", status_code=None)

    def _delay(self, tentativa: int) -> float:
        return self.backoff_base * (self.backoff_fator ** (tentativa - 1))


def _exigir_positivo(nome: str, valor: object) -> None:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser um número > 0")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser um número > 0")


def _sucesso(status_code: int) -> bool:
    return 200 <= status_code <= 299


def _mensagem_http(resposta: ApiResponse) -> str:
    data = resposta.data
    if isinstance(data, dict) and "erro" in data:
        detalhe = data["erro"]
    else:
        detalhe = data
    return f"Erro HTTP {resposta.status_code}: {detalhe}"
