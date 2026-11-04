"""Organização de tarefas pendentes por prioridade."""

from __future__ import annotations


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Devolve as tarefas pendentes, da maior prioridade para a menor.

    Cada item incluído é uma cópia rasa independente do dicionário de origem.
    Empates de prioridade mantêm a ordem relativa da entrada. Itens fora do
    domínio descrito em SUPOSICOES.md são ignorados.
    """
    # Seis baldes (prioridades 0..5) tornam o desempate estável em tempo linear,
    # o que importa quando há dezenas de milhares de ocorrências empatadas.
    baldes: list[list[dict]] = [[], [], [], [], [], []]

    for tarefa in tarefas:
        if not isinstance(tarefa, dict):
            continue

        titulo = tarefa.get("titulo")
        prioridade = tarefa.get("prioridade")
        concluida = tarefa.get("concluida")

        if not isinstance(titulo, str) or titulo == "":
            continue
        # bool é subclasse de int; só o tipo exato int entra na faixa 0..5.
        if type(prioridade) is not int or prioridade < 0 or prioridade > 5:
            continue
        if type(concluida) is not bool or concluida:
            continue

        baldes[prioridade].append(tarefa.copy())

    pendentes: list[dict] = []
    for prioridade in range(5, -1, -1):
        pendentes.extend(baldes[prioridade])
    return pendentes
