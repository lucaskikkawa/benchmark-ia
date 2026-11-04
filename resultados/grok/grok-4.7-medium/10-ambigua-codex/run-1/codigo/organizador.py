"""Organização de tarefas pendentes por prioridade."""

from operator import itemgetter


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Devolve cópias das tarefas pendentes, da maior prioridade para a menor.

    A lista e os dicionários recebidos não são alterados. Empates de
    prioridade mantêm a ordem relativa da entrada. Entradas fora do domínio
    descrito em SUPOSICOES.md são omitidas.
    """
    if not isinstance(tarefas, list):
        return []

    pendentes = [
        dict(tarefa)
        for tarefa in tarefas
        if _pendente_valida(tarefa)
    ]
    pendentes.sort(key=itemgetter("prioridade"), reverse=True)
    return pendentes


def _pendente_valida(tarefa: object) -> bool:
    if not isinstance(tarefa, dict):
        return False

    titulo = tarefa.get("titulo")
    prioridade = tarefa.get("prioridade")
    concluida = tarefa.get("concluida")

    if not isinstance(titulo, str) or titulo == "":
        return False
    # bool é subclasse de int; prioridade precisa ser inteiro de verdade.
    if isinstance(prioridade, bool) or not isinstance(prioridade, int):
        return False
    if prioridade < 0 or prioridade > 5:
        return False
    if concluida is not False:
        return False
    return True
