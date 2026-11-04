"""Módulo para organização de tarefas pendentes por prioridade."""


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Organiza uma lista de tarefas pendentes em ordem decrescente de prioridade.

    Filtra apenas tarefas válidas e pendentes (concluida == False), retornando
    uma nova lista contendo cópias rasas independentes de cada dicionário.
    """
    if not hasattr(tarefas, "__iter__") or isinstance(tarefas, (str, bytes, dict)):
        return []

    resultado = []
    for tarefa in tarefas:
        if not isinstance(tarefa, dict):
            continue

        titulo = tarefa.get("titulo")
        if not isinstance(titulo, str) or len(titulo) == 0:
            continue

        prioridade = tarefa.get("prioridade")
        if type(prioridade) is not int or not (0 <= prioridade <= 5):
            continue

        concluida = tarefa.get("concluida")
        if type(concluida) is not bool:
            continue

        if not concluida:
            resultado.append(tarefa.copy())

    resultado.sort(key=lambda t: t["prioridade"], reverse=True)
    return resultado
