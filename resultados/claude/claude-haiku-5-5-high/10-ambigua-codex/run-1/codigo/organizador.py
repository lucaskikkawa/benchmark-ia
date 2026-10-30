"""Organização de tarefas pendentes por prioridade.

Ver SUPOSICOES.md para as políticas adotadas em casos não especificados.
"""


def _entrada_valida(tarefa: object) -> bool:
    """Indica se a entrada é um dict com titulo, prioridade e concluida válidos."""
    if not isinstance(tarefa, dict):
        return False

    titulo = tarefa.get("titulo")
    prioridade = tarefa.get("prioridade")
    concluida = tarefa.get("concluida")

    if not isinstance(titulo, str) or not titulo.strip():
        return False
    # bool é subclasse de int; rejeitá-lo explicitamente evita aceitar True/False como prioridade.
    if not isinstance(prioridade, int) or isinstance(prioridade, bool):
        return False
    if not 0 <= prioridade <= 5:
        return False
    if not isinstance(concluida, bool):
        return False
    return True


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Retorna as tarefas pendentes válidas, da maior para a menor prioridade.

    A entrada não é alterada. Cada tarefa devolvida é uma cópia rasa independente
    do dicionário original, e empates de prioridade mantêm a ordem da entrada.
    """
    if not tarefas:
        return []

    pendentes = [
        tarefa
        for tarefa in tarefas
        if _entrada_valida(tarefa) and tarefa["concluida"] is False
    ]
    pendentes.sort(key=lambda tarefa: tarefa["prioridade"], reverse=True)
    return [dict(tarefa) for tarefa in pendentes]
