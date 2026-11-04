"""Cliente HTTP resiliente para o servidor simulado do exercício."""

import time
from numbers import Number
from typing import Callable

from fake_api import (
    FakeApiServer,
    SimulatedNetworkError,
    SimulatedTimeoutError,
)


class ApiError(Exception):
    """Erro de API, com código HTTP quando houve uma resposta do servidor."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ClienteResiliente:
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
            raise ValueError("max_tentativas deve ser um inteiro maior ou igual a 1")

        for nome, valor in (
            ("backoff_base", backoff_base),
            ("backoff_fator", backoff_fator),
            ("timeout", timeout),
        ):
            if isinstance(valor, bool) or not isinstance(valor, Number) or valor <= 0:
                raise ValueError(f"{nome} deve ser um número maior que zero")

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
        codigos_retentaveis = {429, 500, 502, 503, 504}

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
                    raise ApiError(str(erro)) from erro
                self.sleep_fn(self.backoff_base * (self.backoff_fator ** (tentativa - 1)))
                continue

            status = resposta.status_code
            if 200 <= status < 300:
                return resposta.data

            if status in codigos_retentaveis:
                erro = ApiError(
                    f"Erro HTTP {status}: {resposta.data}", status_code=status
                )
                if tentativa == self.max_tentativas:
                    raise erro
                self.sleep_fn(self.backoff_base * (self.backoff_fator ** (tentativa - 1)))
                continue

            raise ApiError(f"Erro HTTP {status}: {resposta.data}", status_code=status)

        # O laço sempre retorna ou lança uma exceção; este ponto é inalcançável.
        raise RuntimeError("Estado inesperado ao executar requisição")
