import csv
import io
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
_RE_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_sla(caminho_sla):
    with open(caminho_sla, encoding="utf-8") as f:
        texto = f.read()

    def sem_duplicatas(pares):
        d = {}
        for k, v in pares:
            if k in d:
                raise ValueError(f"chave duplicada no SLA: {k!r}")
            d[k] = v
        return d

    def rejeitar_constante(nome):
        raise ValueError(f"constante inválida no SLA: {nome}")

    try:
        dados = json.loads(
            texto,
            object_pairs_hook=sem_duplicatas,
            parse_constant=rejeitar_constante,
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"SLA JSON inválido: {e}") from None
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for p, v in limites.items():
        if type(v) is not int or v < 1:
            raise ValueError(f"limite inválido para {p!r}: {v!r}")
    return dict(limites)


def _data(valor, campo, linha):
    if len(valor) != 16 or not _RE_DATA.fullmatch(valor):
        raise ValueError(f"linha {linha}: {campo} com formato inválido: {valor!r}")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError(f"linha {linha}: {campo} inexistente: {valor!r}") from None


def _ler_chamados(caminho_csv):
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        texto = f.read()
    try:
        linhas = list(csv.reader(io.StringIO(texto, newline="")))
    except csv.Error as e:
        raise ValueError(f"CSV inválido: {e}") from None

    if not linhas or linhas[0] != CABECALHO:
        raise ValueError("cabeçalho ausente ou diferente do esperado")

    chamados = []
    ids = set()
    for n, bruto in enumerate(linhas[1:], start=2):
        campos = [c.strip() for c in bruto]
        if all(c == "" for c in campos):
            continue
        if len(campos) != len(CABECALHO):
            raise ValueError(f"linha {n}: esperado {len(CABECALHO)} colunas, veio {len(campos)}")
        id_, equipe, aberto, fechado, prioridade = campos
        if not id_:
            raise ValueError(f"linha {n}: id vazio")
        if not equipe:
            raise ValueError(f"linha {n}: equipe vazia")
        if id_ in ids:
            raise ValueError(f"linha {n}: id duplicado: {id_!r}")
        ids.add(id_)
        inicio = _data(aberto, "aberto_em", n)
        fim = _data(fechado, "fechado_em", n)
        if fim < inicio:
            raise ValueError(f"linha {n}: fechado_em anterior a aberto_em")
        if prioridade not in PRIORIDADES:
            raise ValueError(f"linha {n}: prioridade inválida: {prioridade!r}")
        duracao = int((fim - inicio).total_seconds()) // 60
        chamados.append((id_, equipe, duracao, prioridade))
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)
    chamados = _ler_chamados(caminho_csv)

    grupos = {}
    for id_, equipe, duracao, prioridade in chamados:
        grupos.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for equipe in sorted(grupos):
        itens = grupos[equipe]
        total = sum(d for _, d, _ in itens)
        pior = min(itens, key=lambda t: (-t[1], t[0]))
        equipes.append({
            "equipe": equipe,
            "chamados": len(itens),
            "estourados": sum(1 for _, d, p in itens if d > limites[p]),
            "tempo_medio_minutos": total // len(itens),
            "pior_id": pior[0],
        })

    resultado = {"equipes": equipes}
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(conteudo)
    return json.loads(conteudo)
