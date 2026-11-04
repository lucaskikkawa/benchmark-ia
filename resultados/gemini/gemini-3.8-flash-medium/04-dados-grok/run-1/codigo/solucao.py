import csv
import json
import re
from datetime import datetime

EXPECTED_HEADER = ["id", "equipe", "aberto_em", "fechado_em", "prioridade"]
DATETIME_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")


def _parse_data_hora(s: str) -> datetime:
    if not isinstance(s, str) or len(s) != 16 or not DATETIME_REGEX.match(s):
        raise ValueError(f"Formato de data inválido: {s!r}")
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M")
    except Exception as e:
        raise ValueError(f"Data inexistente ou inválida: {s!r}") from e


def _ler_chamados(caminho_csv: str) -> list[dict]:
    with open(caminho_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header_found = False
        chamados = []
        seen_ids = set()

        for row in reader:
            # Linhas em branco ou em que todos os campos ficam vazios após strip são ignoradas
            if not row or all(c.strip() == "" for c in row):
                continue

            if not header_found:
                # O cabeçalho é comparado antes do strip e tem de ser exato
                if row != EXPECTED_HEADER:
                    raise ValueError(f"Cabeçalho inválido: {row}")
                header_found = True
                continue

            # Linha de dados: número de colunas tem que ser exatamente 5
            if len(row) != 5:
                raise ValueError(f"Número incorreto de colunas: esperado 5, recebido {len(row)}")

            id_chamado, equipe, aberto_em, fechado_em, prioridade = [c.strip() for c in row]

            if not id_chamado:
                raise ValueError("Campo 'id' não pode ser vazio")
            if not equipe:
                raise ValueError("Campo 'equipe' não pode ser vazio")

            if id_chamado in seen_ids:
                raise ValueError(f"id duplicado: {id_chamado}")
            seen_ids.add(id_chamado)

            if prioridade not in ("baixa", "media", "alta"):
                raise ValueError(f"Prioridade inválida: {prioridade}")

            dt_aberto = _parse_data_hora(aberto_em)
            dt_fechado = _parse_data_hora(fechado_em)
            if dt_fechado < dt_aberto:
                raise ValueError(f"fechado_em ({fechado_em}) anterior a aberto_em ({aberto_em})")

            duracao = int((dt_fechado - dt_aberto).total_seconds() // 60)

            chamados.append({
                "id": id_chamado,
                "equipe": equipe,
                "duracao": duracao,
                "prioridade": prioridade,
            })

    if not header_found:
        raise ValueError("Arquivo CSV vazio ou sem cabeçalho")

    return chamados


def _ler_sla(caminho_sla: str) -> dict[str, int]:
    with open(caminho_sla, "r", encoding="utf-8") as f:
        conteudo = f.read()

    try:
        dados = json.loads(conteudo)
    except Exception as e:
        raise ValueError("JSON de SLA inválido") from e

    if not isinstance(dados, dict):
        raise ValueError("SLA deve ser um objeto JSON")

    if set(dados.keys()) != {"limites_minutos"}:
        raise ValueError("SLA deve conter exatamente a chave 'limites_minutos'")

    limites = dados["limites_minutos"]
    if not isinstance(limites, dict):
        raise ValueError("'limites_minutos' deve ser um objeto JSON")

    prioridades_esperadas = {"baixa", "media", "alta"}
    if set(limites.keys()) != prioridades_esperadas:
        raise ValueError(f"limites_minutos deve conter exatamente as chaves: {prioridades_esperadas}")

    for p in ("baixa", "media", "alta"):
        val = limites[p]
        if type(val) is not int or val < 1:
            raise ValueError(f"Limite para '{p}' deve ser um int >= 1 (recebido: {val!r})")

    return limites


def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
    chamados = _ler_chamados(caminho_csv)
    limites = _ler_sla(caminho_sla)

    equipes_map: dict[str, dict] = {}
    for ch in chamados:
        eq = ch["equipe"]
        if eq not in equipes_map:
            equipes_map[eq] = {
                "chamados": 0,
                "estourados": 0,
                "soma_duracao": 0,
                "chamados_lista": [],
            }
        limite = limites[ch["prioridade"]]
        estourou = 1 if ch["duracao"] > limite else 0

        equipes_map[eq]["chamados"] += 1
        equipes_map[eq]["estourados"] += estourou
        equipes_map[eq]["soma_duracao"] += ch["duracao"]
        equipes_map[eq]["chamados_lista"].append((ch["duracao"], ch["id"]))

    equipes_saida = []
    for eq in sorted(equipes_map.keys()):
        dados = equipes_map[eq]
        # pior_id: id de maior duração. Empate: menor id na ordem lexicográfica de str.
        pior = min(dados["chamados_lista"], key=lambda x: (-x[0], x[1]))
        equipes_saida.append({
            "equipe": eq,
            "chamados": dados["chamados"],
            "estourados": dados["estourados"],
            "tempo_medio_minutos": dados["soma_duracao"] // dados["chamados"],
            "pior_id": pior[1],
        })

    resultado = {"equipes": equipes_saida}

    conteudo_json = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_json)

    return resultado
