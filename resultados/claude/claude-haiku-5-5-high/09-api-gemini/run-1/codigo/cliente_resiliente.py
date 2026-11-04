import time
from typing import Callable

from fake_api import FakeApiServer, SimulatedNetworkError, SimulatedTimeoutError


class ApiError(Exception):
    """Erro definitivo ou esgotamento de tentativas em uma requisição à API."""

    def __init__(self, mensagem: str, status_code: int | None = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


def _validar_positivo(nome: str, valor: float) -> None:
    # `not valor > 0` também rejeita NaN; bool é excluído mesmo sendo subclasse de int
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not valor > 0:
        raise ValueError(f"{nome} deve ser um número maior que zero.")


def _status_retentavel(status_code: int) -> bool:
    return status_code == 429 or 500 <= status_code <= 599


class ClienteResiliente:
    """Cliente para o servidor de API com retry e exponential backoff."""

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
            except (SimulatedNetworkError, SimulatedTimeoutError) as erro:
                motivo, status_code, causa = str(erro), None, erro
            else:
                if 200 <= resposta.status_code < 300:
                    return resposta.data
                if not _status_retentavel(resposta.status_code):
                    raise ApiError(
                        f"{metodo} {rota} falhou com HTTP {resposta.status_code}.",
                        status_code=resposta.status_code,
                    )
                motivo, status_code, causa = f"HTTP {resposta.status_code}", resposta.status_code, None

            if tentativa == self.max_tentativas:
                raise ApiError(
                    f"{metodo} {rota} falhou após {tentativa} tentativa(s): {motivo}",
                    status_code=status_code,
                ) from causa

            delay = self.backoff_base * (self.backoff_fator ** (tentativa - 1))
            self.sleep_fn(delay)
