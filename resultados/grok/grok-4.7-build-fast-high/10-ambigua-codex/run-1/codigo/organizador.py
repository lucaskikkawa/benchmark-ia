def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Devolve cópias das tarefas pendentes, da maior prioridade para a menor.

    Prioridades iguais mantêm a ordem relativa da entrada. Entradas fora do
    domínio descrito em SUPOSICOES.md são ignoradas. A lista e os dicionários
    recebidos não são alterados.
    """
    if not tarefas:
        return []

    # Seis baldes (prioridade 0..5) evitam ordenação geral e mantêm empates
    # estáveis mesmo com dezenas de milhares de ocorrências.
    baldes: list[list[dict]] = [[], [], [], [], [], []]

    for tarefa in tarefas:
        if not isinstance(tarefa, dict):
            continue

        titulo = tarefa.get("titulo")
        if not isinstance(titulo, str) or titulo == "":
            continue

        prioridade = tarefa.get("prioridade")
        if (
            type(prioridade) is bool
            or not isinstance(prioridade, int)
            or prioridade < 0
            or prioridade > 5
        ):
            continue

        concluida = tarefa.get("concluida")
        if type(concluida) is not bool or concluida:
            continue

        baldes[prioridade].append(dict(tarefa))

    resultado: list[dict] = []
    for prioridade in range(5, -1, -1):
        resultado.extend(baldes[prioridade])
    return resultado
