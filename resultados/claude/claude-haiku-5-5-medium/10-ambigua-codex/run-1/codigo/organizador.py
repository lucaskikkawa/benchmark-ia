def _valida(tarefa: object) -> bool:
    """Indica se a entrada tem os campos obrigatórios com tipos e faixas válidos."""
    if not isinstance(tarefa, dict):
        return False
    titulo = tarefa.get("titulo")
    prioridade = tarefa.get("prioridade")
    concluida = tarefa.get("concluida")
    return (
        isinstance(titulo, str)
        and titulo.strip() != ""
        and isinstance(prioridade, int)
        and not isinstance(prioridade, bool)
        and 0 <= prioridade <= 5
        and isinstance(concluida, bool)
    )


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Devolve as tarefas válidas e pendentes, da maior para a menor prioridade.

    A entrada não é alterada. Cada item devolvido é uma cópia rasa independente
    do dicionário original, de modo que ocorrências repetidas recebem cópias
    distintas e campos extras são preservados.
    """
    if not isinstance(tarefas, list):
        return []

    pendentes = [t for t in tarefas if _valida(t) and t["concluida"] is False]
    # sorted é estável: empates mantêm a ordem original da entrada.
    pendentes.sort(key=lambda t: t["prioridade"], reverse=True)
    return [dict(t) for t in pendentes]
