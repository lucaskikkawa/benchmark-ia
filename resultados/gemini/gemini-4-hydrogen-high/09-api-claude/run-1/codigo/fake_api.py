"""API HTTP de usuários simulada em processo (sem rede, sem sleep real).

Falhas e lentidão são determinísticas: vêm de um ``roteiro`` explícito de
eventos ou são sorteadas por ``random.Random(seed)``.

Não altere este arquivo.
"""

import random
import re
from dataclasses import dataclass, field

_CAMINHO_USUARIO = re.compile(r"/usuarios/(\d+)")
MAX_ID = 1000

# Eventos possíveis por requisição.
OK = "ok"            # resposta normal (200 ou 404, conforme o caminho)
ERRO_500 = "500"     # Resposta(500)
ERRO_503 = "503"     # Resposta(503)
ERRO_429 = "429"     # Resposta(429) com header Retry-After
LENTO = "lento"      # demora latencia_lenta segundos (simulados)
CONEXAO = "conexao"  # levanta ErroConexao
FALHAS = (ERRO_500, ERRO_503, ERRO_429, LENTO, CONEXAO)


class ErroConexao(Exception):
    """Falha de conexão simulada."""


class TempoEsgotado(Exception):
    """A resposta demoraria mais que o timeout pedido."""


@dataclass
class Resposta:
    status: int
    corpo: dict | None = None
    headers: dict[str, str] = field(default_factory=dict)


class FakeAPI:
    """Servidor simulado.

    Args:
        seed: semente do sorteio de falhas (usado quando não há roteiro).
        taxa_falha: probabilidade de cada requisição sortear um evento de FALHAS.
        latencia_normal: segundos simulados de uma resposta normal.
        latencia_lenta: segundos simulados do evento LENTO.
        retry_after: valor do header Retry-After nas respostas 429.
        roteiro: sequência de eventos consumidos em ordem, um por requisição;
            quando acaba, as requisições seguintes são OK. Se fornecido, o
            sorteio por seed não é usado.

    Atributos de inspeção:
        chamadas: lista de (metodo, caminho, timeout) de cada requisição.
        eventos: lista do evento aplicado a cada requisição.
        tempo_simulado: soma das latências simuladas.
    """

    def __init__(
        self,
        seed: int = 0,
        taxa_falha: float = 0.3,
        latencia_normal: float = 0.05,
        latencia_lenta: float = 5.0,
        retry_after: str = "2",
        roteiro: list[str] | None = None,
    ) -> None:
        self._rng = random.Random(seed)
        self.taxa_falha = taxa_falha
        self.latencia_normal = latencia_normal
        self.latencia_lenta = latencia_lenta
        self.retry_after = retry_after
        self._roteiro = list(roteiro) if roteiro is not None else None
        self.chamadas: list[tuple[str, str, float]] = []
        self.eventos: list[str] = []
        self.tempo_simulado = 0.0

    def _proximo_evento(self) -> str:
        if self._roteiro is not None:
            return self._roteiro.pop(0) if self._roteiro else OK
        if self._rng.random() < self.taxa_falha:
            return self._rng.choice(FALHAS)
        return OK

    def requisitar(self, metodo: str, caminho: str, timeout: float) -> Resposta:
        """Executa uma requisição simulada.

        Raises:
            ErroConexao: evento CONEXAO.
            TempoEsgotado: latência simulada maior que ``timeout``.
        """
        self.chamadas.append((metodo, caminho, timeout))
        evento = self._proximo_evento()
        self.eventos.append(evento)

        if evento == CONEXAO:
            raise ErroConexao("conexão recusada (simulada)")
        if evento == ERRO_500:
            return Resposta(500, {"erro": "erro interno"})
        if evento == ERRO_503:
            return Resposta(503, {"erro": "serviço indisponível"})
        if evento == ERRO_429:
            return Resposta(429, {"erro": "muitas requisições"}, {"Retry-After": self.retry_after})

        latencia = self.latencia_lenta if evento == LENTO else self.latencia_normal
        if latencia > timeout:
            self.tempo_simulado += timeout
            raise TempoEsgotado(f"sem resposta em {timeout}s")
        self.tempo_simulado += latencia
        return self._responder(metodo, caminho)

    @staticmethod
    def _responder(metodo: str, caminho: str) -> Resposta:
        if metodo != "GET":
            return Resposta(405, {"erro": "método não permitido"})
        casamento = _CAMINHO_USUARIO.fullmatch(caminho)
        if casamento is None or not 1 <= int(casamento.group(1)) <= MAX_ID:
            return Resposta(404, {"erro": "não encontrado"})
        id_usuario = int(casamento.group(1))
        return Resposta(200, {"id": id_usuario, "nome": f"Usuario {id_usuario}"})
