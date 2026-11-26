from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from typing import Any

_CABECALHO_ESPERADO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES_VALIDAS = frozenset({"baixa", "media", "alta"})
_FORMATO_DATA_HORA_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}", re.ASCII
)


def _carregar_sem_chaves_duplicadas(
    pares: list[tuple[str, Any]],
) -> dict[str, Any]:
    objeto: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Chave duplicada no JSON de SLA: {chave!r}")
        objeto[chave] = valor
    return objeto


def _carregar_sla(conteudo: str) -> dict[str, int]:
    try:
        dados = json.loads(
            conteudo, object_pairs_hook=_carregar_sem_chaves_duplicadas
        )
    except json.JSONDecodeError as exc:
        raise ValueError("JSON de SLA inválido.") from exc

    if not isinstance(dados, dict) or set(dados.keys()) != {"limites_minutos"}:
        raise ValueError(
            "JSON de SLA deve conter exatamente a chave 'limites_minutos'."
        )

    limites = dados["limites_minutos"]
    if (
        not isinstance(limites, dict)
        or set(limites.keys()) != _PRIORIDADES_VALIDAS
    ):
        raise ValueError(
            "'limites_minutos' deve conter exatamente 'baixa', 'media' e 'alta'."
        )

    limites_validados: dict[str, int] = {}
    for prioridade, limite in limites.items():
        if isinstance(limite, bool) or not isinstance(limite, int) or limite < 1:
            raise ValueError(
                f"Limite inválido para prioridade {prioridade!r}: {limite!r}"
            )
        limites_validados[prioridade] = limite

    return limites_validados


def _parse_data_hora(valor: str) -> datetime:
    if _FORMATO_DATA_HORA_RE.fullmatch(valor) is None:
        raise ValueError(f"Data/hora em formato inválido: {valor!r}")

    ano = int(valor[0:4])
    mes = int(valor[5:7])
    dia = int(valor[8:10])
    hora = int(valor[11:13])
    minuto = int(valor[14:16])
    return datetime(ano, mes, dia, hora, minuto)


def consolidar(
    caminho_csv: str, caminho_sla: str, caminho_saida: str
) -> dict[str, Any]:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    ids_vistos: set[str] = set()
    # equipe -> [chamados, estourados, soma_duracoes, pior_duracao, pior_id]
    agregado: dict[str, list[Any]] = {}

    with (
        open(caminho_csv, "r", encoding="utf-8", newline="") as arquivo_csv,
        open(caminho_sla, "r", encoding="utf-8") as arquivo_sla,
    ):
        limites = _carregar_sla(arquivo_sla.read())

        leitor = csv.reader(arquivo_csv)
        try:
            cabecalho = next(leitor, None)
        except csv.Error as exc:
            raise ValueError("CSV inválido.") from exc

        if cabecalho != _CABECALHO_ESPERADO:
            raise ValueError(
                f"Cabeçalho CSV inválido: {cabecalho!r}"
            )

        try:
            for linha in leitor:
                if not linha or all(campo.strip() == "" for campo in linha):
                    continue

                if len(linha) != len(_CABECALHO_ESPERADO):
                    raise ValueError(
                        f"Número de colunas inválido na linha: {linha!r}"
                    )

                chamado_id, equipe, aberto_str, fechado_str, prioridade = (
                    campo.strip() for campo in linha
                )

                if not chamado_id:
                    raise ValueError("Campo 'id' vazio.")
                if not equipe:
                    raise ValueError("Campo 'equipe' vazio.")
                if chamado_id in ids_vistos:
                    raise ValueError(f"ID duplicado: {chamado_id!r}")
                ids_vistos.add(chamado_id)

                if prioridade not in limites:
                    raise ValueError(f"Prioridade inválida: {prioridade!r}")

                aberto_em = _parse_data_hora(aberto_str)
                fechado_em = _parse_data_hora(fechado_str)
                if fechado_em < aberto_em:
                    raise ValueError(
                        f"'fechado_em' anterior a 'aberto_em' no chamado {chamado_id!r}"
                    )

                delta = fechado_em - aberto_em
                duracao_minutos = delta.days * 1440 + delta.seconds // 60
                estourou = 1 if duracao_minutos > limites[prioridade] else 0

                if equipe not in agregado:
                    agregado[equipe] = [
                        1,
                        estourou,
                        duracao_minutos,
                        duracao_minutos,
                        chamado_id,
                    ]
                else:
                    stats = agregado[equipe]
                    stats[0] += 1
                    stats[1] += estourou
                    stats[2] += duracao_minutos
                    if duracao_minutos > stats[3] or (
                        duracao_minutos == stats[3] and chamado_id < stats[4]
                    ):
                        stats[3] = duracao_minutos
                        stats[4] = chamado_id
        except csv.Error as exc:
            raise ValueError("CSV inválido.") from exc

    equipes_resumo: list[dict[str, Any]] = []
    for nome_equipe in sorted(agregado.keys()):
        chamados, estourados, soma_duracoes, _, pior_id = agregado[nome_equipe]
        equipes_resumo.append(
            {
                "equipe": nome_equipe,
                "chamados": chamados,
                "estourados": estourados,
                "tempo_medio_minutos": soma_duracoes // chamados,
                "pior_id": pior_id,
            }
        )

    resultado: dict[str, Any] = {"equipes": equipes_resumo}
    texto_saida = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"

    with open(caminho_saida, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto_saida)

    return resultado
