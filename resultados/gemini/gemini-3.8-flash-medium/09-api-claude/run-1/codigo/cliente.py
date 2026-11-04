"""Cliente HTTP com retry, backoff e timeout para API de usuários simulada."""

from __future__ import annotations

import math
import time

from fake_api import ErroConexao, TempoEsgotado

STATUS_RETENTAVEIS = {429, 500, 502, 503, 504}


class ErroAPI(Exception):
    """Base dos erros do cliente."""

    def __init__(self, *args, status: int | None = None, **kwargs):
        if status is None and len(args) > 1 and isinstance(args[1], int) and not isinstance(args[1], bool):
            status = args[1]
            args = (args[0],)
        elif status is None and len(args) == 1 and isinstance(args[0], int) and not isinstance(args[0], bool):
            status = args[0]
        super().__init__(*args, **kwargs)
        self.status = status


class NaoEncontrado(ErroAPI):
    """Recurso inexistente (404)."""

    def __init__(self, *args, status: int | None = None, **kwargs):
        if status is None:
            for arg in args:
                if isinstance(arg, int) and not isinstance(arg, bool):
                    status = arg
                    break
            if status is None:
                status = 404
        super().__init__(*args, status=status, **kwargs)


class FalhaPermanente(ErroAPI):
    """Desistiu das tentativas; possui o atributo .tentativas: int."""

    def __init__(self, *args, tentativas: int | None = None, status: int | None = None, **kwargs):
        if tentativas is None:
            for arg in args:
                if isinstance(arg, int) and not isinstance(arg, bool):
                    tentativas = arg
                    break
            if tentativas is None:
                tentativas = 0
        super().__init__(*args, status=status, **kwargs)
        self.tentativas = tentativas


def _calcular_backoff(backoff_base: float, backoff_max: float, n: int) -> float:
    if backoff_base == 0:
        return min(float(backoff_max), 0.0)
    if n - 1 > 1050:
        return float(backoff_max)
    try:
        val = backoff_base * (2 ** (n - 1))
        return min(float(backoff_max), float(val))
    except OverflowError:
        return float(backoff_max)


def _extrair_retry_after(headers) -> float | None:
    if not headers:
        return None
    val_raw = None
    if hasattr(headers, "items"):
        for k, v in headers.items():
            if isinstance(k, str) and k.lower() == "retry-after":
                val_raw = v
                break
    elif isinstance(headers, (list, tuple)):
        for item in headers:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                k, v = item
                if isinstance(k, str) and k.lower() == "retry-after":
                    val_raw = v
                    break
    elif hasattr(headers, "get"):
        val_raw = headers.get("retry-after") or headers.get("Retry-After")

    if val_raw is None or isinstance(val_raw, bool):
        return None

    try:
        val = float(val_raw)
    except (ValueError, TypeError):
        return None

    if not math.isfinite(val) or val < 0:
        return None

    return val


class ClienteAPI:
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
        if isinstance(max_tentativas, bool) or not isinstance(max_tentativas, int) or max_tentativas < 1:
            raise ValueError("max_tentativas deve ser um inteiro >= 1")

        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0 or math.isnan(timeout):
            raise ValueError("timeout deve ser > 0")

        if isinstance(backoff_base, bool) or not isinstance(backoff_base, (int, float)) or backoff_base < 0 or math.isnan(backoff_base):
            raise ValueError("backoff_base deve ser >= 0")

        if isinstance(backoff_max, bool) or not isinstance(backoff_max, (int, float)) or backoff_max < 0 or math.isnan(backoff_max):
            raise ValueError("backoff_max deve ser >= 0")

        if orcamento_espera is not None:
            if isinstance(orcamento_espera, bool) or not isinstance(orcamento_espera, (int, float)) or orcamento_espera < 0 or math.isnan(orcamento_espera):
                raise ValueError("orcamento_espera deve ser >= 0 ou None")

        self.api = api
        self.max_tentativas = max_tentativas
        self.backoff_base = float(backoff_base)
        self.backoff_max = float(backoff_max)
        self.timeout = float(timeout)
        self.dormir = dormir
        self.orcamento_espera = float(orcamento_espera) if orcamento_espera is not None else None

    def obter_usuario(self, id_usuario: int) -> dict:
        if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario < 1:
            raise ValueError("id_usuario deve ser um int >= 1")

        tentativas_feitas = 0
        soma_esperas = 0.0
        ultima_falha_excecao: Exception | None = None
        ultimo_status: int | None = None

        for n in range(1, self.max_tentativas + 1):
            tentativas_feitas = n
            resposta = None
            erro_excecao = None

            try:
                resposta = self.api.requisitar("GET", f"/usuarios/{id_usuario}", timeout=self.timeout)
            except (ErroConexao, TempoEsgotado) as exc:
                erro_excecao = exc

            if erro_excecao is None and resposta is not None:
                status = resposta.status
                if status == 200:
                    return resposta.corpo
                if status == 404:
                    raise NaoEncontrado(f"Usuário {id_usuario} não encontrado", status=status)
                if status not in STATUS_RETENTAVEIS:
                    raise ErroAPI(f"Erro HTTP {status}", status=status)

                ultima_falha_excecao = None
                ultimo_status = status
                ultima_resposta = resposta
            else:
                ultima_falha_excecao = erro_excecao
                ultimo_status = None
                ultima_resposta = None

            if n == self.max_tentativas:
                break

            espera = None
            if ultimo_status == 429 and ultima_resposta is not None:
                ra = _extrair_retry_after(getattr(ultima_resposta, "headers", None))
                if ra is not None:
                    espera = min(self.backoff_max, float(ra))

            if espera is None:
                espera = _calcular_backoff(self.backoff_base, self.backoff_max, n)

            if self.orcamento_espera is not None:
                nova_soma = soma_esperas + espera
                if nova_soma > self.orcamento_espera and not math.isclose(nova_soma, self.orcamento_espera, rel_tol=1e-9, abs_tol=1e-9):
                    break

            self.dormir(espera)
            soma_esperas += espera

        if ultima_falha_excecao is not None:
            raise FalhaPermanente(
                f"Falha permanente ao obter usuário {id_usuario} após {tentativas_feitas} tentativa(s)",
                tentativas=tentativas_feitas,
                status=None,
            ) from ultima_falha_excecao
        else:
            raise FalhaPermanente(
                f"Falha permanente ao obter usuário {id_usuario} após {tentativas_feitas} tentativa(s) (HTTP {ultimo_status})",
                tentativas=tentativas_feitas,
                status=ultimo_status,
            ) from None

    def obter_varios(self, ids) -> dict[int, dict | None]:
        lista_ids = list(ids)
        for uid in lista_ids:
            if isinstance(uid, bool) or not isinstance(uid, int) or uid < 1:
                raise ValueError(f"ID inválido: {uid!r}")

        resultado: dict[int, dict | None] = {}
        for uid in dict.fromkeys(lista_ids).keys():
            try:
                resultado[uid] = self.obter_usuario(uid)
            except NaoEncontrado:
                resultado[uid] = None

        return resultado
