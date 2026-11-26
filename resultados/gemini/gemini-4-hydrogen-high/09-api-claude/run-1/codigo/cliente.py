"""Cliente HTTP com retry, backoff exponencial, timeout e orçamento de espera."""

from __future__ import annotations

from decimal import Decimal
import math
import time
from typing import Callable, Iterable

from fake_api import ErroConexao, TempoEsgotado

_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})


class ErroAPI(Exception):
    """Erro base levantado pelo ``ClienteAPI``."""

    def __init__(self, mensagem: str = "", *, status: int | None = None) -> None:
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (HTTP 404)."""

    def __init__(self, mensagem: str = "Recurso não encontrado", *, status: int = 404) -> None:
        super().__init__(mensagem, status=status)


class FalhaPermanente(ErroAPI):
    """Cliente desistiu após esgotar tentativas ou orçamento de espera."""

    def __init__(
        self,
        mensagem: str = "Falha permanente ao requisitar a API",
        *,
        tentativas: int,
        status: int | None = None,
    ) -> None:
        super().__init__(mensagem, status=status)
        self.tentativas = tentativas


def _validar_id(id_usuario: object) -> None:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id de usuário inválido: {id_usuario!r}")


def _obter_retry_after(headers: dict[str, str] | None) -> float | None:
    if not headers:
        return None
    for chave, valor in headers.items():
        if isinstance(chave, str) and chave.lower() == "retry-after":
            if isinstance(valor, bool):
                return None
            try:
                segundos = float(valor)
            except (TypeError, ValueError):
                return None
            if not math.isfinite(segundos) or segundos < 0:
                return None
            return 0.0 if segundos == 0 else segundos
    return None


class ClienteAPI:
    """Cliente resiliente para a API simulada de usuários."""

    def __init__(
        self,
        api,
        max_tentativas: int = 4,
        backoff_base: float = 0.5,
        backoff_max: float = 8.0,
        timeout: float = 2.0,
        dormir: Callable[[float], None] = time.sleep,
        orcamento_espera: float | None = None,
    ) -> None:
        if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int) or max_tentativas < 1:
            raise ValueError("max_tentativas deve ser um inteiro >= 1")
        if not (timeout > 0):
            raise ValueError("timeout deve ser > 0")
        if not (backoff_base >= 0):
            raise ValueError("backoff_base deve ser >= 0")
        if not (backoff_max >= 0):
            raise ValueError("backoff_max deve ser >= 0")
        if orcamento_espera is not None and not (orcamento_espera >= 0):
            raise ValueError("orcamento_espera deve ser >= 0")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self.dormir = dormir
        self.orcamento_espera = orcamento_espera

    def _calcular_backoff(self, falha_numero: int) -> float:
        """Calcula ``min(backoff_max, backoff_base * 2 ** (n - 1))`` sem overflow."""
        espera = float(self.backoff_base)
        limite = float(self.backoff_max)
        if espera <= 0.0 or limite <= 0.0:
            return 0.0
        for _ in range(falha_numero - 1):
            if espera >= limite:
                return limite
            espera *= 2.0
        return min(limite, espera)

    def _calcular_espera(self, falha_numero: int, status: int | None, headers: dict[str, str] | None) -> float:
        if status == 429:
            retry_after = _obter_retry_after(headers)
            if retry_after is not None:
                return min(float(self.backoff_max), retry_after)
        return self._calcular_backoff(falha_numero)

    def _excede_orcamento(self, espera_acumulada: Decimal, proxima_espera: float) -> bool:
        if self.orcamento_espera is None:
            return False
        nova_soma = espera_acumulada + Decimal(str(proxima_espera))
        return nova_soma > Decimal(str(self.orcamento_espera))

    def obter_usuario(self, id_usuario: int) -> dict:
        _validar_id(id_usuario)

        caminho = f"/usuarios/{id_usuario}"
        espera_acumulada = Decimal("0")
        ultima_excecao: Exception | None = None
        ultimo_status: int | None = None
        tentativas = 0

        for tentativa in range(1, self.max_tentativas + 1):
            tentativas = tentativa
            headers: dict[str, str] | None = None

            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as erro:
                ultima_excecao = erro
                ultimo_status = None
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(f"Usuário {id_usuario} não encontrado", status=404)
                if status not in _STATUS_RETENTAVEIS:
                    raise ErroAPI(f"Erro HTTP {status} ao buscar usuário {id_usuario}", status=status)

                ultima_excecao = None
                ultimo_status = status
                headers = resposta.headers

            if tentativa == self.max_tentativas:
                break

            espera = self._calcular_espera(tentativa, ultimo_status, headers)
            if self._excede_orcamento(espera_acumulada, espera):
                break

            self.dormir(espera)
            espera_acumulada += Decimal(str(espera))

        if ultima_excecao is not None:
            raise FalhaPermanente(
                f"Falha ao buscar usuário {id_usuario} após {tentativas} tentativa(s)",
                tentativas=tentativas,
            ) from ultima_excecao

        raise FalhaPermanente(
            f"Falha ao buscar usuário {id_usuario} após {tentativas} tentativa(s) (HTTP {ultimo_status})",
            tentativas=tentativas,
            status=ultimo_status,
        ) from None

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
