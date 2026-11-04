import csv
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
FORMATO_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")


def _ler_data(valor: str) -> datetime:
    if not FORMATO_DATA.match(valor):
        raise ValueError(f"data fora do formato YYYY-MM-DDTHH:MM: {valor!r}")
    return datetime.strptime(valor, "%Y-%m-%dT%H:%M")


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as f:
        try:
            dados = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON de SLA inválido: {e}") from e

    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade in PRIORIDADES:
        limite = limites[prioridade]
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite de {prioridade} deve ser int >= 1")
    return limites


def _ler_chamados(caminho_csv: str) -> list[dict]:
    chamados = []
    ids_vistos = set()
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        try:
            linhas = csv.reader(f)
            cabecalho = next(linhas, None)
            if cabecalho is None:
                raise ValueError("arquivo vazio ou sem cabeçalho")
            if cabecalho != CABECALHO:
                raise ValueError(f"cabeçalho inválido: {cabecalho!r}")

            for numero, linha in enumerate(linhas, start=2):
                campos = [c.strip() for c in linha]
                if not any(campos):
                    continue
                if len(linha) != len(CABECALHO):
                    raise ValueError(f"linha {numero}: número de colunas diferente")

                id_, equipe, aberto, fechado, prioridade = campos
                if not id_ or not equipe:
                    raise ValueError(f"linha {numero}: id e equipe são obrigatórios")
                if id_ in ids_vistos:
                    raise ValueError(f"linha {numero}: id duplicado {id_!r}")
                ids_vistos.add(id_)

                inicio = _ler_data(aberto)
                fim = _ler_data(fechado)
                if fim < inicio:
                    raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
                if prioridade not in PRIORIDADES:
                    raise ValueError(f"linha {numero}: prioridade inválida {prioridade!r}")

                chamados.append({
                    "id": id_,
                    "equipe": equipe,
                    "duracao": int((fim - inicio).total_seconds()) // 60,
                    "prioridade": prioridade,
                })
        except csv.Error as e:
            raise ValueError(f"CSV inválido: {e}") from e
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_sla(caminho_sla)

    grupos = {}
    for chamado in chamados:
        grupos.setdefault(chamado["equipe"], []).append(chamado)

    equipes = []
    for nome in sorted(grupos):
        itens = grupos[nome]
        total = sum(c["duracao"] for c in itens)
        estourados = sum(
            1 for c in itens if c["duracao"] > limites[c["prioridade"]]
        )
        pior = min(itens, key=lambda c: (-c["duracao"], c["id"]))
        equipes.append({
            "equipe": nome,
            "chamados": len(itens),
            "estourados": estourados,
            "tempo_medio_minutos": total // len(itens),
            "pior_id": pior["id"],
        })

    resultado = {"equipes": equipes}
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
