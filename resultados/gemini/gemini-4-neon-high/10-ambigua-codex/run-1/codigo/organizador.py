"""Organização de tarefas pendentes por prioridade."""

from __future__ import annotations

_PRIORIDADE_MIN = 0
_PRIORIDADE_MAX = 5
_CAMPOS_OBRIGATORIOS = ("titulo", "prioridade", "concluida")


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Retorna cópias rasas das tarefas pendentes ordenadas por prioridade decrescente.

    Mantém apenas tarefas com ``concluida is False``, preservando todos os campos
    (inclusive campos extras e a identidade dos objetos neles contidos) e a ordem
    original de aparição em caso de empate de prioridade. Não altera a lista nem os
    dicionários recebidos.
    """
    if not isinstance(tarefas, list):
        raise TypeError("tarefas deve ser uma lista de dicionários")

    buckets: list[list[dict]] = [[] for _ in range(_PRIORIDADE_MAX + 1)]

    for indice, tarefa in enumerate(tarefas):
        if not isinstance(tarefa, dict):
            raise TypeError(f"Tarefa no índice {indice} deve ser um dict")

        for campo in _CAMPOS_OBRIGATORIOS:
            if campo not in tarefa:
                raise ValueError(
                    f"Tarefa no índice {indice} sem campo obrigatório: {campo!r}"
                )

        titulo = tarefa["titulo"]
        if not isinstance(titulo, str):
            raise TypeError(f"Campo 'titulo' no índice {indice} deve ser str")
        if not titulo:
            raise ValueError(f"Campo 'titulo' no índice {indice} não pode ser vazio")

        prioridade = tarefa["prioridade"]
        if isinstance(prioridade, bool) or not isinstance(prioridade, int):
            raise TypeError(f"Campo 'prioridade' no índice {indice} deve ser int")
        if not (_PRIORIDADE_MIN <= prioridade <= _PRIORIDADE_MAX):
            raise ValueError(
                f"Campo 'prioridade' no índice {indice} fora da faixa "
                f"[{_PRIORIDADE_MIN}, {_PRIORIDADE_MAX}]: {prioridade}"
            )

        concluida = tarefa["concluida"]
        if not isinstance(concluida, bool):
            raise TypeError(f"Campo 'concluida' no índice {indice} deve ser bool")

        if not concluida:
            buckets[prioridade].append(dict(tarefa))

    resultado: list[dict] = []
    for prioridade in range(_PRIORIDADE_MAX, _PRIORIDADE_MIN - 1, -1):
        resultado.extend(buckets[prioridade])

    return resultado
