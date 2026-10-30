"""Cliente HTTP com retry, backoff exponencial e orçamento de espera."""

from __future__ import annotations

import math
import time
from typing import Any, Callable, Iterable

from fake_api import ErroConexao, TempoEsgotado

_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})


class ErroAPI(Exception):
    """Base dos erros levantados pelo cliente da API."""

    def __init__(self, mensagem: str = "", status: int | None = None) -> None:
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (HTTP 404)."""

    def __init__(self, mensagem: str = "Recurso não encontrado", status: int = 404) -> None:
        super().__init__(mensagem, status=status)


class FalhaPermanente(ErroAPI):
    """Tentativas ou orçamento de espera esgotados."""

    def __init__(
        self,
        mensagem: str = "Falha permanente após retentativas",
        tentativas: int = 0,
        status: int | None = None,
    ) -> None:
        super().__init__(mensagem, status=status)
        self.tentativas = tentativas


def _validar_numero(valor: Any, nome: str, *, minimo: float, estrito: bool = False) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nome} deve ser numérico")
    valor_float = float(valor)
    if math.isnan(valor_float):
        raise ValueError(f"{nome} não pode ser NaN")
    if estrito:
        if valor_float <= minimo:
            raise ValueError(f"{nome} deve ser > {minimo}")
    else:
        if valor_float < minimo:
            raise ValueError(f"{nome} deve ser >= {minimo}")
    return valor_float


def _validar_id(id_usuario: Any) -> int:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id_usuario inválido: {id_usuario!r}")
    return id_usuario


class ClienteAPI:
    """Cliente para consulta de usuários com suporte a retry, backoff e timeout."""

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

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = _validar_numero(backoff_base, "backoff_base", minimo=0.0)
        self.backoff_max = _validar_numero(backoff_max, "backoff_max", minimo=0.0)
        self.timeout = _validar_numero(timeout, "timeout", minimo=0.0, estrito=True)
        self.dormir = dormir
        self.orcamento_espera = (
            _validar_numero(orcamento_espera, "orcamento_espera", minimo=0.0)
            if orcamento_espera is not None
            else None
        )

    def _calcular_backoff(self, tentativa: int) -> float:
        try:
            calculado = math.ldexp(self.backoff_base, tentativa - 1)
        except OverflowError:
            calculado = float("inf")
        return min(self.backoff_max, calculado)

    def _extrair_retry_after(self, headers: dict[str, Any] | None) -> float | None:
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
                if math.isfinite(segundos) and segundos >= 0.0:
                    return segundos
                return None
        return None

    def obter_usuario(self, id_usuario: int) -> dict:
        _validar_id(id_usuario)

        espera_acumulada = 0.0
        ultimo_erro: Exception | None = None
        ultimo_status: int | None = None

        for tentativa in range(1, self.max_tentativas + 1):
            try:
                resposta = self.api.requisitar("GET", f"/usuarios/{id_usuario}", timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as exc:
                ultimo_erro = exc
                ultimo_status = None
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(f"Usuário {id_usuario} não encontrado", status=status)
                if status not in _STATUS_RETENTAVEIS:
                    raise ErroAPI(f"Erro HTTP {status}", status=status)
                ultimo_erro = None
                ultimo_status = status

            if tentativa == self.max_tentativas:
                break

            espera: float | None = None
            if ultimo_status == 429:
                retry_after = self._extrair_retry_after( getattr(resposta, "headers", None) )
                if retry_after is not None:
                    espera = min(self.backoff_max, retry_after)

            if espera is None:
                espera = self._calcular_backoff(tentativa)

            if self.orcamento_espera is not None and espera_acumulada + espera > self.orcamento_espera:
                break

            espera_acumulada += espera
            self.dormir(espera)

        if ultimo_erro is not None:
            raise FalhaPermanente(
                f"Falha após {tentativa} tentativa(s)",
                tentativas=tentativa,
            ) from ultimo_erro

        raise FalhaPermanente(
            f"Falha HTTP {ultimo_status} após {tentativa} tentativa(s)",
            tentativas=tentativa,
            status=ultimo_status,
        ) from None

    def obter_varios(self, ids: Iterable[int]) -> dict[int, dict | None]:
        lista_ids = [_validar_id(i) for i in ids]
        resultado: dict[int, dict | None] = {}
        for id_usuario in dict.fromkeys(lista_ids):
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado
