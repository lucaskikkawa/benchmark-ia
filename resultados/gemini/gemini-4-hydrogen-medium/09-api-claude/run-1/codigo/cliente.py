"""Cliente com retry, backoff exponencial, Retry-After e orçamento de espera."""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Iterable
from typing import Any

from fake_api import ErroConexao, TempoEsgotado

_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})
_EXCECOES_RETENTAVEIS = (ErroConexao, TempoEsgotado)


class ErroAPI(Exception):
    """Erro base do cliente da API."""

    def __init__(self, mensagem: str = "", *, status: int | None = None) -> None:
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (HTTP 404)."""


class FalhaPermanente(ErroAPI):
    """Todas as tentativas ou o orçamento de espera foram esgotados."""

    def __init__(
        self,
        mensagem: str = "",
        *,
        tentativas: int,
        status: int | None = None,
    ) -> None:
        super().__init__(mensagem, status=status)
        self.tentativas = tentativas


def _validar_id(id_usuario: Any) -> int:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id_usuario inválido: {id_usuario!r}")
    return id_usuario


def _calcular_backoff(backoff_base: float, backoff_max: float, falha_num: int) -> float:
    """Calcula min(backoff_max, backoff_base * 2 ** (falha_num - 1)) sem overflow."""
    if backoff_base == 0.0 or backoff_max == 0.0:
        return 0.0
    if backoff_base >= backoff_max:
        return float(backoff_max)
    if math.isinf(backoff_max):
        return float(backoff_base) * (2.0 ** (falha_num - 1))

    m_base, e_base = math.frexp(backoff_base)
    m_max, e_max = math.frexp(backoff_max)
    exp_alvo = e_base + (falha_num - 1)

    if exp_alvo > e_max or (exp_alvo == e_max and m_base >= m_max):
        return float(backoff_max)
    return math.ldexp(backoff_base, falha_num - 1)


def _extrair_retry_after(headers: Any) -> float | None:
    """Extrai Retry-After numérico finito >= 0 dos headers (case-insensitive)."""
    if not hasattr(headers, "items"):
        return None
    for chave, valor in headers.items():
        if isinstance(chave, str) and chave.lower() == "retry-after":
            if isinstance(valor, bool):
                return None
            try:
                segundos = float(valor)
            except (TypeError, ValueError):
                return None
            if math.isfinite(segundos) and segundos >= 0.0:
                return segundos
            return None
    return None


class ClienteAPI:
    """Cliente resiliente para a API de usuários."""

    def __init__(
        self,
        api: Any,
        max_tentativas: int = 4,
        backoff_base: float = 0.5,
        backoff_max: float = 8.0,
        timeout: float = 2.0,
        dormir: Callable[[float], Any] = time.sleep,
        orcamento_espera: float | None = None,
    ) -> None:
        if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int) or max_tentativas < 1:
            raise ValueError("max_tentativas deve ser um inteiro >= 1")
        if timeout <= 0:
            raise ValueError("timeout deve ser > 0")
        if backoff_base < 0:
            raise ValueError("backoff_base deve ser >= 0")
        if backoff_max < 0:
            raise ValueError("backoff_max deve ser >= 0")
        if orcamento_espera is not None and orcamento_espera < 0:
            raise ValueError("orcamento_espera deve ser >= 0")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self.dormir = dormir
        self.orcamento_espera = orcamento_espera

    def _calcular_espera(self, falha_num: int, status: int | None, headers: Any) -> float:
        if status == 429:
            retry_after = _extrair_retry_after(headers)
            if retry_after is not None:
                return min(float(self.backoff_max), retry_after)
        return _calcular_backoff(self.backoff_base, self.backoff_max, falha_num)

    def obter_usuario(self, id_usuario: int) -> dict:
        _validar_id(id_usuario)

        caminho = f"/usuarios/{id_usuario}"
        espera_acumulada = 0.0

        for tentativa in range(1, self.max_tentativas + 1):
            erro_capturado: Exception | None = None
            status_capturado: int | None = None
            headers_capturados: Any = None

            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except _EXCECOES_RETENTAVEIS as exc:
                erro_capturado = exc
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(
                        f"Usuário {id_usuario} não encontrado", status=404
                    )
                if status not in _STATUS_RETENTAVEIS:
                    raise ErroAPI(
                        f"Erro HTTP inesperado: {status}", status=status
                    )
                status_capturado = status
                headers_capturados = getattr(resposta, "headers", None)

            if tentativa == self.max_tentativas:
                if erro_capturado is not None:
                    raise FalhaPermanente(
                        f"Falha após {tentativa} tentativa(s): {erro_capturado}",
                        tentativas=tentativa,
                    ) from erro_capturado
                raise FalhaPermanente(
                    f"Falha após {tentativa} tentativa(s): HTTP {status_capturado}",
                    tentativas=tentativa,
                    status=status_capturado,
                )

            espera = self._calcular_espera(tentativa, status_capturado, headers_capturados)
            if (
                self.orcamento_espera is not None
                and espera_acumulada + espera > self.orcamento_espera
            ):
                if erro_capturado is not None:
                    raise FalhaPermanente(
                        f"Orçamento de espera excedido após {tentativa} tentativa(s)",
                        tentativas=tentativa,
                    ) from erro_capturado
                raise FalhaPermanente(
                    f"Orçamento de espera excedido após {tentativa} tentativa(s): HTTP {status_capturado}",
                    tentativas=tentativa,
                    status=status_capturado,
                )

            self.dormir(espera)
            espera_acumulada += espera

        raise AssertionError("Estado inalcançável")  # pragma: no cover

    def obter_varios(self, ids: Iterable[int]) -> dict[int, dict | None]:
        ids_unicos: list[int] = []
        vistos: set[int] = set()
        for id_usuario in ids:
            _validar_id(id_usuario)
            if id_usuario not in vistos:
                vistos.add(id_usuario)
                ids_unicos.append(id_usuario)

        resultado: dict[int, dict | None] = {}
        for id_usuario in ids_unicos:
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado
