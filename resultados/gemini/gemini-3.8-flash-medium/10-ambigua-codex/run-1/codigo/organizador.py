"""Módulo para organização de tarefas pendentes por prioridade."""

from typing import Any


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Organiza uma lista de tarefas pendentes por ordem decrescente de prioridade.

    Filtra apenas as tarefas pendentes (concluida == False), preserva os campos
    originais e retorna uma nova lista contendo cópias rasas independentes de
    cada dicionário selecionado.

    Parâmetros:
        tarefas (list[dict]): Lista de dicionários representando tarefas.

    Retorno:
        list[dict]: Nova lista com cópias rasas das tarefas pendentes,
                    ordenadas por prioridade decrescente.
    """
    if not isinstance(tarefas, (list, tuple)):
        return []

    pendentes: list[dict] = []

    for tarefa in tarefas:
        if not isinstance(tarefa, dict):
            continue

        titulo = tarefa.get("titulo")
        if not isinstance(titulo, str) or not titulo:
            continue

        prioridade = tarefa.get("prioridade")
        # Em Python, isinstance(True, int) é True, portanto verificamos type() is int
        if type(prioridade) is not int or not (0 <= prioridade <= 5):
            continue

        concluida = tarefa.get("concluida")
        if type(concluida) is not bool:
            continue

        if not concluida:
            pendentes.append(tarefa.copy())

    # Ordenação estável por prioridade decrescente (preserva a ordem relativa de inserção para empates)
    pendentes.sort(key=lambda t: t["prioridade"], reverse=True)

    return pendentes
