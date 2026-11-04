"""Cliente HTTP com retry, backoff exponencial e timeout para FakeAPI."""

import math
import time
from typing import Any, Mapping

from fake_api import ErroConexao, TempoEsgotado


class ErroAPI(Exception):
    """Base dos erros do cliente."""

    def __init__(self, *args, status: int | None = None):
        if status is None and len(args) >= 2 and isinstance(args[-1], int) and not isinstance(args[-1], bool):
            status = args[-1]
            args = args[:-1]
        super().__init__(*args)
        if status is not None:
            self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (404)."""

    def __init__(self, *args, status: int = 404):
        super().__init__(*args, status=status)


class FalhaPermanente(ErroAPI):
    """Desistiu; atributo .tentativas: int."""

    def __init__(
        self,
        *args,
        tentativas: int | None = None,
        status: int | None = None,
    ):
        if tentativas is None:
            if len(args) >= 2 and isinstance(args[1], int) and not isinstance(args[1], bool):
                tentativas = args[1]
                args = (args[0],) + args[2:]
            elif len(args) == 1 and isinstance(args[0], int) and not isinstance(args[0], bool):
                tentativas = args[0]
                args = ()
            else:
                tentativas = 0
        super().__init__(*args, status=status)
        self.tentativas = tentativas


_STATUS_RETENTAVEIS = {429, 500, 502, 503, 504}


def _extrair_retry_after(resposta: Any) -> float | None:
    if resposta is None:
        return None
    headers = getattr(resposta, "headers", None)
    if not headers:
        return None

    raw = None
    if isinstance(headers, Mapping) or hasattr(headers, "items"):
        for k, v in headers.items():
            if isinstance(k, str) and k.lower() == "retry-after":
                raw = v
                break
    elif isinstance(headers, (list, tuple)):
        for item in headers:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                k, v = item[0], item[1]
                if isinstance(k, str) and k.lower() == "retry-after":
                    raw = v
                    break

    if raw is None and hasattr(headers, "get"):
        raw = headers.get("retry-after") or headers.get("Retry-After")

    if raw is None or isinstance(raw, bool):
        return None

    try:
        val = float(raw)
        if math.isfinite(val) and val >= 0:
            return val
    except (ValueError, TypeError):
        return None

    return None


class ClienteAPI:
    """Cliente para API de usuários com retry, backoff e timeout."""

    def __init__(
        self,
        api: Any,
        max_tentativas: int = 4,
        backoff_base: float = 0.5,
        backoff_max: float = 8.0,
        timeout: float = 2.0,
        dormir=time.sleep,
        orcamento_espera: float | None = None,
    ) -> None:
        if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int) or max_tentativas < 1:
            raise ValueError(f"max_tentativas deve ser int >= 1, recebido: {max_tentativas!r}")

        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or math.isnan(timeout) or timeout <= 0:
            raise ValueError(f"timeout deve ser float > 0, recebido: {timeout!r}")

        if isinstance(backoff_base, bool) or not isinstance(backoff_base, (int, float)) or math.isnan(backoff_base) or backoff_base < 0:
            raise ValueError(f"backoff_base deve ser float >= 0, recebido: {backoff_base!r}")

        if isinstance(backoff_max, bool) or not isinstance(backoff_max, (int, float)) or math.isnan(backoff_max) or backoff_max < 0:
            raise ValueError(f"backoff_max deve ser float >= 0, recebido: {backoff_max!r}")

        if orcamento_espera is not None:
            if (
                isinstance(orcamento_espera, bool)
                or not isinstance(orcamento_espera, (int, float))
                or math.isnan(orcamento_espera)
                or orcamento_espera < 0
            ):
                raise ValueError(f"orcamento_espera deve ser float >= 0 ou None, recebido: {orcamento_espera!r}")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = float(backoff_base)
        self.backoff_max = float(backoff_max)
        self.timeout = float(timeout)
        self.dormir = dormir
        self.orcamento_espera = float(orcamento_espera) if orcamento_espera is not None else None

    def _calcular_backoff(self, n: int) -> float:
        if self.backoff_base == 0.0 or self.backoff_max == 0.0:
            return 0.0
        if n - 1 > 2100:
            return self.backoff_max
        try:
            val = self.backoff_base * (2 ** (n - 1))
            return min(self.backoff_max, float(val))
        except OverflowError:
            return self.backoff_max

    def obter_usuario(self, id_usuario: int) -> dict:
        if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
            raise ValueError(f"id inválido: {id_usuario!r}")

        tentativas = 0
        soma_esperas = 0.0
        ultimo_erro = None
        ultimo_status = None

        while tentativas < self.max_tentativas:
            tentativas += 1
            ultimo_erro = None
            ultimo_status = None

            try:
                resposta = self.api.requisitar("GET", f"/usuarios/{id_usuario}", timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as erro:
                ultimo_erro = erro
            else:
                status = getattr(resposta, "status", None)
                if status == 200:
                    return resposta.corpo
                elif status == 404:
                    raise NaoEncontrado("Usuário não encontrado", status=404) from None
                elif status in _STATUS_RETENTAVEIS:
                    ultimo_status = status
                else:
                    raise ErroAPI(f"Erro na API com status {status}", status=status) from None

            # Se chegou aqui, a tentativa falhou com erro retentável
            if tentativas == self.max_tentativas:
                break

            # Calcular próxima espera após a falha n (com n = tentativas)
            if ultimo_status == 429:
                retry_after = _extrair_retry_after(resposta)
                if retry_after is not None:
                    espera = min(self.backoff_max, retry_after)
                else:
                    espera = self._calcular_backoff(tentativas)
            else:
                espera = self._calcular_backoff(tentativas)

            # Verificar orçamento de espera
            if self.orcamento_espera is not None and (soma_esperas + espera) > self.orcamento_espera:
                if ultimo_erro is not None:
                    raise FalhaPermanente(
                        f"Orçamento de espera excedido ({soma_esperas + espera} > {self.orcamento_espera}) após {tentativas} tentativas",
                        tentativas=tentativas,
                        status=ultimo_status,
                    ) from ultimo_erro
                else:
                    raise FalhaPermanente(
                        f"Orçamento de espera excedido ({soma_esperas + espera} > {self.orcamento_espera}) após {tentativas} tentativas",
                        tentativas=tentativas,
                        status=ultimo_status,
                    ) from None

            soma_esperas += espera
            self.dormir(espera)

        # Tentativas esgotadas
        if ultimo_erro is not None:
            raise FalhaPermanente(
                f"Máximo de tentativas ({tentativas}) atingido",
                tentativas=tentativas,
                status=ultimo_status,
            ) from ultimo_erro
        else:
            raise FalhaPermanente(
                f"Máximo de tentativas ({tentativas}) atingido",
                tentativas=tentativas,
                status=ultimo_status,
            ) from None

    def obter_varios(self, ids) -> dict[int, dict | None]:
        lista_ids = list(ids)
        for id_item in lista_ids:
            if isinstance(id_item, bool) or not isinstance(id_item, int) or id_item < 1:
                raise ValueError(f"id inválido: {id_item!r}")

        resultado: dict[int, dict | None] = {}
        for id_usuario in dict.fromkeys(lista_ids):
            try:
                resultado[id_usuario] = self.obter_usuario(id_usuario)
            except NaoEncontrado:
                resultado[id_usuario] = None

        return resultado
