"""Cliente da API de usuários com retry, backoff exponencial e timeout."""

import math
import time
from collections.abc import Callable, Iterable

from fake_api import ErroConexao, TempoEsgotado

STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})
EXCECOES_RETENTAVEIS = (ErroConexao, TempoEsgotado)


class ErroAPI(Exception):
    """Base dos erros do cliente. ``status`` é o código HTTP quando o erro veio de uma resposta."""

    def __init__(self, mensagem: str, status: int | None = None) -> None:
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """O recurso não existe (HTTP 404)."""


class FalhaPermanente(ErroAPI):
    """O cliente desistiu após falhas retentáveis (tentativas ou orçamento de espera esgotados)."""

    def __init__(self, mensagem: str, tentativas: int) -> None:
        super().__init__(mensagem)
        self.tentativas = tentativas


def _ler_retry_after(headers: dict | None) -> float | None:
    """Segundos do header Retry-After (nome sem diferenciar caixa), ou None se ausente/inválido."""
    valor = next(
        (v for chave, v in (headers or {}).items() if str(chave).lower() == "retry-after"),
        None,
    )
    try:
        segundos = float(valor)
    except (TypeError, ValueError):
        return None
    return segundos if math.isfinite(segundos) and segundos >= 0 else None


def _validar_id(id_usuario) -> None:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id inválido: {id_usuario!r}")


class ClienteAPI:
    """Cliente de ``/usuarios/{id}`` resiliente a falhas transitórias."""

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
        if max_tentativas < 1:
            raise ValueError("max_tentativas deve ser >= 1")
        if timeout <= 0:
            raise ValueError("timeout deve ser > 0")
        if backoff_base < 0 or backoff_max < 0:
            raise ValueError("backoff_base e backoff_max devem ser >= 0")
        if orcamento_espera is not None and orcamento_espera < 0:
            raise ValueError("orcamento_espera deve ser >= 0")
        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self.orcamento_espera = orcamento_espera
        self._dormir = dormir

    def _espera(self, falha: int, retry_after: float | None) -> float:
        """Tempo de espera após a ``falha``-ésima falha (1, 2, ...)."""
        if retry_after is not None:
            return min(self.backoff_max, retry_after)
        try:
            # ldexp(b, e) == b * 2**e, sem converter 2**e (int enorme) para float.
            exponencial = math.ldexp(self.backoff_base, falha - 1)
        except OverflowError:
            exponencial = math.inf
        return min(self.backoff_max, exponencial)

    def obter_usuario(self, id_usuario: int) -> dict:
        """Busca um usuário, repetindo em falhas transitórias.

        Raises:
            ValueError: id inválido.
            NaoEncontrado: usuário inexistente.
            ErroAPI: status HTTP não retentável inesperado.
            FalhaPermanente: tentativas ou orçamento de espera esgotados.
        """
        _validar_id(id_usuario)
        caminho = f"/usuarios/{id_usuario}"

        esperado = 0.0
        ultimo_erro: Exception | None = None
        for tentativa in range(1, self.max_tentativas + 1):
            retry_after = None
            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except EXCECOES_RETENTAVEIS as erro:
                ultimo_erro = erro
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(f"{caminho}: não encontrado", status)
                if status not in STATUS_RETENTAVEIS:
                    raise ErroAPI(f"status inesperado {status} em {caminho}", status)
                ultimo_erro = None
                if status == 429:
                    retry_after = _ler_retry_after(resposta.headers)

            if tentativa == self.max_tentativas:
                break
            espera = self._espera(tentativa, retry_after)
            if self.orcamento_espera is not None and esperado + espera > self.orcamento_espera:
                break
            self._dormir(espera)
            esperado += espera

        mensagem = f"{caminho}: desistiu após {tentativa} tentativa(s)"
        raise FalhaPermanente(mensagem, tentativa) from ultimo_erro

    def obter_varios(self, ids: Iterable[int]) -> dict[int, dict | None]:
        """Busca vários usuários; inexistentes viram None. Ids repetidos são buscados uma vez."""
        ids = list(ids)
        for id_usuario in ids:
            _validar_id(id_usuario)
        resultado: dict[int, dict | None] = {}
        for id_usuario in ids:
            if id_usuario in resultado:
                continue
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado
