import csv
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_data(valor: str, nome_campo: str, linha: int) -> datetime:
    if not FORMATO_DATA.fullmatch(valor):
        raise ValueError(f"linha {linha}: {nome_campo} com formato inválido: {valor!r}")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M")
    except ValueError as erro:
        raise ValueError(f"linha {linha}: {nome_campo} inexistente: {valor!r}") from erro


def _ler_chamados(caminho_csv: str) -> list[dict]:
    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("arquivo de chamados vazio ou sem cabeçalho") from None
        if cabecalho != CABECALHO:
            raise ValueError(f"cabeçalho inválido: {cabecalho!r}")

        chamados = []
        ids = set()
        try:
            linhas = list(leitor)
        except csv.Error as erro:
            raise ValueError(f"CSV inválido: {erro}") from erro

    for numero, campos in enumerate(linhas, start=2):
        campos = [campo.strip() for campo in campos]
        if all(campo == "" for campo in campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {numero}: esperados {len(CABECALHO)} campos, veio {len(campos)}")

        id_chamado, equipe, aberto_em, fechado_em, prioridade = campos
        if not id_chamado:
            raise ValueError(f"linha {numero}: id vazio")
        if not equipe:
            raise ValueError(f"linha {numero}: equipe vazia")
        if id_chamado in ids:
            raise ValueError(f"linha {numero}: id duplicado: {id_chamado!r}")
        ids.add(id_chamado)

        inicio = _ler_data(aberto_em, "aberto_em", numero)
        fim = _ler_data(fechado_em, "fechado_em", numero)
        if fim < inicio:
            raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {numero}: prioridade inválida: {prioridade!r}")

        chamados.append(
            {
                "id": id_chamado,
                "equipe": equipe,
                "duracao_minutos": (fim - inicio) // timedelta(minutes=1),
                "prioridade": prioridade,
            }
        )
    return chamados


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as arquivo:
        try:
            dados = json.load(arquivo)
        except json.JSONDecodeError as erro:
            raise ValueError(f"JSON de SLA inválido: {erro}") from erro

    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("'limites_minutos' deve ter exatamente as prioridades baixa, media e alta")
    for prioridade in PRIORIDADES:
        limite = limites[prioridade]
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite de {prioridade!r} deve ser int >= 1: {limite!r}")
    return limites


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_sla(caminho_sla)

    grupos: dict[str, list[dict]] = {}
    for chamado in chamados:
        grupos.setdefault(chamado["equipe"], []).append(chamado)

    equipes = []
    for nome in sorted(grupos):
        itens = grupos[nome]
        total = len(itens)
        duracao_total = sum(item["duracao_minutos"] for item in itens)
        estourados = sum(
            1 for item in itens if item["duracao_minutos"] > limites[item["prioridade"]]
        )
        pior = min(itens, key=lambda item: (-item["duracao_minutos"], item["id"]))
        equipes.append(
            {
                "equipe": nome,
                "chamados": total,
                "estourados": estourados,
                "tempo_medio_minutos": duracao_total // total,
                "pior_id": pior["id"],
            }
        )

    resultado = {"equipes": equipes}
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
