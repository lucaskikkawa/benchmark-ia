"""Organização de tarefas pendentes por prioridade."""

PRIORIDADE_MIN = 0
PRIORIDADE_MAX = 5


def _tarefa_valida(tarefa) -> bool:
    if not isinstance(tarefa, dict):
        return False
    titulo = tarefa.get("titulo")
    prioridade = tarefa.get("prioridade")
    concluida = tarefa.get("concluida")
    if not isinstance(titulo, str) or titulo == "":
        return False
    # bool é subclasse de int, mas não é uma prioridade válida.
    if type(prioridade) is not int:
        return False
    if not PRIORIDADE_MIN <= prioridade <= PRIORIDADE_MAX:
        return False
    if type(concluida) is not bool:
        return False
    return True


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Retorna cópias rasas das tarefas pendentes, da maior para a menor prioridade.

    Empates preservam a ordem original (ordenação estável). Entradas inválidas
    são ignoradas. A lista e os dicionários recebidos não são alterados.
    """
    if not tarefas:
        return []
    pendentes = [
        dict(t) for t in tarefas if _tarefa_valida(t) and t["concluida"] is False
    ]
    pendentes.sort(key=lambda t: t["prioridade"], reverse=True)
    return pendentes
