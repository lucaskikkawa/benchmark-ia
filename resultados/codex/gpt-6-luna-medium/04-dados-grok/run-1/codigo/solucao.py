import csv
import json
import re
from datetime import datetime


_CABECALHO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES = ("baixa", "media", "alta")
_FORMATO_DATA = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}\Z")


def _objeto_sem_chaves_duplicadas(pares):
    resultado = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError("Chave JSON duplicada")
        resultado[chave] = valor
    return resultado


def _ler_sla(caminho_sla):
    with open(caminho_sla, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo, object_pairs_hook=_objeto_sem_chaves_duplicadas)

    if not isinstance(dados, dict) or set(dados) != {"limites_minutos"}:
        raise ValueError("Estrutura de SLA inválida")
    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites) != set(_PRIORIDADES):
        raise ValueError("Limites de SLA inválidos")
    for prioridade in _PRIORIDADES:
        limite = limites[prioridade]
        if isinstance(limite, bool) or not isinstance(limite, int) or limite < 1:
            raise ValueError("Limite de SLA inválido")
    return limites


def _ler_data(valor):
    if len(valor) != 16 or _FORMATO_DATA.fullmatch(valor) is None:
        raise ValueError("Data em formato inválido")
    try:
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M")
    except ValueError as erro:
        raise ValueError("Data inválida") from erro


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)
    equipes = {}
    ids = set()

    with open(caminho_csv, "r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            raise ValueError("CSV vazio ou sem cabeçalho")
        if cabecalho != _CABECALHO:
            raise ValueError("Cabeçalho CSV inválido")

        for linha in leitor:
            if not linha or all(campo.strip() == "" for campo in linha):
                continue
            if len(linha) != len(_CABECALHO):
                raise ValueError("Número de colunas inválido")
            identificador, equipe, aberto, fechado, prioridade = (
                campo.strip() for campo in linha
            )
            if not identificador or not equipe:
                raise ValueError("id e equipe não podem ser vazios")
            if prioridade not in _PRIORIDADES:
                raise ValueError("Prioridade inválida")

            inicio = _ler_data(aberto)
            fim = _ler_data(fechado)
            if fim < inicio:
                raise ValueError("fechado_em anterior a aberto_em")
            delta = fim - inicio
            duracao = delta.days * 1440 + delta.seconds // 60

            if identificador in ids:
                raise ValueError("id duplicado")
            ids.add(identificador)

            if equipe not in equipes:
                equipes[equipe] = {
                    "chamados": 0,
                    "estourados": 0,
                    "soma": 0,
                    "pior_duracao": -1,
                    "pior_id": None,
                }
            resumo = equipes[equipe]
            resumo["chamados"] += 1
            resumo["soma"] += duracao
            if duracao > limites[prioridade]:
                resumo["estourados"] += 1
            if (duracao > resumo["pior_duracao"] or
                    (duracao == resumo["pior_duracao"] and identificador < resumo["pior_id"])):
                resumo["pior_duracao"] = duracao
                resumo["pior_id"] = identificador

    resultado = {
        "equipes": [
            {
                "equipe": equipe,
                "chamados": equipes[equipe]["chamados"],
                "estourados": equipes[equipe]["estourados"],
                "tempo_medio_minutos": equipes[equipe]["soma"] // equipes[equipe]["chamados"],
                "pior_id": equipes[equipe]["pior_id"],
            }
            for equipe in sorted(equipes)
        ]
    }
    with open(caminho_saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    return resultado
