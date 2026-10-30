"""Cliente resiliente para a API simulada de usuários."""

import math
import time

from fake_api import ErroConexao, TempoEsgotado


class ErroAPI(Exception):
    """Erro produzido pelo cliente ao consultar a API."""


class NaoEncontrado(ErroAPI):
    """O recurso solicitado não existe."""


class FalhaPermanente(ErroAPI):
    """A consulta falhou após esgotar tentativas ou o orçamento de espera."""

    def __init__(self, mensagem: str, tentativas: int):
        super().__init__(mensagem)
        self.tentativas = tentativas


class ClienteAPI:
    _STATUS_RETENTAVEIS = {429, 500, 502, 503, 504}

    def __init__(
        self,
        api,
        max_tentativas: int = 4,
        backoff_base: float = 0.5,
        backoff_max: float = 8.0,
        timeout: float = 2.0,
        dormir=time.sleep,
        orcamento_espera: float | None = None,
    ):
        if max_tentativas < 1:
            raise ValueError("max_tentativas deve ser pelo menos 1")
        if timeout <= 0:
            raise ValueError("timeout deve ser positivo")
        if backoff_base < 0 or backoff_max < 0:
            raise ValueError("backoff não pode ser negativo")
        if orcamento_espera is not None and orcamento_espera < 0:
            raise ValueError("orcamento_espera não pode ser negativo")
        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self.dormir = dormir
        self.orcamento_espera = orcamento_espera

    @staticmethod
    def _validar_id(id_usuario):
        if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
            raise ValueError("id_usuario deve ser um inteiro positivo")

    def _backoff(self, falha_numero: int) -> float:
        """Calcula base * 2**(falha_numero-1), saturando sem expoente enorme."""
        valor = self.backoff_base
        for _ in range(falha_numero - 1):
            if valor >= self.backoff_max or valor == 0:
                return min(valor, self.backoff_max)
            # A comparação evita criar um float infinito em valores extremos.
            if valor > self.backoff_max / 2:
                return self.backoff_max
            valor *= 2
        return min(valor, self.backoff_max)

    @staticmethod
    def _retry_after(headers):
        for nome, valor in (headers or {}).items():
            if str(nome).lower() == "retry-after":
                try:
                    segundos = float(valor)
                except (TypeError, ValueError):
                    return None
                if math.isfinite(segundos) and segundos >= 0:
                    return segundos
                return None
        return None

    def obter_usuario(self, id_usuario: int) -> dict:
        self._validar_id(id_usuario)
        esperas_totais = 0.0
        ultima_excecao = None

        for tentativa in range(1, self.max_tentativas + 1):
            try:
                resposta = self.api.requisitar(
                    "GET", f"/usuarios/{id_usuario}", timeout=self.timeout
                )
            except (ErroConexao, TempoEsgotado) as erro:
                ultima_excecao = erro
                resposta = None
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    erro = NaoEncontrado(f"Usuário {id_usuario} não encontrado")
                    erro.status = status
                    raise erro
                if status not in self._STATUS_RETENTAVEIS:
                    erro = ErroAPI(f"Resposta HTTP inesperada: {status}")
                    erro.status = status
                    raise erro
                ultima_excecao = None

            if tentativa == self.max_tentativas:
                break

            espera = self._backoff(tentativa)
            if resposta is not None and resposta.status == 429:
                retry_after = self._retry_after(resposta.headers)
                if retry_after is not None:
                    espera = min(self.backoff_max, retry_after)

            novo_total = esperas_totais + espera
            if (self.orcamento_espera is not None
                    and novo_total > self.orcamento_espera):
                break
            self.dormir(espera)
            esperas_totais = novo_total

        falha = FalhaPermanente(
            f"Não foi possível obter usuário {id_usuario} após {tentativa} tentativa(s)",
            tentativa,
        )
        if ultima_excecao is not None:
            raise falha from ultima_excecao
        raise falha from None

    def obter_varios(self, ids) -> dict[int, dict | None]:
        ids_validados = list(ids)
        for id_usuario in ids_validados:
            self._validar_id(id_usuario)

        resultado = {}
        for id_usuario in ids_validados:
            if id_usuario in resultado:
                continue
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado
