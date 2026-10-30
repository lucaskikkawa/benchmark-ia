"""Cliente HTTP resiliente com retry e exponential backoff."""

from __future__ import annotations

import time
from collections.abc import Callable

from fake_api import FakeApiServer, SimulatedNetworkError, SimulatedTimeoutError


class ApiError(Exception):
    """Erro definitivo de API, após esgotar retentativas ou em falha não retentável."""

    def __init__(self, message: str = "", status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _numero_positivo(nome: str, valor: object) -> None:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser um número positivo.")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser maior que zero.")


class ClienteResiliente:
    """Executa requisições no FakeApiServer com retry para falhas transitórias."""

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
            raise ValueError("max_tentativas deve ser um inteiro maior ou igual a 1.")
        _numero_positivo("backoff_base", backoff_base)
        _numero_positivo("backoff_fator", backoff_fator)
        _numero_positivo("timeout", timeout)

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
        ultimo_erro: str | None = None
        ultimo_status: int | None = None

        for tentativa in range(1, self.max_tentativas + 1):
            try:
                resposta = self.servidor.requisicao(
                    metodo=metodo,
                    rota=rota,
                    payload=payload,
                    timeout=self.timeout,
                )
            except (SimulatedNetworkError, SimulatedTimeoutError) as exc:
                ultimo_erro = str(exc)
                ultimo_status = None
                if tentativa < self.max_tentativas:
                    self.sleep_fn(self._delay(tentativa))
                    continue
                raise ApiError(ultimo_erro, status_code=None) from exc

            status = resposta.status_code
            if 200 <= status <= 299:
                return resposta.data

            if self._retentavel(status):
                ultimo_erro = f"HTTP {status}: {resposta.data}"
                ultimo_status = status
                if tentativa < self.max_tentativas:
                    self.sleep_fn(self._delay(tentativa))
                    continue
                raise ApiError(ultimo_erro, status_code=ultimo_status)

            raise ApiError(f"HTTP {status}: {resposta.data}", status_code=status)

        raise ApiError(ultimo_erro or "Falha na requisição.", status_code=ultimo_status)

    def _delay(self, tentativa: int) -> float:
        return self.backoff_base * (self.backoff_fator ** (tentativa - 1))

    @staticmethod
    def _retentavel(status: int) -> bool:
        return status == 429 or 500 <= status <= 599
