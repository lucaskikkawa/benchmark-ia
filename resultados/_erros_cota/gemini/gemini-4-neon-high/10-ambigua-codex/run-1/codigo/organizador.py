"""Organização de tarefas pendentes por prioridade."""

from operator import itemgetter

_CAMPOS_OBRIGATORIOS = ("titulo", "prioridade", "concluida")
_PRIORIDADE_MIN = 0
_PRIORIDADE_MAX = 5
_CHAVE_PRIORIDADE = itemgetter("prioridade")


def _validar_tarefa(tarefa: object, indice: int) -> bool:
    """Valida uma tarefa e retorna True se estiver pendente (concluida is False)."""
    if not isinstance(tarefa, dict):
        raise TypeError(
            f"Tarefa no índice {indice} deve ser dict, recebido {type(tarefa).__name__}."
        )

    for campo in _CAMPOS_OBRIGATORIOS:
        if campo not in tarefa:
            raise ValueError(
                f"Tarefa no índice {indice} sem o campo obrigatório '{campo}'."
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
            f"Campo 'prioridade' no índice {indice} deve ser int (não bool), "
            f"recebido {type(prioridade).__name__}."
        )
    if not (_PRIORIDADE_MIN <= prioridade <= _PRIORIDADE_MAX):
        raise ValueError(
            f"Campo 'prioridade' no índice {indice} deve estar entre "
            f"{_PRIORIDADE_MIN} e {_PRIORIDADE_MAX}, recebido {prioridade}."
        )

    concluida = tarefa["concluida"]
    if not isinstance(concluida, bool):
        raise TypeError(
            f"Campo 'concluida' no índice {indice} deve ser bool, "
            f"recebido {type(concluida).__name__}."
        )

    return not concluida


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Filtra tarefas pendentes e as ordena por prioridade decrescente.

    Retorna uma nova lista contendo cópias rasas independentes das tarefas com
    `concluida == False`, preservando todos os campos originais (incluindo
    campos extras e a identidade dos objetos neles contidos) sem alterar a
    entrada. Em caso de empate de prioridade, preserva a ordem relativa original.
    """
    if not isinstance(tarefas, list):
        raise TypeError(
            f"Parâmetro 'tarefas' deve ser list, recebido {type(tarefas).__name__}."
        )

    pendentes: list[dict] = []
    for indice, tarefa in enumerate(tarefas):
        if _validar_tarefa(tarefa, indice):
            pendentes.append(tarefa.copy())

    pendentes.sort(key=_CHAVE_PRIORIDADE, reverse=True)
    return pendentes
