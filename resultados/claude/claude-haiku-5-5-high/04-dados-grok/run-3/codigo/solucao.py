import csv
import json
import re
from datetime import datetime, timedelta

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")
UM_MINUTO = timedelta(minutes=1)


def _instante(texto: str) -> datetime:
    if not FORMATO_DATA.fullmatch(texto):
        raise ValueError(f"data fora do formato YYYY-MM-DDTHH:MM: {texto!r}")
    return datetime.strptime(texto, "%Y-%m-%dT%H:%M")


def _ler_chamados(caminho_csv: str) -> list:
    chamados = []
    ids = set()
    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            if next(leitor, None) != CABECALHO:
                raise ValueError("cabeçalho do CSV diferente do esperado")
            for campos in leitor:
                if all(campo.strip() == "" for campo in campos):
                    continue
                if len(campos) != len(CABECALHO):
                    raise ValueError(f"linha {leitor.line_num}: número de colunas inválido")
                id_, equipe, aberto_em, fechado_em, prioridade = [c.strip() for c in campos]
                if not id_:
                    raise ValueError(f"linha {leitor.line_num}: id vazio")
                if not equipe:
                    raise ValueError(f"linha {leitor.line_num}: equipe vazia")
                if id_ in ids:
                    raise ValueError(f"id duplicado: {id_!r}")
                ids.add(id_)
                if prioridade not in PRIORIDADES:
                    raise ValueError(f"linha {leitor.line_num}: prioridade inválida: {prioridade!r}")
                inicio = _instante(aberto_em)
                fim = _instante(fechado_em)
                if fim < inicio:
                    raise ValueError(f"linha {leitor.line_num}: fechado_em anterior a aberto_em")
                chamados.append((id_, equipe, (fim - inicio) // UM_MINUTO, prioridade))
        except csv.Error as erro:
            raise ValueError(f"CSV inválido: {erro}") from erro
    return chamados


def _ler_limites(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter somente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("'limites_minutos' deve ter exatamente baixa, media e alta")
    for prioridade in PRIORIDADES:
        limite = limites[prioridade]
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite de {prioridade!r} deve ser int >= 1")
    return limites


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_limites(caminho_sla)

    por_equipe = {}
    for id_, equipe, duracao, prioridade in chamados:
        por_equipe.setdefault(equipe, []).append((id_, duracao, prioridade))

    equipes = []
    for nome in sorted(por_equipe):
        itens = por_equipe[nome]
        equipes.append({
            "equipe": nome,
            "chamados": len(itens),
            "estourados": sum(1 for _, duracao, prioridade in itens if duracao > limites[prioridade]),
            "tempo_medio_minutos": sum(duracao for _, duracao, _ in itens) // len(itens),
            "pior_id": min(itens, key=lambda item: (-item[1], item[0]))[0],
        })

    resultado = {"equipes": equipes}
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(texto)
    return resultado
