import time
from typing import Callable

from fake_api import FakeApiServer, SimulatedNetworkError, SimulatedTimeoutError


STATUS_RETENTAVEIS = {429, 500, 502, 503, 504}


class ApiError(Exception):
    """Erro retornado pelo cliente quando a requisição falha definitivamente."""

    def __init__(self, mensagem: str, status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


def _eh_numero(valor: object) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


class ClienteResiliente:
    """Cliente com retry e exponential backoff para o FakeApiServer."""

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
        if not _eh_numero(backoff_base) or backoff_base <= 0:
            raise ValueError("backoff_base deve ser numérico e maior que 0.")
        if not _eh_numero(backoff_fator) or backoff_fator <= 0:
            raise ValueError("backoff_fator deve ser numérico e maior que 0.")
        if not _eh_numero(timeout) or timeout <= 0:
            raise ValueError("timeout deve ser numérico e maior que 0.")

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
                        f"Falha de rede/timeout em {metodo} {rota} após {tentativa} tentativa(s): {erro}",
                        status_code=None,
                    ) from erro
                self._aguardar(tentativa)
                continue

            status = resposta.status_code
            if 200 <= status < 300:
                return resposta.data

            if status in STATUS_RETENTAVEIS:
                if tentativa == self.max_tentativas:
                    raise ApiError(
                        f"HTTP {status} em {metodo} {rota} após {tentativa} tentativa(s).",
                        status_code=status,
                    )
                self._aguardar(tentativa)
                continue

            raise ApiError(
                f"HTTP {status} em {metodo} {rota}: erro definitivo, sem retry.",
                status_code=status,
            )

        # Inalcançável: o laço sempre retorna ou levanta ApiError.
        raise ApiError(f"Nenhuma tentativa executada em {metodo} {rota}.")

    def _aguardar(self, tentativa: int) -> None:
        delay = self.backoff_base * (self.backoff_fator ** (tentativa - 1))
        self.sleep_fn(delay)
