"""Organização de tarefas pendentes por prioridade."""

from __future__ import annotations


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Devolve cópias das tarefas pendentes válidas, maior prioridade primeiro.

    A ordem relativa original é preservada entre tarefas de mesma prioridade.
    Entradas inválidas são ignoradas. A lista e os dicionários recebidos não
    são alterados.
    """
    if not tarefas:
        return []

    pendentes: list[dict] = []
    for tarefa in tarefas:
        if not _pendente_valida(tarefa):
            continue
        pendentes.append(dict(tarefa))

    pendentes.sort(key=_prioridade, reverse=True)
    return pendentes


def _pendente_valida(tarefa: object) -> bool:
    if not isinstance(tarefa, dict):
        return False

    titulo = tarefa.get("titulo")
    prioridade = tarefa.get("prioridade")
    concluida = tarefa.get("concluida")

    if type(titulo) is not str or titulo == "":
        return False
    if type(prioridade) is not int or prioridade < 0 or prioridade > 5:
        return False
    if type(concluida) is not bool or concluida:
        return False
    return True


def _prioridade(tarefa: dict) -> int:
    return tarefa["prioridade"]
