"""Cliente de usuários com timeout, retentativas e orçamento de espera."""

import math
import time

from fake_api import ErroConexao, TempoEsgotado


class ErroAPI(Exception):
    """Erro do cliente, com o status HTTP quando houver resposta."""

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
    def __init__(self, api, max_tentativas: int = 4, backoff_base: float = 0.5,
                 backoff_max: float = 8.0, timeout: float = 2.0, dormir=time.sleep,
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

    def _espera_retry_after(self, headers, padrao):
        for nome, valor in headers.items():
            if nome.lower() == "retry-after":
                try:
                    segundos = float(valor)
                except (TypeError, ValueError, OverflowError):
                    return padrao
                if math.isfinite(segundos) and segundos >= 0:
                    return min(self.backoff_max, segundos)
                return padrao
        return padrao

    def obter_usuario(self, id_usuario: int) -> dict:
        self._validar_id(id_usuario)
        total_espera = 0.0
        backoff = min(self.backoff_max, self.backoff_base)

        for tentativa in range(1, self.max_tentativas + 1):
            erro = None
            status = None
            espera = backoff
            try:
                resposta = self.api.requisitar(
                    "GET", f"/usuarios/{id_usuario}", timeout=self.timeout
                )
            except (ErroConexao, TempoEsgotado) as falha:
                erro = falha
            else:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(
                        f"Usuário {id_usuario} não encontrado", status=status
                    )
                if status not in (429, 500, 502, 503, 504):
                    raise ErroAPI(f"Resposta HTTP {status}", status=status)
                if status == 429:
                    espera = self._espera_retry_after(resposta.headers, backoff)

            if (tentativa == self.max_tentativas
                    or (self.orcamento_espera is not None
                        and total_espera + espera > self.orcamento_espera)):
                raise FalhaPermanente(
                    f"Falha ao obter usuário {id_usuario} após {tentativa} tentativa(s)",
                    tentativas=tentativa, status=status,
                ) from erro

            self.dormir(espera)
            total_espera += espera
            # Comparar com o espaço restante evita overflow ao dobrar e
            # mantém o custo constante, mesmo com milhares de tentativas.
            if backoff >= self.backoff_max - backoff:
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
