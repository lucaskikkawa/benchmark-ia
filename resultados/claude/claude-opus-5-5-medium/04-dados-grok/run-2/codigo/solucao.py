import csv
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_sla(caminho_sla):
    with open(caminho_sla, encoding="utf-8") as f:
        texto = f.read()
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"SLA JSON inválido: {e}") from None
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade, limite in limites.items():
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite inválido para {prioridade!r}: {limite!r}")
    return dict(limites)


def _data(valor, campo, numero_linha):
    if not _FORMATO_DATA.fullmatch(valor):
        raise ValueError(f"linha {numero_linha}: {campo} com formato inválido: {valor!r}")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError(f"linha {numero_linha}: {campo} inexistente: {valor!r}") from None


def _ler_chamados(caminho_csv):
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        try:
            linhas = list(csv.reader(f, strict=True))
        except csv.Error as e:
            raise ValueError(f"CSV inválido: {e}") from None
    if not linhas:
        raise ValueError("CSV vazio")
    if linhas[0] != CABECALHO:
        raise ValueError(f"cabeçalho inválido: {linhas[0]!r}")

    chamados = []
    ids = set()
    for numero_linha, linha in enumerate(linhas[1:], start=2):
        campos = [c.strip() for c in linha]
        if all(c == "" for c in campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {numero_linha}: esperado {len(CABECALHO)} colunas, veio {len(campos)}")
        id_, equipe, aberto_em, fechado_em, prioridade = campos
        if not id_:
            raise ValueError(f"linha {numero_linha}: id vazio")
        if not equipe:
            raise ValueError(f"linha {numero_linha}: equipe vazia")
        if id_ in ids:
            raise ValueError(f"linha {numero_linha}: id duplicado: {id_!r}")
        ids.add(id_)
        aberto = _data(aberto_em, "aberto_em", numero_linha)
        fechado = _data(fechado_em, "fechado_em", numero_linha)
        if fechado < aberto:
            raise ValueError(f"linha {numero_linha}: fechado_em anterior a aberto_em")
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {numero_linha}: prioridade inválida: {prioridade!r}")
        duracao = int((fechado - aberto).total_seconds()) // 60
        chamados.append((id_, equipe, duracao, prioridade))
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)
    chamados = _ler_chamados(caminho_csv)

    por_equipe = {}
    for id_, equipe, duracao, prioridade in chamados:
        por_equipe.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for equipe in sorted(por_equipe):
        itens = por_equipe[equipe]
        soma = sum(d for _, d, _ in itens)
        estourados = sum(1 for _, d, p in itens if d > limites[p])
        pior_id = min(itens, key=lambda item: (-item[1], item[0]))[0]
        equipes.append({
            "equipe": equipe,
            "chamados": len(itens),
            "estourados": estourados,
            "tempo_medio_minutos": soma // len(itens),
            "pior_id": pior_id,
        })

    resultado = {"equipes": equipes}
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(texto)
    return json.loads(texto)
