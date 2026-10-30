"""Cliente com retry, backoff e timeout para API de usuários simulada."""

import math
import time
from typing import Any

from fake_api import ErroConexao, TempoEsgotado

STATUS_RETENTAVEIS = {429, 500, 502, 503, 504}


class ErroAPI(Exception):
    """Base dos erros do cliente."""

    def __init__(self, *args, status: int | None = None):
        if status is None and len(args) >= 2 and isinstance(args[-1], int) and not isinstance(args[-1], bool):
            status = args[-1]
        super().__init__(*args)
        if status is not None:
            self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (404)."""

    def __init__(self, *args, status: int = 404):
        super().__init__(*args, status=status)


class FalhaPermanente(ErroAPI):
    """Desistência das tentativas do cliente."""

    def __init__(
        self,
        *args,
        tentativas: int | None = None,
        status: int | None = None,
    ):
        if tentativas is None:
            if len(args) >= 2 and isinstance(args[1], int) and not isinstance(args[1], bool):
                tentativas = args[1]
            elif len(args) == 1 and isinstance(args[0], int) and not isinstance(args[0], bool):
                tentativas = args[0]
            else:
                tentativas = 0
        super().__init__(*args, status=status)
        self.tentativas = tentativas


def _calcular_backoff(backoff_base: float, backoff_max: float, n: int) -> float:
    """Calcula min(backoff_max, backoff_base * 2 ** (n - 1)) sem overflow."""
    if backoff_base <= 0:
        return 0.0
    exp = n - 1
    if exp <= 0:
        return min(float(backoff_max), float(backoff_base))
    try:
        val = math.ldexp(float(backoff_base), exp)
    except OverflowError:
        val = float("inf")
    return min(float(backoff_max), val)


def _extrair_retry_after(headers: Any) -> float | None:
    """Extrai e valida valor de Retry-After dos headers."""
    if headers is None:
        return None
    items = None
    if hasattr(headers, "items"):
        items = headers.items()
    elif isinstance(headers, (list, tuple)):
        items = headers
    if items is None:
        return None

    for item in items:
        try:
            k, v = item
        except (ValueError, TypeError):
            continue
        if isinstance(k, str) and k.lower() == "retry-after":
            if isinstance(v, bool):
                return None
            try:
                val = float(v)
                if math.isfinite(val) and val >= 0:
                    return val
                return None
            except (ValueError, TypeError, OverflowError):
                return None
    return None


class ClienteAPI:
    def __init__(
        self,
        api,
        max_tentativas: int = 4,
        backoff_base: float = 0.5,
        backoff_max: float = 8.0,
        timeout: float = 2.0,
        dormir=time.sleep,
        orcamento_espera: float | None = None,
    ):
        if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int) or max_tentativas < 1:
            raise ValueError(f"max_tentativas deve ser um inteiro >= 1: {max_tentativas!r}")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or math.isnan(timeout) or timeout <= 0:
            raise ValueError(f"timeout deve ser um número > 0: {timeout!r}")
        if (
            isinstance(backoff_base, bool)
            or not isinstance(backoff_base, (int, float))
            or math.isnan(backoff_base)
            or backoff_base < 0
        ):
            raise ValueError(f"backoff_base deve ser um número >= 0: {backoff_base!r}")
        if (
            isinstance(backoff_max, bool)
            or not isinstance(backoff_max, (int, float))
            or math.isnan(backoff_max)
            or backoff_max < 0
        ):
            raise ValueError(f"backoff_max deve ser um número >= 0: {backoff_max!r}")
        if orcamento_espera is not None:
            if (
                isinstance(orcamento_espera, bool)
                or not isinstance(orcamento_espera, (int, float))
                or math.isnan(orcamento_espera)
                or orcamento_espera < 0
            ):
                raise ValueError(f"orcamento_espera deve ser um número >= 0 ou None: {orcamento_espera!r}")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self.dormir = dormir
        self.orcamento_espera = orcamento_espera

    def obter_usuario(self, id_usuario: int) -> dict:
        if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
            raise ValueError(f"id_usuario deve ser um inteiro >= 1: {id_usuario!r}")

        soma_esperas = 0.0
        tentativas = 0
        ultima_excecao: Exception | None = None
        ultimo_status: int | None = None
        ultimos_headers: Any = None

        while tentativas < self.max_tentativas:
            tentativas += 1
            try:
                resp = self.api.requisitar("GET", f"/usuarios/{id_usuario}", timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as erro:
                ultima_excecao = erro
                ultimo_status = None
                ultimos_headers = None
            else:
                status = resp.status
                if status == 200:
                    return resp.corpo
                if status == 404:
                    raise NaoEncontrado(f"Usuário {id_usuario} não encontrado", status=status)
                if status not in STATUS_RETENTAVEIS:
                    raise ErroAPI(f"Erro na API com status {status}", status=status)

                ultima_excecao = None
                ultimo_status = status
                ultimos_headers = getattr(resp, "headers", None)

            # Não espera após a última tentativa
            if tentativas >= self.max_tentativas:
                break

            # Calcula espera antes da próxima tentativa
            if ultimo_status == 429:
                espera_header = _extrair_retry_after(ultimos_headers)
                if espera_header is not None:
                    espera = min(float(self.backoff_max), espera_header)
                else:
                    espera = _calcular_backoff(self.backoff_base, self.backoff_max, tentativas)
            else:
                espera = _calcular_backoff(self.backoff_base, self.backoff_max, tentativas)

            # Orçamento de espera
            if self.orcamento_espera is not None and (soma_esperas + espera) > self.orcamento_espera:
                break

            soma_esperas += espera
            self.dormir(espera)

        if ultima_excecao is not None:
            raise FalhaPermanente(
                f"Falha permanente após {tentativas} tentativa(s)",
                tentativas=tentativas,
            ) from ultima_excecao
        else:
            raise FalhaPermanente(
                f"Falha permanente após {tentativas} tentativa(s) com status {ultimo_status}",
                tentativas=tentativas,
                status=ultimo_status,
            ) from None

    def obter_varios(self, ids) -> dict[int, dict | None]:
        lista_ids = list(ids)
        for id_val in lista_ids:
            if isinstance(id_val, bool) or not isinstance(id_val, int) or id_val < 1:
                raise ValueError(f"id_usuario inválido: {id_val!r}")

        resultado: dict[int, dict | None] = {}
        for id_val in dict.fromkeys(lista_ids):
            try:
                resultado[id_val] = self.obter_usuario(id_val)
            except NaoEncontrado:
                resultado[id_val] = None
        return resultado
