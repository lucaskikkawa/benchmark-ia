"""Cliente HTTP com retry, backoff exponencial, Retry-After, timeout e orçamento de espera."""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Iterable
from typing import Any

from fake_api import ErroConexao, TempoEsgotado

_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})
_EXCECOES_RETENTAVEIS = (ErroConexao, TempoEsgotado)


class ErroAPI(Exception):
    """Base dos erros do cliente da API."""

    def __init__(self, mensagem: str = "", *, status: int | None = None) -> None:
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (HTTP 404)."""

    def __init__(self, mensagem: str = "Recurso não encontrado", *, status: int = 404) -> None:
        super().__init__(mensagem, status=status)


class FalhaPermanente(ErroAPI):
    """Erro levantado quando todas as tentativas ou o orçamento de espera se esgotam."""

    def __init__(
        self,
        mensagem: str = "Falha permanente após tentativas esgotadas",
        *,
        tentativas: int,
        status: int | None = None,
    ) -> None:
        super().__init__(mensagem, status=status)
        self.tentativas = tentativas


def _validar_id(id_usuario: Any) -> int:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id de usuário inválido: {id_usuario!r}")
    return id_usuario


def _extrair_retry_after(headers: Any) -> float | None:
    if not headers or not hasattr(headers, "items"):
        return None
    for chave, valor in headers.items():
        if isinstance(chave, str) and chave.lower() == "retry-after":
            if isinstance(valor, bool):
                return None
            try:
                segundos = float(valor)
            except (TypeError, ValueError):
                return None
            if math.isfinite(segundos) and segundos >= 0:
                return 0.0 if segundos == 0 else segundos
            return None
    return None


class ClienteAPI:
    """Cliente com retry, backoff exponencial e orçamento de espera."""

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
        if isinstance(timeout, bool) or not (timeout > 0):
            raise ValueError("timeout deve ser > 0")
        if isinstance(backoff_base, bool) or not (backoff_base >= 0):
            raise ValueError("backoff_base deve ser >= 0")
        if isinstance(backoff_max, bool) or not (backoff_max >= 0):
            raise ValueError("backoff_max deve ser >= 0")
        if orcamento_espera is not None and (
            isinstance(orcamento_espera, bool) or not (orcamento_espera >= 0)
        ):
            raise ValueError("orcamento_espera deve ser None ou >= 0")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self.dormir = dormir
        self.orcamento_espera = orcamento_espera

    def _calcular_backoff(self, tentativa: int) -> float:
        if self.backoff_base == 0 or self.backoff_max == 0:
            return 0.0
        try:
            valor = math.ldexp(self.backoff_base, tentativa - 1)
        except OverflowError:
            return float(self.backoff_max)
        return min(float(self.backoff_max), valor)

    def _calcular_espera(self, tentativa: int, status: int | None, headers: Any) -> float:
        if status == 429:
            retry_after = _extrair_retry_after(headers)
            if retry_after is not None:
                return min(float(self.backoff_max), retry_after)
        return self._calcular_backoff(tentativa)

    def obter_usuario(self, id_usuario: int) -> dict:
        _validar_id(id_usuario)

        caminho = f"/usuarios/{id_usuario}"
        espera_acumulada = 0.0
        tentativas = 0
        ultimo_erro: Exception | None = None
        ultimo_status: int | None = None

        for tentativa in range(1, self.max_tentativas + 1):
            tentativas = tentativa
            ultimo_erro = None
            ultimo_status = None
            headers = None

            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except _EXCECOES_RETENTAVEIS as erro:
                ultimo_erro = erro
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(f"Usuário {id_usuario} não encontrado", status=404)
                if status not in _STATUS_RETENTAVEIS:
                    raise ErroAPI(
                        f"Erro HTTP {status} ao obter usuário {id_usuario}",
                        status=status,
                    )
                ultimo_status = status
                headers = getattr(resposta, "headers", None)

            if tentativa == self.max_tentativas:
                break

            espera = self._calcular_espera(tentativa, ultimo_status, headers)
            if (
                self.orcamento_espera is not None
                and espera_acumulada + espera > self.orcamento_espera
            ):
                break

            self.dormir(espera)
            espera_acumulada += espera

        if ultimo_erro is not None:
            raise FalhaPermanente(
                f"Falha ao obter usuário {id_usuario} após {tentativas} tentativa(s): {ultimo_erro}",
                tentativas=tentativas,
            ) from ultimo_erro

        raise FalhaPermanente(
            f"Falha HTTP {ultimo_status} ao obter usuário {id_usuario} após {tentativas} tentativa(s)",
            tentativas=tentativas,
            status=ultimo_status,
        )

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
