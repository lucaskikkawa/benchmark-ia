"""Organização de tarefas pendentes por prioridade.

Políticas para casos em aberto estão descritas em SUPOSICOES.md.
"""

PRIORIDADE_MIN = 0
PRIORIDADE_MAX = 5


def _validar(indice: int, tarefa: object) -> None:
    if not isinstance(tarefa, dict):
        raise ValueError(f"tarefa {indice}: esperado dict, recebido {type(tarefa).__name__}")
    for campo in ("titulo", "prioridade", "concluida"):
        if campo not in tarefa:
            raise ValueError(f"tarefa {indice}: campo obrigatório ausente: {campo!r}")

    titulo = tarefa["titulo"]
    if not isinstance(titulo, str) or titulo == "":
        raise ValueError(f"tarefa {indice}: 'titulo' deve ser str não vazia")

    prioridade = tarefa["prioridade"]
    # bool é subclasse de int, mas não é uma prioridade válida.
    if type(prioridade) is not int:
        raise ValueError(f"tarefa {indice}: 'prioridade' deve ser int")
    if not PRIORIDADE_MIN <= prioridade <= PRIORIDADE_MAX:
        raise ValueError(
            f"tarefa {indice}: 'prioridade' fora da faixa "
            f"{PRIORIDADE_MIN}..{PRIORIDADE_MAX}: {prioridade}"
        )

    if not isinstance(tarefa["concluida"], bool):
        raise ValueError(f"tarefa {indice}: 'concluida' deve ser bool")


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Devolve cópias rasas das tarefas pendentes, da maior para a menor prioridade.

    Empates mantêm a ordem original da entrada (ordenação estável).
    Entradas inválidas levantam ValueError antes de qualquer resultado.
    """
    if not isinstance(tarefas, list):
        raise ValueError(f"esperada list de tarefas, recebido {type(tarefas).__name__}")

    for indice, tarefa in enumerate(tarefas):
        _validar(indice, tarefa)

    pendentes = [dict(tarefa) for tarefa in tarefas if tarefa["concluida"] is False]
    # sorted é estável: com reverse=True, empates continuam na ordem de entrada.
    return sorted(pendentes, key=lambda t: t["prioridade"], reverse=True)
