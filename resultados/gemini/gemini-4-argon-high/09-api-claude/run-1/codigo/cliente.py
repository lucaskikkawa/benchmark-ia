"""Cliente HTTP com retry, backoff exponencial e controle de orçamento de espera."""

from __future__ import annotations

import math
import time
from typing import Any, Callable, Iterable

from fake_api import ErroConexao, TempoEsgotado

_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})
_EXCECOES_RETENTAVEIS = (ErroConexao, TempoEsgotado)


class ErroAPI(Exception):
    """Exceção base dos erros do cliente da API."""

    def __init__(self, mensagem: str = "", status: int | None = None) -> None:
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (HTTP 404)."""

    def __init__(self, mensagem: str = "Recurso não encontrado", status: int = 404) -> None:
        super().__init__(mensagem, status=status)


class FalhaPermanente(ErroAPI):
    """Falha definitiva após esgotar tentativas ou orçamento de espera."""

    def __init__(
        self,
        mensagem: str = "Falha permanente",
        tentativas: int = 0,
        status: int | None = None,
    ) -> None:
        super().__init__(mensagem, status=status)
        self.tentativas = tentativas


def _validar_id_usuario(id_usuario: Any) -> int:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id_usuario inválido: {id_usuario!r}")
    return id_usuario


def _extrair_retry_after(headers: dict[str, Any] | None) -> float | None:
    if not headers:
        return None
    for chave, valor in headers.items():
        if isinstance(chave, str) and chave.lower() == "retry-after":
            if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
                return None
            try:
                segundos = float(valor)
            except (ValueError, TypeError):
                return None
            if math.isfinite(segundos) and segundos >= 0:
                return 0.0 if segundos == 0 else segundos
            return None
    return None


class ClienteAPI:
    """Cliente para consulta de usuários com política de retry e backoff."""

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
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0 or math.isnan(timeout):
            raise ValueError("timeout deve ser > 0")
        if (
            isinstance(backoff_base, bool)
            or not isinstance(backoff_base, (int, float))
            or backoff_base < 0
            or math.isnan(backoff_base)
        ):
            raise ValueError("backoff_base deve ser >= 0")
        if (
            isinstance(backoff_max, bool)
            or not isinstance(backoff_max, (int, float))
            or backoff_max < 0
            or math.isnan(backoff_max)
        ):
            raise ValueError("backoff_max deve ser >= 0")
        if orcamento_espera is not None and (
            isinstance(orcamento_espera, bool)
            or not isinstance(orcamento_espera, (int, float))
            or orcamento_espera < 0
            or math.isnan(orcamento_espera)
        ):
            raise ValueError("orcamento_espera deve ser >= 0 ou None")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = float(backoff_base)
        self.backoff_max = float(backoff_max)
        self.timeout = float(timeout)
        self.dormir = dormir
        self.orcamento_espera = float(orcamento_espera) if orcamento_espera is not None else None

    def _calcular_backoff(self, tentativa: int) -> float:
        if self.backoff_base == 0.0 or self.backoff_max == 0.0:
            return 0.0
        try:
            espera = math.ldexp(self.backoff_base, tentativa - 1)
        except OverflowError:
            return self.backoff_max
        return min(self.backoff_max, espera)

    def _calcular_espera(self, tentativa: int, status: int | None, headers: dict[str, Any] | None) -> float:
        if status == 429:
            retry_after = _extrair_retry_after(headers)
            if retry_after is not None:
                return min(self.backoff_max, retry_after)
        return self._calcular_backoff(tentativa)

    def _excede_orcamento(self, espera_acumulada: float, proxima_espera: float) -> bool:
        if self.orcamento_espera is None:
            return False
        return espera_acumulada + proxima_espera > self.orcamento_espera

    def obter_usuario(self, id_usuario: int) -> dict:
        _validar_id_usuario(id_usuario)
        caminho = f"/usuarios/{id_usuario}"
        espera_acumulada = 0.0

        for tentativa in range(1, self.max_tentativas + 1):
            ultimo_erro: Exception | None = None
            ultimo_status: int | None = None
            headers: dict[str, Any] | None = None

            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except _EXCECOES_RETENTAVEIS as exc:
                ultimo_erro = exc
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(f"Usuário {id_usuario} não encontrado", status=404)
                if status not in _STATUS_RETENTAVEIS:
                    raise ErroAPI(f"Erro HTTP {status}", status=status)
                ultimo_status = status
                headers = getattr(resposta, "headers", None)

            if tentativa < self.max_tentativas:
                espera = self._calcular_espera(tentativa, ultimo_status, headers)
                if not self._excede_orcamento(espera_acumulada, espera):
                    espera_acumulada += espera
                    self.dormir(espera)
                    continue

            if ultimo_erro is not None:
                raise FalhaPermanente(
                    f"Falha ao obter usuário {id_usuario} após {tentativa} tentativa(s)",
                    tentativas=tentativa,
                ) from ultimo_erro
            raise FalhaPermanente(
                f"Falha ao obter usuário {id_usuario} após {tentativa} tentativa(s) (status {ultimo_status})",
                tentativas=tentativa,
                status=ultimo_status,
            )

        raise AssertionError("Inalcançável")

    def obter_varios(self, ids: Iterable[int]) -> dict[int, dict | None]:
        ids_validados = [_validar_id_usuario(i) for i in ids]
        ids_unicos = list(dict.fromkeys(ids_validados))

        resultado: dict[int, dict | None] = {}
        for id_usuario in ids_unicos:
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado
