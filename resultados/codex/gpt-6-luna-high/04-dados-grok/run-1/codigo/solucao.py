import csv
import json
import re
from datetime import datetime


_CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES = ("baixa", "media", "alta")
_FORMATO_DATA = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}\Z")


def _ler_sla(caminho_sla: str) -> dict:
    try:
        with open(caminho_sla, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (json.JSONDecodeError, UnicodeDecodeError) as erro:
        raise ValueError("JSON de SLA inválido") from erro

    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("Estrutura de SLA inválida")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(_PRIORIDADES):
        raise ValueError("Prioridades de SLA inválidas")
    if any(type(limites[p]) is not int or limites[p] < 1 for p in _PRIORIDADES):
        raise ValueError("Limite de SLA inválido")
    return limites


def _ler_data(valor: str) -> datetime:
    if not _FORMATO_DATA.fullmatch(valor):
        raise ValueError("Data deve usar o formato YYYY-MM-DDTHH:MM")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M")
    except ValueError as erro:
        raise ValueError("Data inexistente") from erro


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)
    equipes = {}
    ids = set()

    try:
        with open(caminho_csv, "r", encoding="utf-8", newline="") as arquivo:
            leitor = csv.reader(arquivo)
            try:
                cabecalho = next(leitor)
            except StopIteration as erro:
                raise ValueError("CSV vazio ou sem cabeçalho") from erro
            if cabecalho != _CABECALHO:
                raise ValueError("Cabeçalho CSV inválido")

            for linha in leitor:
                if not linha or all(not campo.strip() for campo in linha):
                    continue
                if len(linha) != len(_CABECALHO):
                    raise ValueError("Número de colunas inválido")

                chamado_id, equipe, aberto, fechado, prioridade = (
                    campo.strip() for campo in linha
                )
                if not chamado_id or not equipe:
                    raise ValueError("id e equipe não podem ficar vazios")
                if chamado_id in ids:
                    raise ValueError("id duplicado")
                ids.add(chamado_id)

                if prioridade not in _PRIORIDADES:
                    raise ValueError("Prioridade inválida")
                instante_aberto = _ler_data(aberto)
                instante_fechado = _ler_data(fechado)
                if instante_fechado < instante_aberto:
                    raise ValueError("fechado_em anterior a aberto_em")
                duracao = int((instante_fechado - instante_aberto).total_seconds() // 60)
                estourado = duracao > limites[prioridade]

                resumo = equipes.setdefault(
                    equipe,
                    {"total": 0, "estourados": 0, "soma": 0, "pior_duracao": None, "pior_id": None},
                )
                resumo["total"] += 1
                resumo["estourados"] += int(estourado)
                resumo["soma"] += duracao
                if (
                    resumo["pior_duracao"] is None
                    or duracao > resumo["pior_duracao"]
                    or (duracao == resumo["pior_duracao"] and chamado_id < resumo["pior_id"])
                ):
                    resumo["pior_duracao"] = duracao
                    resumo["pior_id"] = chamado_id
    except (UnicodeDecodeError, csv.Error) as erro:
        raise ValueError("CSV inválido") from erro

    resultado = {
        "equipes": [
            {
                "equipe": nome,
                "chamados": equipes[nome]["total"],
                "estourados": equipes[nome]["estourados"],
                "tempo_medio_minutos": equipes[nome]["soma"] // equipes[nome]["total"],
                "pior_id": equipes[nome]["pior_id"],
            }
            for nome in sorted(equipes)
        ]
    }

    with open(caminho_saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
