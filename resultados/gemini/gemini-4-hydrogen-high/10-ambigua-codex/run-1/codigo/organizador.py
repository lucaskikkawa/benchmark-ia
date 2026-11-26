from __future__ import annotations


def _validar_tarefa(tarefa: object, indice: int) -> tuple[int, bool]:
    """Valida os campos obrigatórios de uma tarefa e retorna (prioridade, concluida)."""
    if not isinstance(tarefa, dict):
        raise TypeError(f"Tarefa no índice {indice} deve ser um dict.")

    for campo in ("titulo", "prioridade", "concluida"):
        if campo not in tarefa:
            raise ValueError(
                f"Tarefa no índice {indice} não possui o campo obrigatório '{campo}'."
            )

    titulo = tarefa["titulo"]
    if not isinstance(titulo, str):
        raise TypeError(f"Campo 'titulo' no índice {indice} deve ser str.")
    if titulo == "":
        raise ValueError(f"Campo 'titulo' no índice {indice} não pode ser vazio.")

    prioridade = tarefa["prioridade"]
    if not isinstance(prioridade, int) or isinstance(prioridade, bool):
        raise TypeError(f"Campo 'prioridade' no índice {indice} deve ser int.")
    if not (0 <= prioridade <= 5):
        raise ValueError(
            f"Campo 'prioridade' no índice {indice} deve estar entre 0 e 5."
        )

    concluida = tarefa["concluida"]
    if not isinstance(concluida, bool):
        raise TypeError(f"Campo 'concluida' no índice {indice} deve ser bool.")

    return prioridade, concluida


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Retorna cópias rasas das tarefas pendentes em ordem decrescente de prioridade."""
    if not isinstance(tarefas, list):
        raise TypeError("O argumento 'tarefas' deve ser uma list.")

    # Baldes de prioridade 0..5 garantem ordenação estável em O(n).
    baldes: tuple[list[dict], ...] = ([], [], [], [], [], [])

    for indice, tarefa in enumerate(tarefas):
        prioridade, concluida = _validar_tarefa(tarefa, indice)
        if not concluida:
            baldes[prioridade].append(tarefa.copy())

    resultado: list[dict] = []
    for prioridade in range(5, -1, -1):
        resultado.extend(baldes[prioridade])

    return resultado
