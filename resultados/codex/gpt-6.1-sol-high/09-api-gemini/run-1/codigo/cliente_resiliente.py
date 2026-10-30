"""Cliente para a API simulada com retentativas e backoff exponencial."""

import time
from numbers import Number
from typing import Callable

from fake_api import FakeApiServer, SimulatedNetworkError, SimulatedTimeoutError


class ApiError(Exception):
    """Erro de API com código HTTP opcional."""

    def __init__(self, mensagem: str, status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
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
            raise ValueError("max_tentativas deve ser um inteiro maior ou igual a 1.")

        for nome, valor in (
            ("backoff_base", backoff_base),
            ("backoff_fator", backoff_fator),
            ("timeout", timeout),
        ):
            if isinstance(valor, bool) or not isinstance(valor, Number):
                raise ValueError(f"{nome} deve ser um número positivo.")
            try:
                positivo = valor > 0
            except (TypeError, ValueError) as erro:
                raise ValueError(f"{nome} deve ser um número positivo.") from erro
            if not positivo:
                raise ValueError(f"{nome} deve ser um número positivo.")

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
                    raise ApiError(
                        f"Falha após {tentativa} tentativa(s): {erro}"
                    ) from erro
            else:
                status = resposta.status_code
                if 200 <= status < 300:
                    return resposta.data

                retentavel = status == 429 or 500 <= status < 600
                if not retentavel:
                    raise ApiError(f"Erro HTTP {status}: {resposta.data}", status)
                if tentativa == self.max_tentativas:
                    raise ApiError(
                        f"Erro HTTP {status} após {tentativa} tentativa(s): {resposta.data}",
                        status,
                    )

            delay = self.backoff_base * (self.backoff_fator ** (tentativa - 1))
            self.sleep_fn(delay)
