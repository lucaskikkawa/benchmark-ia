import csv
import io
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_UM_MINUTO = timedelta(minutes=1)
_RE_DATA = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2})")


def _ler_texto(caminho):
    with open(caminho, "r", encoding="utf-8", newline="") as f:
        return f.read()


def _data(texto):
    m = _RE_DATA.fullmatch(texto)
    if m is None:
        raise ValueError(f"data em formato inválido: {texto!r}")
    try:
        return datetime(*(int(g) for g in m.groups()))
    except ValueError as e:
        raise ValueError(f"data inexistente: {texto!r}") from e


def _validar_sla(texto):
    if not texto.strip():
        raise ValueError("SLA vazio")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"SLA com JSON inválido: {e}") from e
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade, limite in limites.items():
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite inválido para {prioridade!r}: {limite!r}")
    return dict(limites)


def _ler_chamados(texto):
    try:
        linhas = list(csv.reader(io.StringIO(texto, newline="")))
    except csv.Error as e:
        raise ValueError(f"CSV inválido: {e}") from e
    if not linhas:
        raise ValueError("CSV vazio")
    if linhas[0] != CABECALHO:
        raise ValueError(f"cabeçalho inválido: {linhas[0]!r}")

    chamados = []
    ids = set()
    for numero, linha in enumerate(linhas[1:], start=2):
        campos = [c.strip() for c in linha]
        if all(c == "" for c in campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {numero}: esperado {len(CABECALHO)} colunas, obtido {len(campos)}")
        id_, equipe, aberto_em, fechado_em, prioridade = campos
        if not id_:
            raise ValueError(f"linha {numero}: id vazio")
        if not equipe:
            raise ValueError(f"linha {numero}: equipe vazia")
        if id_ in ids:
            raise ValueError(f"linha {numero}: id duplicado {id_!r}")
        ids.add(id_)
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {numero}: prioridade inválida {prioridade!r}")
        aberto = _data(aberto_em)
        fechado = _data(fechado_em)
        if fechado < aberto:
            raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
        duracao = (fechado - aberto) // _UM_MINUTO
        chamados.append((id_, equipe, duracao, prioridade))
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    texto_csv = _ler_texto(caminho_csv)
    texto_sla = _ler_texto(caminho_sla)

    limites = _validar_sla(texto_sla)
    chamados = _ler_chamados(texto_csv)

    por_equipe = {}
    for id_, equipe, duracao, prioridade in chamados:
        por_equipe.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for equipe in sorted(por_equipe):
        itens = por_equipe[equipe]
        total = sum(d for _, d, _ in itens)
        estourados = sum(1 for _, d, p in itens if d > limites[p])
        pior_id = min(itens, key=lambda t: (-t[1], t[0]))[0]
        equipes.append({
            "equipe": equipe,
            "chamados": len(itens),
            "estourados": estourados,
            "tempo_medio_minutos": total // len(itens),
            "pior_id": pior_id,
        })

    resultado = {"equipes": equipes}
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(conteudo)
    return json.loads(conteudo)
