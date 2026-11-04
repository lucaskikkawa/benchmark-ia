"""Cliente com retry para a API simulada de usuários."""

import math
import time

from fake_api import ErroConexao, TempoEsgotado


class ErroAPI(Exception):
    """Erro ocorrido ao consultar a API."""


class NaoEncontrado(ErroAPI):
    """O usuário solicitado não existe."""


class FalhaPermanente(ErroAPI):
    """As tentativas disponíveis foram esgotadas."""

    def __init__(self, mensagem: str, tentativas: int) -> None:
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
    ) -> None:
        if max_tentativas < 1:
            raise ValueError("max_tentativas deve ser pelo menos 1")
        if timeout <= 0:
            raise ValueError("timeout deve ser positivo")
        if backoff_base < 0:
            raise ValueError("backoff_base não pode ser negativo")
        if backoff_max < 0:
            raise ValueError("backoff_max não pode ser negativo")
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
    def _retry_after(headers):
        """Retorna Retry-After válido, ou None se ausente/inválido."""
        if headers is None:
            return None
        for nome, valor in headers.items():
            if isinstance(nome, str) and nome.lower() == "retry-after":
                try:
                    segundos = float(valor)
                except (TypeError, ValueError):
                    return None
                return segundos if math.isfinite(segundos) and segundos >= 0 else None
        return None

    def _falha_permanente(self, tentativas, erro_excecao=None):
        erro = FalhaPermanente(
            f"API falhou após {tentativas} tentativa(s)", tentativas=tentativas
        )
        if erro_excecao is not None:
            raise erro from erro_excecao
        raise erro from None

    def obter_usuario(self, id_usuario: int) -> dict:
        if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
            raise ValueError("id_usuario deve ser um inteiro positivo")

        tentativas = 0
        espera_backoff = min(self.backoff_base, self.backoff_max)
        espera_total = 0.0
        ultima_excecao = None

        while tentativas < self.max_tentativas:
            tentativas += 1
            try:
                resposta = self.api.requisitar(
                    "GET", f"/usuarios/{id_usuario}", timeout=self.timeout
                )
            except (ErroConexao, TempoEsgotado) as erro:
                ultima_excecao = erro
                headers = None
                status = None
            else:
                status = resposta.status
                ultima_excecao = None
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
                headers = resposta.headers

            if tentativas >= self.max_tentativas:
                self._falha_permanente(tentativas, ultima_excecao)

            espera = espera_backoff
            if status == 429:
                retry_after = self._retry_after(headers)
                if retry_after is not None:
                    espera = min(self.backoff_max, retry_after)

            if (
                self.orcamento_espera is not None
                and espera_total + espera > self.orcamento_espera
            ):
                self._falha_permanente(tentativas, ultima_excecao)

            self.dormir(espera)
            espera_total += espera

            # Mantém o próximo backoff limitado sem calcular 2 ** n, que pode
            # crescer além da faixa de representação numérica em muitas tentativas.
            if espera_backoff < self.backoff_max:
                if espera_backoff >= self.backoff_max / 2:
                    espera_backoff = self.backoff_max
                else:
                    espera_backoff *= 2

        # O laço sempre encerra dentro do ramo de esgotamento acima.
        raise AssertionError("fluxo inalcançável")

    def obter_varios(self, ids) -> dict[int, dict | None]:
        ids_unicos = []
        vistos = set()
        for id_usuario in ids:
            if (
                isinstance(id_usuario, bool)
                or not isinstance(id_usuario, int)
                or id_usuario < 1
            ):
                raise ValueError("cada id deve ser um inteiro positivo")
            if id_usuario not in vistos:
                vistos.add(id_usuario)
                ids_unicos.append(id_usuario)

        resultado = {}
        for id_usuario in ids_unicos:
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None
        return resultado
