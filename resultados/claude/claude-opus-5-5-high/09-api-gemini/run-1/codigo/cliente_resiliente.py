"""Cliente resiliente para o FakeApiServer, com retry e exponential backoff."""

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
    """Erro definitivo ao falar com a API (ou tentativas esgotadas)."""

    def __init__(self, mensagem: str = "", status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.message = mensagem
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code is None:
            return self.mensagem
        return f"[{self.status_code}] {self.mensagem}"


def _validar_positivo(nome: str, valor: object) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser numérico, recebido {type(valor).__name__}")
    if not math.isfinite(valor) or valor <= 0:
        raise ValueError(f"{nome} deve ser > 0 e finito, recebido {valor!r}")
    return valor


def _status_retentavel(status: int) -> bool:
    return status == 429 or 500 <= status <= 599


class ClienteResiliente:
    """Executa requisições com retry para falhas transitórias."""

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
            raise ValueError(f"max_tentativas deve ser int >= 1, recebido {max_tentativas!r}")
        self.servidor = servidor
        self.max_tentativas = max_tentativas
        self.backoff_base = _validar_positivo("backoff_base", backoff_base)
        self.backoff_fator = _validar_positivo("backoff_fator", backoff_fator)
        self.timeout = _validar_positivo("timeout", timeout)
        self.sleep_fn = sleep_fn

    def get(self, rota: str) -> dict:
        return self.executar("GET", rota)

    def post(self, rota: str, payload: dict) -> dict:
        return self.executar("POST", rota, payload)

    def _delay(self, tentativa: int) -> float:
        return self.backoff_base * (self.backoff_fator ** (tentativa - 1))

    def executar(self, metodo: str, rota: str, payload: dict | None = None) -> dict:
        for tentativa in range(1, self.max_tentativas + 1):
            ultima = tentativa == self.max_tentativas
            try:
                resposta: ApiResponse = self.servidor.requisicao(
                    metodo=metodo, rota=rota, payload=payload, timeout=self.timeout
                )
            except (SimulatedNetworkError, SimulatedTimeoutError) as exc:
                if ultima:
                    raise ApiError(
                        f"{metodo} {rota} falhou após {tentativa} tentativa(s): "
                        f"{type(exc).__name__}: {exc}",
                        status_code=None,
                    ) from exc
                self.sleep_fn(self._delay(tentativa))
                continue

            status = resposta.status_code
            if 200 <= status <= 299:
                return resposta.data

            if not _status_retentavel(status):
                raise ApiError(
                    f"{metodo} {rota} retornou erro não retentável: {resposta.data!r}",
                    status_code=status,
                )

            if ultima:
                raise ApiError(
                    f"{metodo} {rota} falhou após {tentativa} tentativa(s): "
                    f"HTTP {status} {resposta.data!r}",
                    status_code=status,
                )
            self.sleep_fn(self._delay(tentativa))

        # Inalcançável: max_tentativas >= 1 garante retorno ou exceção no laço.
        raise AssertionError("laço de tentativas terminou sem resultado")
