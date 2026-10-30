"""API local em processo, sem rede.

As falhas dependem só do prefixo do id e da seed. O relógio de lentidão é
fixo (ATRASO_S), para o cliente conseguir impor timeout.
"""

import hashlib
import time

ATRASO_S = 1.2


class LojaErro(Exception):
    """Base dos erros simulados da loja."""


class LojaIndisponivel(LojaErro):
    """Falha transitória (equivalente a HTTP 503). Vale tentar de novo."""


class LojaErroCliente(LojaErro):
    """Pedido impossível (equivalente a HTTP 404). Não vale tentar de novo."""


def payload_pedido(seed: int, pedido_id: str) -> dict:
    """Corpo estável de um pedido pago. Não altera contadores."""
    digest = hashlib.sha256(f"{seed}:{pedido_id}".encode()).hexdigest()
    return {
        "id": pedido_id,
        "total_centavos": int(digest[:8], 16) % 100_000,
        "status": "pago",
    }


class LojaAPI:
    """Cliente falso. Cada chamada a obter_pedido conta uma tentativa.

    Regras, nesta ordem, com n = número da tentativa (1 na primeira):

    - id que começa com ``missing-``: sempre LojaErroCliente.
    - id que começa com ``down-``: sempre LojaIndisponivel.
    - id que começa com ``flaky-``: as primeiras ``(seed % 3) + 1`` tentativas
      levantam LojaIndisponivel; a seguinte devolve o pedido.
    - id que começa com ``slow-``: as primeiras ``(seed % 2) + 1`` tentativas
      dormem ATRASO_S segundos e só então devolvem o pedido. As demais
      devolvem na hora.
    - id que começa com ``timeout-``: toda tentativa dorme ATRASO_S e só
      então devolveria o pedido.
    - qualquer outro id: devolve o pedido na hora.

    ``tentativas(pedido_id)`` informa quantas vezes aquele id foi chamado.
    """

    ATRASO_S = ATRASO_S

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self._contagens: dict[str, int] = {}

    def tentativas(self, pedido_id: str) -> int:
        return self._contagens.get(pedido_id, 0)

    def obter_pedido(self, pedido_id: str) -> dict:
        if not isinstance(pedido_id, str) or pedido_id == "":
            raise LojaErroCliente("id invalido")
        self._contagens[pedido_id] = self._contagens.get(pedido_id, 0) + 1
        n = self._contagens[pedido_id]
        if pedido_id.startswith("missing-"):
            raise LojaErroCliente(f"404 {pedido_id}")
        if pedido_id.startswith("down-"):
            raise LojaIndisponivel("503")
        if pedido_id.startswith("flaky-"):
            if n <= (self.seed % 3) + 1:
                raise LojaIndisponivel("503")
            return payload_pedido(self.seed, pedido_id)
        if pedido_id.startswith("slow-"):
            if n <= (self.seed % 2) + 1:
                time.sleep(self.ATRASO_S)
            return payload_pedido(self.seed, pedido_id)
        if pedido_id.startswith("timeout-"):
            time.sleep(self.ATRASO_S)
            return payload_pedido(self.seed, pedido_id)
        return payload_pedido(self.seed, pedido_id)
