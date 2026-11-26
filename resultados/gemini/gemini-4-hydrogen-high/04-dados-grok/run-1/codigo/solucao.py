from __future__ import annotations

import csv
import json
import re
from datetime import datetime

CABECALHO_ESPERADO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES_VALIDAS = frozenset({"baixa", "media", "alta"})
PADRAO_DATA_HORA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _carregar_sla(caminho_sla: str) -> dict[str, int]:
    with open(caminho_sla, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, dict) or set(dados.keys()) != {"limites_minutos"}:
        raise ValueError("SLA deve ser um objeto JSON com exatamente a chave 'limites_minutos'.")

    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites.keys()) != PRIORIDADES_VALIDAS:
        raise ValueError("'limites_minutos' deve conter exatamente as prioridades baixa, media e alta.")

    resultado: dict[str, int] = {}
    for prioridade in PRIORIDADES_VALIDAS:
        limite = limites[prioridade]
        if isinstance(limite, bool) or not isinstance(limite, int) or limite < 1:
            raise ValueError(f"Limite inválido para prioridade '{prioridade}': deve ser int >= 1.")
        resultado[prioridade] = limite

    return resultado


def _analisar_data_hora(valor: str) -> datetime:
    if PADRAO_DATA_HORA.fullmatch(valor) is None:
        raise ValueError(f"Data/hora fora do formato YYYY-MM-DDTHH:MM: {valor!r}")
    return datetime.strptime(valor, "%Y-%m-%dT%H:%M")


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _carregar_sla(caminho_sla)

    ids_vistos: set[str] = set()
    agregado: dict[str, dict[str, int | str]] = {}

    try:
        with open(caminho_csv, "r", encoding="utf-8", newline="") as arquivo:
            leitor = csv.reader(arquivo)
            cabecalho = next(leitor, None)
            if cabecalho != CABECALHO_ESPERADO:
                raise ValueError("Cabeçalho CSV ausente ou diferente do esperado.")

            for linha in leitor:
                if not linha or all(campo.strip() == "" for campo in linha):
                    continue

                if len(linha) != 5:
                    raise ValueError(f"Linha com número inválido de colunas: {len(linha)}.")

                id_chamado, equipe, aberto_str, fechado_str, prioridade = (
                    campo.strip() for campo in linha
                )

                if not id_chamado or not equipe:
                    raise ValueError("'id' e 'equipe' não podem ficar vazios.")

                if id_chamado in ids_vistos:
                    raise ValueError(f"ID de chamado duplicado: {id_chamado!r}")
                ids_vistos.add(id_chamado)

                if prioridade not in limites:
                    raise ValueError(f"Prioridade inválida: {prioridade!r}")

                aberto_em = _analisar_data_hora(aberto_str)
                fechado_em = _analisar_data_hora(fechado_str)
                if fechado_em < aberto_em:
                    raise ValueError("Data/hora de fechamento anterior à de abertura.")

                delta = fechado_em - aberto_em
                duracao_minutos = delta.days * 1440 + (delta.seconds // 60)
                estourou = 1 if duracao_minutos > limites[prioridade] else 0

                if equipe not in agregado:
                    agregado[equipe] = {
                        "chamados": 1,
                        "estourados": estourou,
                        "soma_duracao": duracao_minutos,
                        "maior_duracao": duracao_minutos,
                        "pior_id": id_chamado,
                    }
                else:
                    stats = agregado[equipe]
                    stats["chamados"] = int(stats["chamados"]) + 1
                    stats["estourados"] = int(stats["estourados"]) + estourou
                    stats["soma_duracao"] = int(stats["soma_duracao"]) + duracao_minutos
                    maior_duracao = int(stats["maior_duracao"])
                    pior_id = str(stats["pior_id"])
                    if duracao_minutos > maior_duracao or (
                        duracao_minutos == maior_duracao and id_chamado < pior_id
                    ):
                        stats["maior_duracao"] = duracao_minutos
                        stats["pior_id"] = id_chamado
    except csv.Error as exc:
        raise ValueError(f"CSV malformado: {exc}") from exc

    equipes = []
    for equipe in sorted(agregado):
        stats = agregado[equipe]
        chamados = int(stats["chamados"])
        estourados = int(stats["estourados"])
        soma_duracao = int(stats["soma_duracao"])
        equipes.append(
            {
                "equipe": equipe,
                "chamados": chamados,
                "estourados": estourados,
                "tempo_medio_minutos": soma_duracao // chamados,
                "pior_id": str(stats["pior_id"]),
            }
        )

    resultado = {"equipes": equipes}
    conteudo_json = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8") as arquivo_saida:
        arquivo_saida.write(conteudo_json)

    return resultado
