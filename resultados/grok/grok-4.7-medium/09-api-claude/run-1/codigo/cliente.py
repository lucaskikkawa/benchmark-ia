"""Cliente com retry, backoff e timeout para a API simulada de usuários."""

from __future__ import annotations

import math
import time

from fake_api import ErroConexao, TempoEsgotado

# Status HTTP que justificam nova tentativa.
_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})


class ErroAPI(Exception):
    """Base dos erros do cliente."""


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (HTTP 404)."""


class FalhaPermanente(ErroAPI):
    """Desistiu após esgotar as tentativas ou o orçamento de espera.

    Attributes:
        tentativas: número de requisições feitas na chamada que desistiu.
    """

    def __init__(self, mensagem: str, tentativas: int) -> None:
        super().__init__(mensagem)
        self.tentativas = tentativas


class ClienteAPI:
    """Cliente de usuários com retentativas, backoff exponencial e timeout.

    ``api`` é qualquer objeto com ``requisitar(metodo, caminho, timeout)``.
    ``dormir`` é chamado entre tentativas (os testes podem injetar um substituto).
    """

    def __init__(
        self,
        api,
        max_tentativas: int = 4,
        backoff_base: float = 0.5,
        backoff_max: float = 8.0,
        timeout: float = 2.0,
        dormir=time.sleep,
        orcamento_espera: float | None = None,
    ) -> None:
        if max_tentativas < 1:
            raise ValueError("max_tentativas deve ser >= 1")
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

    def obter_usuario(self, id_usuario: int) -> dict:
        """Busca um usuário, repetindo falhas transitórias até desistir."""
        _validar_id(id_usuario)
        caminho = f"/usuarios/{id_usuario}"
        soma_esperas = 0.0

        for n in range(1, self.max_tentativas + 1):
            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as erro:
                self._apos_falha(n, soma_esperas, self._backoff(n), erro)
                soma_esperas += self._backoff(n)
                continue

            status = resposta.status
            if status == 200:
                return resposta.corpo
            if status == 404:
                raise _erro_status(NaoEncontrado, status, "usuário não encontrado")
            if status not in _STATUS_RETENTAVEIS:
                raise _erro_status(ErroAPI, status, f"resposta HTTP {status}")

            espera = self._espera_retentavel(n, status, getattr(resposta, "headers", None))
            self._apos_falha(n, soma_esperas, espera, None)
            soma_esperas += espera

        raise AssertionError("loop de tentativas terminou sem retorno")  # pragma: no cover

    def obter_varios(self, ids) -> dict[int, dict | None]:
        """Busca vários usuários, um a um, na ordem da primeira aparição.

        Valida todos os ids antes de qualquer requisição. Ids repetidos são
        pedidos uma única vez. ``NaoEncontrado`` vira ``None``.
        """
        unicos: list[int] = []
        vistos: set[int] = set()
        for id_usuario in ids:
            _validar_id(id_usuario)
            if id_usuario not in vistos:
                vistos.add(id_usuario)
                unicos.append(id_usuario)

        resultado: dict[int, dict | None] = {}
        for id_usuario in unicos:
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado

    def _apos_falha(
        self,
        n: int,
        soma_esperas: float,
        espera: float,
        causa: BaseException | None,
    ) -> None:
        """Desiste na última tentativa ou se a próxima espera estourar o orçamento.

        Caso contrário, espera ``espera`` segundos via ``dormir``.
        """
        if n >= self.max_tentativas or self._estoura_orcamento(soma_esperas, espera):
            self._desistir(n, causa)
        self.dormir(espera)

    def _desistir(self, tentativas: int, causa: BaseException | None) -> None:
        erro = FalhaPermanente(
            f"falha permanente após {tentativas} tentativa(s)",
            tentativas,
        )
        if causa is None:
            raise erro from None
        raise erro from causa

    def _estoura_orcamento(self, soma_esperas: float, espera: float) -> bool:
        if self.orcamento_espera is None:
            return False
        return soma_esperas + espera > self.orcamento_espera

    def _espera_retentavel(self, n: int, status: int, headers) -> float:
        if status == 429:
            retry_after = _retry_after_segundos(headers)
            if retry_after is not None:
                return min(self.backoff_max, retry_after)
        return self._backoff(n)

    def _backoff(self, n: int) -> float:
        """``min(backoff_max, backoff_base * 2 ** (n - 1))`` sem estourar o float."""
        expoente = n - 1
        base = float(self.backoff_base)
        teto = float(self.backoff_max)
        if base <= 0.0 or teto <= 0.0:
            return 0.0
        if expoente <= 0:
            return min(teto, base)
        if base >= teto:
            return teto
        # Atalho quando o resultado certamente ultrapassa o teto (n grande).
        # A margem de 1 no log evita um corte prematuro por erro de arredondamento.
        if expoente > (math.log2(teto) - math.log2(base)) + 1:
            return teto
        try:
            valor = math.ldexp(base, expoente)
        except (OverflowError, ValueError):
            return teto
        if not math.isfinite(valor) or valor >= teto:
            return teto
        return valor


def _validar_id(id_usuario) -> None:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id de usuário inválido: {id_usuario!r}")


def _erro_status(classe: type[ErroAPI], status: int, mensagem: str) -> ErroAPI:
    erro = classe(mensagem)
    erro.status = status
    return erro


def _retry_after_segundos(headers) -> float | None:
    """Segundos de Retry-After, ou None se o header não for um número finito >= 0."""
    if not headers:
        return None
    bruto = None
    for chave, valor in headers.items():
        if isinstance(chave, str) and chave.lower() == "retry-after":
            bruto = valor
            break
    if bruto is None:
        return None
    try:
        numero = float(bruto)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numero) or numero < 0:
        return None
    return numero
