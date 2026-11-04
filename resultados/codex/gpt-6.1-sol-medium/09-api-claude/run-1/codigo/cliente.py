"""Cliente da API de usuários com tentativas e espera limitadas."""

import math
import time

from fake_api import ErroConexao, TempoEsgotado


class ErroAPI(Exception):
    """Erro ao consultar a API; status é preenchido para erros HTTP."""

    def __init__(self, mensagem, status=None):
        super().__init__(mensagem)
        self.status = status


class NaoEncontrado(ErroAPI):
    """O usuário solicitado não existe."""


class FalhaPermanente(ErroAPI):
    """As tentativas ou o orçamento de espera foram esgotados."""

    def __init__(self, mensagem, tentativas, status=None):
        super().__init__(mensagem, status=status)
        self.tentativas = tentativas


class ClienteAPI:
    _STATUS_RETENTAVEIS = frozenset({429, 500, 502, 503, 504})

    def __init__(self, api, max_tentativas: int = 4,
                 backoff_base: float = 0.5, backoff_max: float = 8.0,
                 timeout: float = 2.0, dormir=time.sleep,
                 orcamento_espera: float | None = None):
        if max_tentativas < 1:
            raise ValueError("max_tentativas deve ser pelo menos 1")
        if timeout <= 0:
            raise ValueError("timeout deve ser positivo")
        if backoff_base < 0 or backoff_max < 0:
            raise ValueError("os valores de backoff não podem ser negativos")
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
        if (not isinstance(id_usuario, int)
                or isinstance(id_usuario, bool) or id_usuario < 1):
            raise ValueError("id_usuario deve ser um inteiro positivo")

    def _espera_http(self, resposta, backoff):
        if resposta.status == 429:
            for nome, valor in resposta.headers.items():
                if nome.lower() == "retry-after":
                    try:
                        segundos = float(valor)
                    except (TypeError, ValueError, OverflowError):
                        break
                    if math.isfinite(segundos) and segundos >= 0:
                        return min(self.backoff_max, segundos)
                    break
        return backoff

    def obter_usuario(self, id_usuario: int) -> dict:
        self._validar_id(id_usuario)
        total_espera = 0.0
        backoff = min(self.backoff_base, self.backoff_max)

        for tentativa in range(1, self.max_tentativas + 1):
            ultimo_erro = None
            status = None
            espera = backoff
            try:
                resposta = self.api.requisitar(
                    "GET", f"/usuarios/{id_usuario}", timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as erro:
                ultimo_erro = erro
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado("Usuário não encontrado", status=status)
                if status not in self._STATUS_RETENTAVEIS:
                    raise ErroAPI(f"Resposta HTTP {status}", status=status)
                espera = self._espera_http(resposta, backoff)

            if tentativa == self.max_tentativas:
                raise FalhaPermanente(
                    "Número máximo de tentativas atingido", tentativa,
                    status=status) from ultimo_erro
            if (self.orcamento_espera is not None
                    and total_espera + espera > self.orcamento_espera):
                raise FalhaPermanente(
                    "Orçamento de espera esgotado", tentativa,
                    status=status) from ultimo_erro

            self.dormir(espera)
            total_espera += espera
            # Dobra apenas enquanto abaixo do teto, sem criar 2 ** tentativa.
            if backoff >= self.backoff_max / 2:
                backoff = self.backoff_max
            else:
                backoff *= 2

    def obter_varios(self, ids) -> dict[int, dict | None]:
        unicos = {}
        for id_usuario in ids:
            self._validar_id(id_usuario)
            unicos.setdefault(id_usuario, None)

        for id_usuario in unicos:
            try:
                unicos[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                unicos[id_usuario] = None
        return unicos
