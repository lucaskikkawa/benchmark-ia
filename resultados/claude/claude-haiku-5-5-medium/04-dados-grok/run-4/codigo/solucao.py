import csv
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_sla(caminho_sla):
    with open(caminho_sla, encoding="utf-8") as f:
        texto = f.read()
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"SLA JSON inválido: {e}") from e
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("limites_minutos deve ter exatamente baixa, media e alta")
    for prioridade in PRIORIDADES:
        valor = limites[prioridade]
        if type(valor) is not int or valor < 1:
            raise ValueError(f"limite de {prioridade} deve ser int >= 1")
    return dict(limites)


def _data(texto):
    if not FORMATO_DATA.fullmatch(texto):
        raise ValueError(f"data fora do formato YYYY-MM-DDTHH:MM: {texto!r}")
    return datetime.strptime(texto, "%Y-%m-%dT%H:%M")


def _ler_chamados(caminho_csv):
    chamados = []
    ids = set()
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        try:
            cabecalho_lido = False
            for linha in csv.reader(f):
                if not cabecalho_lido:
                    if not linha:
                        continue
                    if linha != CABECALHO:
                        raise ValueError(f"cabeçalho inválido: {linha!r}")
                    cabecalho_lido = True
                    continue

                campos = [c.strip() for c in linha]
                if not any(campos):
                    continue
                if len(campos) != len(CABECALHO):
                    raise ValueError(f"número de colunas inválido: {linha!r}")

                id_, equipe, aberto, fechado, prioridade = campos
                if not id_ or not equipe:
                    raise ValueError("id e equipe não podem ser vazios")
                if id_ in ids:
                    raise ValueError(f"id duplicado: {id_!r}")
                ids.add(id_)

                inicio = _data(aberto)
                fim = _data(fechado)
                if fim < inicio:
                    raise ValueError(f"fechado_em anterior a aberto_em: {id_!r}")
                if prioridade not in PRIORIDADES:
                    raise ValueError(f"prioridade inválida: {prioridade!r}")

                chamados.append({
                    "id": id_,
                    "equipe": equipe,
                    "duracao": (fim - inicio) // timedelta(minutes=1),
                    "prioridade": prioridade,
                })
            if not cabecalho_lido:
                raise ValueError("arquivo sem cabeçalho")
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
        soma = sum(c["duracao"] for c in itens)
        estourados = sum(1 for c in itens if c["duracao"] > limites[c["prioridade"]])
        pior = min(itens, key=lambda c: (-c["duracao"], c["id"]))
        equipes.append({
            "equipe": nome,
            "chamados": len(itens),
            "estourados": estourados,
            "tempo_medio_minutos": soma // len(itens),
            "pior_id": pior["id"],
        })

    resultado = {"equipes": equipes}
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        f.write(conteudo)
    return resultado
