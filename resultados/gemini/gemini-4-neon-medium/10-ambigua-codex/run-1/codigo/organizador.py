"""Organização de tarefas pendentes por prioridade."""

from __future__ import annotations

_CAMPOS_OBRIGATORIOS = ("titulo", "prioridade", "concluida")
_PRIORIDADE_MIN = 0
_PRIORIDADE_MAX = 5


def _validar_tarefa(tarefa: object, indice: int) -> tuple[int, bool]:
    """Valida os campos obrigatórios de uma tarefa e retorna (prioridade, concluida)."""
    if not isinstance(tarefa, dict):
        raise TypeError(
            f"Tarefa no índice {indice} deve ser dict, recebido {type(tarefa).__name__}."
        )

    for campo in _CAMPOS_OBRIGATORIOS:
        if campo not in tarefa:
            raise ValueError(
                f"Tarefa no índice {indice} não contém o campo obrigatório '{campo}'."
            )

    titulo = tarefa["titulo"]
    if not isinstance(titulo, str):
        raise TypeError(
            f"Campo 'titulo' no índice {indice} deve ser str, recebido {type(titulo).__name__}."
        )
    if len(titulo) == 0:
        raise ValueError(f"Campo 'titulo' no índice {indice} não pode ser vazio.")

    prioridade = tarefa["prioridade"]
    if isinstance(prioridade, bool) or not isinstance(prioridade, int):
        raise TypeError(
            f"Campo 'prioridade' no índice {indice} deve ser int, recebido {type(prioridade).__name__}."
        )
    if not (_PRIORIDADE_MIN <= prioridade <= _PRIORIDADE_MAX):
        raise ValueError(
            f"Campo 'prioridade' no índice {indice} deve estar entre {_PRIORIDADE_MIN} e {_PRIORIDADE_MAX}, recebido {prioridade}."
        )

    concluida = tarefa["concluida"]
    if not isinstance(concluida, bool):
        raise TypeError(
            f"Campo 'concluida' no índice {indice} deve ser bool, recebido {type(concluida).__name__}."
        )

    return prioridade, concluida


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Retorna cópias rasas das tarefas pendentes em ordem decrescente de prioridade.

    Em caso de empate de prioridade, preserva a ordem relativa original da entrada.
    Não altera a lista nem os dicionários recebidos.
    """
    if not isinstance(tarefas, list):
        raise TypeError(
            f"'tarefas' deve ser uma list, recebido {type(tarefas).__name__}."
        )

    grupos: list[list[dict]] = [[] for _ in range(_PRIORIDADE_MAX + 1)]

    for indice, tarefa in enumerate(tarefas):
        prioridade, concluida = _validar_tarefa(tarefa, indice)
        if not concluida:
            grupos[prioridade].append(dict(tarefa))

    resultado: list[dict] = []
    for prioridade in range(_PRIORIDADE_MAX, _PRIORIDADE_MIN - 1, -1):
        resultado.extend(grupos[prioridade])

    return resultado
