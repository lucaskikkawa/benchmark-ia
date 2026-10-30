import csv
from datetime import datetime
import json
import re

_PADRAO_DATA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}$")
_CABECALHO_ESPERADO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
_PRIORIDADES_VALIDAS = ("baixa", "media", "alta")


def _carregar_objeto_sem_duplicatas(pares: list[tuple[str, object]]) -> dict:
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Chave duplicada no JSON: {chave}")
        objeto[chave] = valor
    return objeto


def _ler_sla(caminho_sla: str) -> dict[str, int]:
    with open(caminho_sla, mode="r", encoding="utf-8") as f:
        try:
            dados = json.load(f, object_pairs_hook=_carregar_objeto_sem_duplicatas)
        except json.JSONDecodeError as exc:
            raise ValueError("JSON de SLA inválido") from exc

    if not isinstance(dados, dict) or set(dados.keys()) != {"limites_minutos"}:
        raise ValueError("Estrutura de SLA inválida")

    limites = dados["limites_minutos"]
    if not isinstance(limites, dict) or set(limites.keys()) != set(_PRIORIDADES_VALIDAS):
        raise ValueError("Prioridades de SLA inválidas")

    limites_validados: dict[str, int] = {}
    for prioridade, limite in limites.items():
        if isinstance(limite, bool) or not isinstance(limite, int) or limite < 1:
            raise ValueError(f"Limite inválido para prioridade {prioridade}")
        limites_validados[prioridade] = limite

    return limites_validados


def _parse_timestamp(valor: str) -> datetime:
    if not _PADRAO_DATA.match(valor):
        raise ValueError(f"Formato de data inválido: {valor}")
    return datetime(
        int(valor[0:4]),
        int(valor[5:7]),
        int(valor[8:10]),
        int(valor[11:13]),
        int(valor[14:16]),
    )


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)

    ids_vistos: set[str] = set()
    dados_equipes: dict[str, dict] = {}

    with open(caminho_csv, mode="r", encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        try:
            cabecalho = next(leitor)
        except StopIteration as exc:
            raise ValueError("Arquivo CSV vazio") from exc
        except csv.Error as exc:
            raise ValueError("Erro ao ler cabeçalho do CSV") from exc

        if cabecalho != _CABECALHO_ESPERADO:
            raise ValueError("Cabeçalho do CSV inválido")

        try:
            for linha in leitor:
                if not linha or all(campo.strip() == "" for campo in linha):
                    continue

                if len(linha) != 5:
                    raise ValueError("Número de colunas inválido no CSV")

                id_chamado, equipe, aberto_str, fechado_str, prioridade = (
                    campo.strip() for campo in linha
                )

                if not id_chamado or not equipe:
                    raise ValueError("id e equipe não podem ser vazios")

                if id_chamado in ids_vistos:
                    raise ValueError(f"id duplicado: {id_chamado}")
                ids_vistos.add(id_chamado)

                if prioridade not in _PRIORIDADES_VALIDAS:
                    raise ValueError(f"Prioridade inválida: {prioridade}")

                aberto_em = _parse_timestamp(aberto_str)
                fechado_em = _parse_timestamp(fechado_str)

                if fechado_em < aberto_em:
                    raise ValueError("fechado_em anterior a aberto_em")

                delta = fechado_em - aberto_em
                duracao_minutos = delta.days * 1440 + delta.seconds // 60
                estourou = 1 if duracao_minutos > limites[prioridade] else 0

                if equipe not in dados_equipes:
                    dados_equipes[equipe] = {
                        "chamados": 1,
                        "estourados": estourou,
                        "soma_duracao": duracao_minutos,
                        "pior_duracao": duracao_minutos,
                        "pior_id": id_chamado,
                    }
                else:
                    info = dados_equipes[equipe]
                    info["chamados"] += 1
                    info["estourados"] += estourou
                    info["soma_duracao"] += duracao_minutos
                    if duracao_minutos > info["pior_duracao"] or (
                        duracao_minutos == info["pior_duracao"]
                        and id_chamado < info["pior_id"]
                    ):
                        info["pior_duracao"] = duracao_minutos
                        info["pior_id"] = id_chamado
        except csv.Error as exc:
            raise ValueError("Erro de formatação no CSV") from exc

    resumo_equipes = []
    for nome_equipe in sorted(dados_equipes.keys()):
        info = dados_equipes[nome_equipe]
        resumo_equipes.append(
            {
                "equipe": nome_equipe,
                "chamados": info["chamados"],
                "estourados": info["estourados"],
                "tempo_medio_minutos": info["soma_duracao"] // info["chamados"],
                "pior_id": info["pior_id"],
            }
        )

    resultado = {"equipes": resumo_equipes}

    with open(caminho_saida, mode="w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")

    return resultado
