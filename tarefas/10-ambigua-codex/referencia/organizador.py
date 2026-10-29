def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Copie tarefas pendentes e ordene por prioridade decrescente, preservando empates."""
    pendentes = [dict(tarefa) for tarefa in tarefas if not tarefa['concluida']]
    return sorted(pendentes, key=lambda tarefa: tarefa['prioridade'], reverse=True)
