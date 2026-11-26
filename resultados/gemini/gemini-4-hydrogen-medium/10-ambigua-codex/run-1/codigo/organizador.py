from __future__ import annotations


def _validar_tarefa(tarefa: object, indice: int) -> dict:
    """Valida uma entrada de tarefa e a retorna como dict."""
    if not isinstance(tarefa, dict):
        raise TypeError(f"Item no índice {indice} deve ser dict.")

    for campo in ("titulo", "prioridade", "concluida"):
        if campo not in tarefa:
            raise ValueError(f"Item no índice {indice} sem campo obrigatório '{campo}'.")

    titulo = tarefa["titulo"]
    if not isinstance(titulo, str):
        raise TypeError(f"Campo 'titulo' no índice {indice} deve ser str.")
    if len(titulo) == 0:
        raise ValueError(f"Campo 'titulo' no índice {indice} não pode ser vazio.")

    prioridade = tarefa["prioridade"]
    if isinstance(prioridade, bool) or not isinstance(prioridade, int):
        raise TypeError(f"Campo 'prioridade' no índice {indice} deve ser int.")
    if not (0 <= prioridade <= 5):
        raise ValueError(f"Campo 'prioridade' no índice {indice} deve estar entre 0 e 5.")

    concluida = tarefa["concluida"]
    if not isinstance(concluida, bool):
        raise TypeError(f"Campo 'concluida' no índice {indice} deve ser bool.")

    return tarefa


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Retorna cópias rasas das tarefas pendentes ordenadas por prioridade decrescente."""
    if not isinstance(tarefas, list):
        raise TypeError("O argumento 'tarefas' deve ser uma list.")

    buckets: list[list[dict]] = [[] for _ in range(6)]

    for indice, item in enumerate(tarefas):
        tarefa = _validar_tarefa(item, indice)
        if not tarefa["concluida"]:
            buckets[tarefa["prioridade"]].append(tarefa.copy())

    resultado: list[dict] = []
    for prioridade in range(5, -1, -1):
        resultado.extend(buckets[prioridade])

    return resultado
