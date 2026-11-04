import csv
from datetime import datetime, timedelta
import json

CABECALHO_ESPERADO = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
PRIORIDADES_VALIDAS = {"baixa", "media", "alta"}


def _carregar_sem_duplicatas(pares: list[tuple[str, object]]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for chave, valor in pares:
        if chave in obj:
            raise ValueError(f"Chave duplicada no JSON: {chave}")
        obj[chave] = valor
    return obj


def _ler_sla(caminho_sla: str) -> dict[str, int]:
    with open(caminho_sla, "r", encoding="utf-8") as f:
        dados = json.load(f, object_pairs_hook=_carregar_sem_duplicatas)

    if type(dados) is not dict or set(dados.keys()) != {"limites_minutos"}:
        raise ValueError("Estrutura de SLA inválida")

    limites = dados["limites_minutos"]
    if type(limites) is not dict or set(limites.keys()) != PRIORIDADES_VALIDAS:
        raise ValueError("Prioridades de SLA inválidas")

    resultado: dict[str, int] = {}
    for prio, valor in limites.items():
        if type(valor) is not int or valor < 1:
            raise ValueError(f"Limite inválido para {prio}")
        resultado[prio] = valor

    return resultado


def _parse_data(texto: str) -> datetime:
    if (
        len(texto) != 16
        or texto[4] != "-"
        or texto[7] != "-"
        or texto[10] != "T"
        or texto[13] != ":"
    ):
        raise ValueError(f"Data com formato inválido: {texto}")

    partes = (texto[0:4], texto[5:7], texto[8:10], texto[11:13], texto[14:16])
    if not all(p.isascii() and p.isdigit() for p in partes):
        raise ValueError(f"Data com formato inválido: {texto}")

    ano, mes, dia, hora, minuto = (int(p) for p in partes)
    return datetime(ano, mes, dia, hora, minuto)


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    limites = _ler_sla(caminho_sla)

    ids_vistos: set[str] = set()
    equipes: dict[str, dict[str, object]] = {}

    with open(caminho_csv, "r", encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        try:
            try:
                cabecalho = next(leitor)
            except StopIteration:
                raise ValueError("Arquivo CSV vazio")

            if cabecalho != CABECALHO_ESPERADO:
                raise ValueError("Cabeçalho inválido")

            for linha in leitor:
                if not linha or all(campo.strip() == "" for campo in linha):
                    continue

                if len(linha) != 5:
                    raise ValueError("Número de colunas inválido")

                id_chamado, equipe, aberto_str, fechado_str, prioridade = (
                    campo.strip() for campo in linha
                )

                if not id_chamado or not equipe:
                    raise ValueError("id e equipe não podem ser vazios")

                if id_chamado in ids_vistos:
                    raise ValueError(f"id duplicado: {id_chamado}")
                ids_vistos.add(id_chamado)

                if prioridade not in PRIORIDADES_VALIDAS:
                    raise ValueError(f"Prioridade inválida: {prioridade}")

                aberto_em = _parse_data(aberto_str)
                fechado_em = _parse_data(fechado_str)

                if fechado_em < aberto_em:
                    raise ValueError("fechado_em anterior a aberto_em")

                duracao = (fechado_em - aberto_em) // timedelta(minutes=1)
                estourou = 1 if duracao > limites[prioridade] else 0

                if equipe not in equipes:
                    equipes[equipe] = {
                        "chamados": 1,
                        "estourados": estourou,
                        "soma_duracao": duracao,
                        "pior_duracao": duracao,
                        "pior_id": id_chamado,
                    }
                else:
                    dados_eq = equipes[equipe]
                    dados_eq["chamados"] = int(dados_eq["chamados"]) + 1
                    dados_eq["estourados"] = int(dados_eq["estourados"]) + estourou
                    dados_eq["soma_duracao"] = int(dados_eq["soma_duracao"]) + duracao
                    pior_duracao = int(dados_eq["pior_duracao"])
                    pior_id = str(dados_eq["pior_id"])
                    if (duracao > pior_duracao) or (
                        duracao == pior_duracao and id_chamado < pior_id
                    ):
                        dados_eq["pior_duracao"] = duracao
                        dados_eq["pior_id"] = id_chamado
        except csv.Error as exc:
            raise ValueError("Erro ao processar CSV") from exc

    lista_equipes = []
    for nome_equipe in sorted(equipes.keys()):
        dados_eq = equipes[nome_equipe]
        chamados = int(dados_eq["chamados"])
        soma_duracao = int(dados_eq["soma_duracao"])
        lista_equipes.append(
            {
                "equipe": nome_equipe,
                "chamados": chamados,
                "estourados": int(dados_eq["estourados"]),
                "tempo_medio_minutos": soma_duracao // chamados,
                "pior_id": str(dados_eq["pior_id"]),
            }
        )

    resultado = {"equipes": lista_equipes}
    conteudo_json = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_json)

    return resultado
