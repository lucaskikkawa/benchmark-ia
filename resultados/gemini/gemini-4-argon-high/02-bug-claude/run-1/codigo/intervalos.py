"""Utilitários para intervalos fechados de inteiros."""


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
    pares = []
    for inicio, fim in intervalos:
        if (
            not isinstance(inicio, int)
            or isinstance(inicio, bool)
            or not isinstance(fim, int)
            or isinstance(fim, bool)
        ):
            raise TypeError(f"inicio e fim devem ser int: ({inicio!r}, {fim!r})")
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
        pares.append((inicio, fim))

    if not pares:
        return []

    pares.sort()
    resultado = [list(pares[0])]
    for inicio, fim in pares[1:]:
        ultimo = resultado[-1]
        if inicio <= ultimo[1]:
            ultimo[1] = max(ultimo[1], fim)
        else:
            resultado.append([inicio, fim])
    return [tuple(i) for i in resultado]


def total_coberto(intervalos):
    """Comprimento total coberto pela união dos intervalos (soma de fim - inicio).

    Aceita as mesmas entradas e faz as mesmas validações de mesclar_intervalos.
    Lista vazia retorna 0.
    """
    return sum(fim - inicio for inicio, fim in mesclar_intervalos(intervalos))
