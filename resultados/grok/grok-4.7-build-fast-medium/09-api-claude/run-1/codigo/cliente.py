"""Cliente com retentativas, backoff exponencial e orçamento de espera."""

from __future__ import annotations

import math
import time

from fake_api import ErroConexao, TempoEsgotado

# Status HTTP que autorizam uma nova tentativa.
_STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})


class ErroAPI(Exception):
    """Erro do cliente ao interpretar a resposta da API."""


class NaoEncontrado(ErroAPI):
    """O recurso pedido não existe (HTTP 404)."""

    def __init__(self, mensagem: str = "não encontrado", status: int = 404) -> None:
        super().__init__(mensagem)
        self.status = status


class FalhaPermanente(ErroAPI):
    """As tentativas ou o orçamento de espera se esgotaram."""

    def __init__(self, mensagem: str = "falha permanente", tentativas: int = 0) -> None:
        super().__init__(mensagem)
        self.tentativas = tentativas


def _validar_id(id_usuario: object) -> None:
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
        raise ValueError(f"id de usuário inválido: {id_usuario!r}")


def _erro_status(cls: type[ErroAPI], mensagem: str, status: int) -> ErroAPI:
    erro = cls(mensagem)
    erro.status = status
    return erro


def _retry_after(headers) -> float | None:
    """Segundos de Retry-After, ou None se o header não servir."""
    if not headers:
        return None
    try:
        itens = headers.items()
    except AttributeError:
        return None
    for chave, valor in itens:
        if not isinstance(chave, str) or chave.lower() != "retry-after":
            continue
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return None
        if math.isfinite(numero) and numero >= 0:
            return numero
        return None
    return None


class ClienteAPI:
    """Consulta usuários com timeout, retentativa e backoff.

    ``dormir`` é chamado entre tentativas (os testes podem injetar um falso).
    ``orcamento_espera`` limita a soma das esperas de uma chamada de
    ``obter_usuario``; ``None`` desliga o limite.
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
        """Busca um usuário. Retenta falhas transitórias até o limite."""
        _validar_id(id_usuario)
        caminho = f"/usuarios/{id_usuario}"
        espera_acumulada = 0.0

        for n in range(1, self.max_tentativas + 1):
            try:
                resposta = self.api.requisitar("GET", caminho, timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as erro:
                espera_acumulada += self._apos_falha_retentavel(
                    n, espera_acumulada, None, erro
                )
                continue

            status = resposta.status
            if status == 200:
                return resposta.corpo
            if status == 404:
                raise _erro_status(NaoEncontrado, "não encontrado", status)
            if status not in _STATUS_RETENTAVEIS:
                raise _erro_status(ErroAPI, f"resposta HTTP {status}", status)

            espera_acumulada += self._apos_falha_retentavel(
                n, espera_acumulada, resposta, None
            )

        raise FalhaPermanente(
            f"falha permanente após {self.max_tentativas} tentativa(s)",
            tentativas=self.max_tentativas,
        )

    def obter_varios(self, ids) -> dict[int, dict | None]:
        """Busca vários usuários, na ordem da primeira aparição de cada id.

        Valida todos os ids antes de qualquer requisição. ``NaoEncontrado``
        vira ``None``. Ids repetidos são pedidos uma única vez.
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

    def _espera_exponencial(self, n: int) -> float:
        """``min(backoff_max, backoff_base * 2 ** (n - 1))`` sem estourar."""
        base = float(self.backoff_base)
        teto = float(self.backoff_max)
        expoente = n - 1
        if expoente <= 0:
            return min(base, teto)
        if base <= 0.0 or teto <= 0.0:
            return 0.0
        if base >= teto:
            return teto

        # base = mantissa * 2**eb, com 0.5 <= mantissa < 1.
        mantissa, eb = math.frexp(base)
        exp_total = eb + expoente
        mantissa_teto, exp_teto = math.frexp(teto)
        if exp_total > exp_teto or (exp_total == exp_teto and mantissa >= mantissa_teto):
            return teto
        try:
            return math.ldexp(mantissa, exp_total)
        except (OverflowError, ValueError):
            return teto

    def _calcular_espera(self, n: int, resposta) -> float:
        if resposta is not None and resposta.status == 429:
            indicado = _retry_after(getattr(resposta, "headers", None))
            if indicado is not None:
                teto = float(self.backoff_max)
                return indicado if indicado < teto else teto
        return self._espera_exponencial(n)

    def _apos_falha_retentavel(
        self,
        n: int,
        espera_acumulada: float,
        resposta,
        causa: BaseException | None,
    ) -> float:
        """Espera antes da próxima tentativa, ou desiste.

        Devolve a espera aplicada (já dormida).
        """
        if n >= self.max_tentativas:
            self._desistir(n, causa)
        espera = self._calcular_espera(n, resposta)
        orcamento = self.orcamento_espera
        if orcamento is not None and espera_acumulada + espera > orcamento:
            self._desistir(n, causa)
        self.dormir(espera)
        return espera

    @staticmethod
    def _desistir(tentativas: int, causa: BaseException | None) -> None:
        erro = FalhaPermanente(
            f"falha permanente após {tentativas} tentativa(s)",
            tentativas=tentativas,
        )
        if causa is not None:
            raise erro from causa
        raise erro
