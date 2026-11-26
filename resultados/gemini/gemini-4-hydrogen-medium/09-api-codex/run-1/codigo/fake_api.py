"""API inteiramente local: latências virtuais, sem socket e sem espera real."""
from copy import deepcopy
import random


class ErroTemporario(Exception):
    pass


class ErroPermanente(Exception):
    pass


class FakeAPI:
    def __init__(self, dados: dict[str, dict], seed: int = 0):
        self._dados = deepcopy(dados)
        rng = random.Random(seed)
        self._roteiros = {
            chave: [rng.choice(('temporario', 'lento')) for _ in range(rng.randrange(3))] + ['ok']
            for chave in sorted(dados)
        }
        self._posicoes = dict.fromkeys(dados, 0)
        self.chamadas = []

    def get(self, chave: str, *, timeout: float) -> dict:
        """Consuma um evento do roteiro, comparando a latência virtual ao timeout."""
        if chave not in self._dados:
            self.chamadas.append((chave, timeout, 'permanente'))
            raise ErroPermanente(chave)
        roteiro = self._roteiros[chave]
        indice = self._posicoes[chave]
        evento = roteiro[min(indice, len(roteiro) - 1)]
        self._posicoes[chave] += 1
        self.chamadas.append((chave, timeout, evento))
        latencia = 2.0 if evento == 'lento' else 0.01
        if latencia > timeout:
            raise TimeoutError('latência virtual excedeu o timeout')
        if evento == 'temporario':
            raise ErroTemporario(chave)
        return deepcopy(self._dados[chave])
