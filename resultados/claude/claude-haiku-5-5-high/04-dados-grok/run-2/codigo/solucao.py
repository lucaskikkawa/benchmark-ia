import csv
import json
import re
from datetime import datetime

CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES = ("baixa", "media", "alta")
FORMATO_DATA = "%Y-%m-%dT%H:%M"
REGEX_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}")


def _ler_sla(caminho_sla: str) -> dict:
    with open(caminho_sla, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("SLA deve ter exatamente a chave 'limites_minutos'")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(PRIORIDADES):
        raise ValueError("'limites_minutos' deve ter exatamente baixa, media e alta")
    for prioridade in PRIORIDADES:
        limite = limites[prioridade]
        if type(limite) is not int or limite < 1:
            raise ValueError(f"limite de {prioridade!r} deve ser int >= 1")
    return limites


def _ler_instante(texto: str, campo: str) -> datetime:
    if not REGEX_DATA.fullmatch(texto):
        raise ValueError(f"{campo} fora do formato YYYY-MM-DDTHH:MM: {texto!r}")
    try:
        return datetime.strptime(texto, FORMATO_DATA)
    except ValueError:
        raise ValueError(f"{campo} inexistente: {texto!r}") from None


def _ler_chamados(caminho_csv: str) -> list[dict]:
    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("arquivo de chamados vazio") from None
        if cabecalho != CABECALHO:
            raise ValueError(f"cabeçalho inesperado: {cabecalho!r}")

        ids = set()
        chamados = []
        for linha in leitor:
            numero = leitor.line_num
            campos = [campo.strip() for campo in linha]
            if not any(campos):
                continue
            if len(linha) != len(CABECALHO):
                raise ValueError(
                    f"linha {numero}: esperados {len(CABECALHO)} campos, vieram {len(linha)}"
                )

            id_, equipe, aberto_texto, fechado_texto, prioridade = campos
            if not id_ or not equipe:
                raise ValueError(f"linha {numero}: id e equipe são obrigatórios")
            if id_ in ids:
                raise ValueError(f"id duplicado: {id_!r}")
            ids.add(id_)

            aberto = _ler_instante(aberto_texto, "aberto_em")
            fechado = _ler_instante(fechado_texto, "fechado_em")
            if fechado < aberto:
                raise ValueError(f"linha {numero}: fechado_em anterior a aberto_em")
            if prioridade not in PRIORIDADES:
                raise ValueError(f"linha {numero}: prioridade inválida: {prioridade!r}")

            chamados.append(
                {
                    "id": id_,
                    "equipe": equipe,
                    "duracao": int((fechado - aberto).total_seconds()) // 60,
                    "prioridade": prioridade,
                }
            )
    return chamados


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_sla(caminho_sla)

    por_equipe = {}
    for chamado in chamados:
        por_equipe.setdefault(chamado["equipe"], []).append(chamado)

    equipes = []
    for nome in sorted(por_equipe):
        grupo = por_equipe[nome]
        total = sum(c["duracao"] for c in grupo)
        estourados = sum(1 for c in grupo if c["duracao"] > limites[c["prioridade"]])
        pior = min(grupo, key=lambda c: (-c["duracao"], c["id"]))
        equipes.append(
            {
                "equipe": nome,
                "chamados": len(grupo),
                "estourados": estourados,
                "tempo_medio_minutos": total // len(grupo),
                "pior_id": pior["id"],
            }
        )

    resumo = {"equipes": equipes}
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n")
    return resumo
