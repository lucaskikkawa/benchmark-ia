import csv
import json
import re
from datetime import datetime

_CABECALHO_ESPERADO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES_VALIDAS = frozenset({"baixa", "media", "alta"})
_PADRAO_DATA_HORA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}$")


def _carregar_sla(caminho_sla: str) -> dict[str, int]:
    with open(caminho_sla, "r", encoding="utf-8") as f:
        conteudo = f.read()

    if not conteudo.strip():
        raise ValueError("Arquivo de SLA vazio.")

    dados = json.loads(conteudo)
    if not isinstance(dados, dict) or set(dados.keys()) != {"limites_minutos"}:
        raise ValueError("Estrutura de SLA inválida.")

    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites.keys()) != _PRIORIDADES_VALIDAS:
        raise ValueError("Limites de SLA inválidos.")

    for prioridade, limite in limites.items():
        if isinstance(limite, bool) or not isinstance(limite, int) or limite < 1:
            raise ValueError(f"Limite inválido para prioridade {prioridade!r}.")

    return limites


def _parse_data_hora(valor: str) -> datetime:
    if not _PADRAO_DATA_HORA.fullmatch(valor):
        raise ValueError(f"Formato de data/hora inválido: {valor!r}")
    return datetime.strptime(valor, "%Y-%m-%dT%H:%M")


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _carregar_sla(caminho_sla)

    ids_vistos: set[str] = set()
    por_equipe: dict[str, dict] = {}

    with open(caminho_csv, "r", encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        cabecalho = next(leitor, None)
        if cabecalho != _CABECALHO_ESPERADO:
            raise ValueError("Cabeçalho do CSV inválido ou ausente.")

        for linha in leitor:
            if not linha or all(campo.strip() == "" for campo in linha):
                continue

            if len(linha) != 5:
                raise ValueError("Número de colunas inválido no CSV.")

            id_chamado, equipe, aberto_str, fechado_str, prioridade = (
                campo.strip() for campo in linha
            )

            if not id_chamado or not equipe:
                raise ValueError("Campos 'id' e 'equipe' não podem ser vazios.")

            if id_chamado in ids_vistos:
                raise ValueError(f"ID duplicado: {id_chamado!r}")
            ids_vistos.add(id_chamado)

            if prioridade not in _PRIORIDADES_VALIDAS:
                raise ValueError(f"Prioridade inválida: {prioridade!r}")

            aberto_em = _parse_data_hora(aberto_str)
            fechado_em = _parse_data_hora(fechado_str)
            if fechado_em < aberto_em:
                raise ValueError(
                    f"Data de fechamento anterior à abertura no chamado {id_chamado!r}."
                )

            delta = fechado_em - aberto_em
            duracao = delta.days * 1440 + delta.seconds // 60
            estourou = duracao > limites[prioridade]

            if equipe not in por_equipe:
                por_equipe[equipe] = {
                    "chamados": 1,
                    "estourados": 1 if estourou else 0,
                    "soma_duracoes": duracao,
                    "pior_duracao": duracao,
                    "pior_id": id_chamado,
                }
            else:
                acc = por_equipe[equipe]
                acc["chamados"] += 1
                if estourou:
                    acc["estourados"] += 1
                acc["soma_duracoes"] += duracao
                if duracao > acc["pior_duracao"] or (
                    duracao == acc["pior_duracao"] and id_chamado < acc["pior_id"]
                ):
                    acc["pior_duracao"] = duracao
                    acc["pior_id"] = id_chamado

    equipes_saida = []
    for nome_equipe in sorted(por_equipe):
        acc = por_equipe[nome_equipe]
        equipes_saida.append(
            {
                "equipe": nome_equipe,
                "chamados": acc["chamados"],
                "estourados": acc["estourados"],
                "tempo_medio_minutos": acc["soma_duracoes"] // acc["chamados"],
                "pior_id": acc["pior_id"],
            }
        )

    resultado = {"equipes": equipes_saida}
    texto_json = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(texto_json)

    return resultado
