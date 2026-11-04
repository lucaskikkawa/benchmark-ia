from typing import Any


def organizar_tarefas(tarefas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filtra tarefas pendentes e as ordena por prioridade decrescente.

    Retorna uma nova lista contendo cópias rasas independentes de cada
    dicionário de tarefa com ``concluida == False``, preservando a ordem
    relativa original em caso de empate de prioridade.
    """
    if not isinstance(tarefas, list):
        raise TypeError("A entrada 'tarefas' deve ser uma lista.")

    pendentes: list[dict[str, Any]] = []
    for tarefa in tarefas:
        if not isinstance(tarefa, dict):
            raise TypeError("Cada tarefa deve ser um dicionário.")

        if (
            "titulo" not in tarefa
            or "prioridade" not in tarefa
            or "concluida" not in tarefa
        ):
            raise ValueError(
                "Cada tarefa deve conter 'titulo', 'prioridade' e 'concluida'."
            )

        titulo = tarefa["titulo"]
        prioridade = tarefa["prioridade"]
        concluida = tarefa["concluida"]

        if not isinstance(titulo, str) or titulo == "":
            raise ValueError("O campo 'titulo' deve ser uma string não vazia.")

        if (
            not isinstance(prioridade, int)
            or isinstance(prioridade, bool)
            or not (0 <= prioridade <= 5)
        ):
            raise ValueError(
                "O campo 'prioridade' deve ser um inteiro entre 0 e 5."
            )

        if not isinstance(concluida, bool):
            raise ValueError("O campo 'concluida' deve ser um booleano.")

        if not concluida:
            pendentes.append(tarefa.copy())

    pendentes.sort(key=lambda t: t["prioridade"], reverse=True)
    return pendentes
