"""Cliente HTTP com retry, backoff exponencial, Retry-After e orçamento de espera."""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from fake_api import ErroConexao, TempoEsgotado

_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})
_EXCECOES_RETENTAVEIS = (ErroConexao, TempoEsgotado)
_MAX_LDEXP_EXP = 2098  # 2**(-1074) * 2**2098 == 2**1024 > sys.float_info.max


class ErroAPI(Exception):
    """Erro base levantado pelo ClienteAPI."""

    def __init__(self, mensagem: str = "", *, status: int | None = None) -> None:
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (HTTP 404)."""

    def __init__(self, mensagem: str = "", *, status: int = 404) -> None:
        super().__init__(mensagem, status=status)


class FalhaPermanente(ErroAPI):
    """Cliente desistiu após esgotar tentativas ou orçamento de espera."""

    def __init__(
        self,
        mensagem: str = "",
        *,
        tentativas: int = 0,
        status: int | None = None,
    ) -> None:
        super().__init__(mensagem, status=status)
        self.tentativas = tentativas


def _validar_id(id_usuario: Any) -> int:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id_usuario inválido: {id_usuario!r}")
    return id_usuario


def _extrair_retry_after(headers: Mapping[str, Any] | None) -> float | None:
    if not headers:
        return None
    valor: Any = None
    for chave, v in headers.items():
        if isinstance(chave, str) and chave.lower() == "retry-after":
            valor = v
            break
    if valor is None or isinstance(valor, bool):
        return None
    try:
        segundos = float(valor)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(segundos) or segundos < 0:
        return None
    return 0.0 if segundos == 0 else segundos


class ClienteAPI:
    """Cliente resiliente com retry, backoff exponencial e timeout."""

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
            raise ValueError(f"max_tentativas deve ser inteiro >= 1, recebido: {max_tentativas!r}")
        if isinstance(timeout, bool) or not (timeout > 0):
            raise ValueError(f"timeout deve ser > 0, recebido: {timeout!r}")
        if isinstance(backoff_base, bool) or not (backoff_base >= 0):
            raise ValueError(f"backoff_base deve ser >= 0, recebido: {backoff_base!r}")
        if isinstance(backoff_max, bool) or not (backoff_max >= 0):
            raise ValueError(f"backoff_max deve ser >= 0, recebido: {backoff_max!r}")
        if orcamento_espera is not None and (isinstance(orcamento_espera, bool) or not (orcamento_espera >= 0)):
            raise ValueError(f"orcamento_espera deve ser >= 0 ou None, recebido: {orcamento_espera!r}")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = float(backoff_base)
        self.backoff_max = float(backoff_max)
        self.timeout = float(timeout)
        self.dormir = dormir
        self.orcamento_espera = float(orcamento_espera) if orcamento_espera is not None else None

    def _calcular_backoff(self, numero_falha: int) -> float:
        base = self.backoff_base
        limite = self.backoff_max
        if base == 0.0 or limite == 0.0:
            return 0.0
        if base >= limite:
            return limite
        expoente = numero_falha - 1
        if expoente >= _MAX_LDEXP_EXP:
            return limite
        try:
            calculado = math.ldexp(base, expoente)
        except OverflowError:
            return limite
        return min(limite, calculado)

    def _calcular_espera(self, numero_falha: int, resposta: Any | None) -> float:
        if resposta is not None and resposta.status == 429:
            retry_after = _extrair_retry_after(resposta.headers)
            if retry_after is not None:
                return min(self.backoff_max, retry_after)
        return self._calcular_backoff(numero_falha)

    def obter_usuario(self, id_usuario: int) -> dict:
        _validar_id(id_usuario)
        caminho = f"/usuarios/{id_usuario}"
        espera_acumulada = 0.0
        ultima_excecao: Exception | None = None
        ultimo_status: int | None = None
        tentativas_feitas = 0

        for tentativa in range(1, self.max_tentativas + 1):
            tentativas_feitas = tentativa
            resposta = None
            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except _EXCECOES_RETENTAVEIS as erro:
                ultima_excecao = erro
                ultimo_status = None
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(f"Usuário {id_usuario} não encontrado", status=404)
                if status not in _STATUS_RETENTAVEIS:
                    raise ErroAPI(f"Erro HTTP {status} ao obter usuário {id_usuario}", status=status)
                ultima_excecao = None
                ultimo_status = status

            if tentativa == self.max_tentativas:
                break

            espera = self._calcular_espera(tentativa, resposta)
            if self.orcamento_espera is not None and espera_acumulada + espera > self.orcamento_espera:
                break

            self.dormir(espera)
            espera_acumulada += espera

        if ultima_excecao is not None:
            raise FalhaPermanente(
                f"Falha após {tentativas_feitas} tentativa(s) ao obter usuário {id_usuario}: {ultima_excecao}",
                tentativas=tentativas_feitas,
            ) from ultima_excecao

        raise FalhaPermanente(
            f"Falha após {tentativas_feitas} tentativa(s) ao obter usuário {id_usuario} (HTTP {ultimo_status})",
            tentativas=tentativas_feitas,
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
