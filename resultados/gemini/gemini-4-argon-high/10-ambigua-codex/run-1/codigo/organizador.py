"""Módulo para organização de tarefas pendentes por prioridade."""

from typing import Any


def _tarefa_pendente_valida(tarefa: Any) -> bool:
    """Verifica se o item é um dicionário de tarefa válida e pendente."""
    if not isinstance(tarefa, dict):
        return False
    if tarefa.get("concluida") is not False:
        return False
    titulo = tarefa.get("titulo")
    if not isinstance(titulo, str) or len(titulo) == 0:
        return False
    prioridade = tarefa.get("prioridade")
    if isinstance(prioridade, bool) or not isinstance(prioridade, int):
        return False
    return 0 <= prioridade <= 5


def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    """Retorna cópias rasas das tarefas pendentes ordenadas por prioridade decrescente.

    Políticas adotadas (documentadas em SUPOSICOES.md):
    - Apenas tarefas válidas com ``concluida is False`` são incluídas.
    - Ordenação decrescente por ``prioridade`` (5 até 0), preservando a ordem
      original de entrada em caso de empate (ordenação estável).
    - Entradas inválidas (não-dicionários, campos obrigatórios ausentes, tipos
      incorretos ou prioridade fora de 0..5) são ignoradas.
    - Cada ocorrência na saída recebe uma nova cópia rasa (``dict.copy()``),
      preservando campos extras e a identidade de seus valores internos.
    """
    if not isinstance(tarefas, list):
        return []

    pendentes = [t.copy() for t in tarefas if _tarefa_pendente_valida(t)]
    pendentes.sort(key=lambda t: t["prioridade"], reverse=True)
    return pendentes
