from dataclasses import dataclass, field
import random
from typing import Any


class SimulatedNetworkError(Exception):
    """Simula perda transitória de conexão de rede."""
    pass


class SimulatedTimeoutError(Exception):
    """Simula timeout da requisição."""
    pass


@dataclass
class ApiResponse:
    status_code: int
    data: dict
    headers: dict = field(default_factory=dict)


class FakeApiServer:
    """Servidor mock determinístico em processo."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)
        self.chamadas: list[dict[str, Any]] = []
        self._falhas: dict[str, dict[str, Any]] = {}
        self._respostas: dict[str, ApiResponse] = {}

    def configurar_falhas(self, rota: str, qtd_falhas: int, tipo_falha: str = "network") -> None:
        """Configura quantidade e tipo de falha transitória antes de responder com sucesso."""
        self._falhas[rota] = {"qtd": qtd_falhas, "tipo": tipo_falha}

    def configurar_resposta(self, rota: str, status_code: int, data: dict) -> None:
        """Define a resposta padrão para uma rota."""
        self._respostas[rota] = ApiResponse(status_code=status_code, data=data)

    def requisicao(
        self,
        metodo: str,
        rota: str,
        payload: dict | None = None,
        timeout: float | None = None,
    ) -> ApiResponse:
        """Processa uma requisição simulada."""
        self.chamadas.append({
            "metodo": metodo,
            "rota": rota,
            "payload": payload,
            "timeout": timeout,
        })

        if rota in self._falhas:
            cfg = self._falhas[rota]
            if cfg["qtd"] > 0:
                cfg["qtd"] -= 1
                tipo = cfg["tipo"]
                if tipo == "network":
                    raise SimulatedNetworkError("Conexão interrompida com o servidor.")
                elif tipo == "timeout":
                    raise SimulatedTimeoutError("Operação excedeu o tempo limite configurado.")
                elif tipo == "503":
                    return ApiResponse(status_code=503, data={"erro": "Serviço Indisponível"})
                elif tipo == "429":
                    return ApiResponse(status_code=429, data={"erro": "Too Many Requests"})

        if rota in self._respostas:
            return self._respostas[rota]

        return ApiResponse(
            status_code=200,
            data={"status": "ok", "metodo": metodo, "rota": rota, "payload": payload},
        )
