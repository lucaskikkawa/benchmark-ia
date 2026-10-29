"""Cliente da API de usuários com retry, backoff exponencial e timeout."""

import time
from collections.abc import Callable, Iterable

from fake_api import ErroConexao, TempoEsgotado

STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})
EXCECOES_RETENTAVEIS = (ErroConexao, TempoEsgotado)


class ErroAPI(Exception):
    """Base dos erros do cliente."""


class NaoEncontrado(ErroAPI):
    """O recurso não existe (HTTP 404)."""


class FalhaPermanente(ErroAPI):
    """Todas as tentativas falharam com erros retentáveis."""

    def __init__(self, mensagem: str, tentativas: int) -> None:
        super().__init__(mensagem)
        self.tentativas = tentativas


def _ler_retry_after(headers: dict | None) -> float | None:
    """Segundos do header Retry-After, ou None se ausente/inválido."""
    valor = (headers or {}).get("Retry-After")
    try:
        segundos = float(valor)
    except (TypeError, ValueError):
        return None
    return segundos if segundos >= 0 else None


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
    ) -> None:
        if max_tentativas < 1:
            raise ValueError("max_tentativas deve ser >= 1")
        if timeout <= 0:
            raise ValueError("timeout deve ser > 0")
        if backoff_base < 0 or backoff_max < 0:
            raise ValueError("backoff_base e backoff_max devem ser >= 0")
        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self._dormir = dormir

    def _espera(self, falha: int, retry_after: float | None) -> float:
        """Tempo de espera após a ``falha``-ésima falha (1, 2, ...)."""
        if retry_after is not None:
            return min(self.backoff_max, retry_after)
        return min(self.backoff_max, self.backoff_base * 2 ** (falha - 1))

    def obter_usuario(self, id_usuario: int) -> dict:
        """Busca um usuário, repetindo em falhas transitórias.

        Raises:
            ValueError: id inválido.
            NaoEncontrado: usuário inexistente.
            ErroAPI: erro 4xx não retentável ou status inesperado.
            FalhaPermanente: tentativas esgotadas.
        """
        if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
            raise ValueError(f"id inválido: {id_usuario!r}")
        caminho = f"/usuarios/{id_usuario}"

        ultimo_erro: Exception | None = None
        for tentativa in range(1, self.max_tentativas + 1):
            retry_after = None
            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except EXCECOES_RETENTAVEIS as erro:
                ultimo_erro = erro
            else:
                if resposta.status == 200:
                    return resposta.corpo
                if resposta.status == 404:
                    raise NaoEncontrado(caminho)
                if resposta.status not in STATUS_RETENTAVEIS:
                    raise ErroAPI(f"status inesperado {resposta.status} em {caminho}")
                ultimo_erro = None
                if resposta.status == 429:
                    retry_after = _ler_retry_after(resposta.headers)

            if tentativa < self.max_tentativas:
                self._dormir(self._espera(tentativa, retry_after))

        mensagem = f"{caminho}: falhou após {self.max_tentativas} tentativa(s)"
        raise FalhaPermanente(mensagem, self.max_tentativas) from ultimo_erro

    def obter_varios(self, ids: Iterable[int]) -> dict[int, dict | None]:
        """Busca vários usuários; inexistentes viram None. Ids repetidos são buscados uma vez."""
        resultado: dict[int, dict | None] = {}
        for id_usuario in ids:
            if id_usuario in resultado:
                continue
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado
