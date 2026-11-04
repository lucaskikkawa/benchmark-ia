"""Cliente HTTP resiliente com retentativa e backoff exponencial."""

from __future__ import annotations

import time
from typing import Callable

from fake_api import FakeApiServer, SimulatedNetworkError, SimulatedTimeoutError


# Códigos HTTP transitórios: 429 e a faixa 5xx.
_STATUS_RETENTAVEIS_EXATOS = {429}


class ApiError(Exception):
    """Erro definitivo de API após falha não retentável ou esgotamento das tentativas."""

    def __init__(self, mensagem: str = "", status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.status_code = status_code


def _numero_positivo(valor: object) -> bool:
    """True se valor for int/float (exceto bool) e estritamente positivo."""
    if type(valor) is bool or not isinstance(valor, (int, float)):
        return False
    return valor > 0


def _status_retentavel(status_code: int) -> bool:
    return status_code in _STATUS_RETENTAVEIS_EXATOS or 500 <= status_code <= 599


def _mensagem_http(status_code: int, data: object) -> str:
    if isinstance(data, dict) and "erro" in data:
        return f"HTTP {status_code}: {data['erro']}"
    return f"HTTP {status_code}: {data}"


class ClienteResiliente:
    """Executa requisições no FakeApiServer com retry e exponential backoff."""

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
        if not _numero_positivo(backoff_base):
            raise ValueError("backoff_base deve ser um número > 0")
        if not _numero_positivo(backoff_fator):
            raise ValueError("backoff_fator deve ser um número > 0")
        if not _numero_positivo(timeout):
            raise ValueError("timeout deve ser um número > 0")

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
        """Envia a requisição, repetindo apenas falhas transitórias."""
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
                self._aguardar(tentativa)
                continue

            status = resposta.status_code
            if 200 <= status <= 299:
                return resposta.data

            if _status_retentavel(status):
                if tentativa == self.max_tentativas:
                    raise ApiError(
                        _mensagem_http(status, resposta.data),
                        status_code=status,
                    )
                self._aguardar(tentativa)
                continue

            raise ApiError(_mensagem_http(status, resposta.data), status_code=status)

        raise ApiError("Número de tentativas esgotado", status_code=None)

    def _aguardar(self, tentativa: int) -> None:
        delay = self.backoff_base * (self.backoff_fator ** (tentativa - 1))
        self.sleep_fn(delay)
