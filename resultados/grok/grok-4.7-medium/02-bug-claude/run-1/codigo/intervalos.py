"""Utilitários para intervalos fechados de inteiros."""


def _validar_par(par):
    """Valida um par (inicio, fim) e devolve a tupla de inteiros."""
    try:
        inicio, fim = par
    except (TypeError, ValueError):
        raise TypeError(
            "cada intervalo deve ser um par (inicio, fim) de inteiros"
        ) from None
    if type(inicio) is not int or type(fim) is not int:
        raise TypeError(
            f"inicio e fim devem ser int, recebido ({inicio!r}, {fim!r})"
        )
    if inicio > fim:
        raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
    return inicio, fim


def mesclar_intervalos(intervalos):
    """Une intervalos fechados [inicio, fim] que se sobrepõem ou se tocam.

    - ``intervalos`` pode ser qualquer iterável (lista, tupla, gerador...) de
      pares (inicio, fim); cada par pode ser tupla ou lista de 2 elementos.
    - inicio e fim devem ser ``int`` (bool NÃO é aceito); caso contrário,
      levanta TypeError.
    - Cada intervalo deve ter inicio <= fim; caso contrário, levanta ValueError.
    - Todos os intervalos são validados antes de qualquer resultado ser produzido.
    - Intervalos que se sobrepõem ou se tocam (fim de um == inicio do outro)
      viram um só.
    - A entrada pode estar em qualquer ordem e NÃO deve ser modificada.
    - Retorna uma nova lista de tuplas, ordenada por inicio, sem sobreposições.
    - Lista vazia retorna lista vazia.
    """
    normalizados = [_validar_par(par) for par in intervalos]
    normalizados.sort()

    resultado = []
    for inicio, fim in normalizados:
        if resultado and inicio <= resultado[-1][1]:
            ultimo_inicio, ultimo_fim = resultado[-1]
            resultado[-1] = (ultimo_inicio, max(ultimo_fim, fim))
        else:
            resultado.append((inicio, fim))
    return resultado


def total_coberto(intervalos):
    """Comprimento total coberto pela união dos intervalos (soma de fim - inicio).

    Aceita as mesmas entradas e faz as mesmas validações de mesclar_intervalos.
    Lista vazia retorna 0.
    """
    return sum(fim - inicio for inicio, fim in mesclar_intervalos(intervalos))
