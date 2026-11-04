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
    validados = []
    for item in intervalos:
        if not isinstance(item, (tuple, list)):
            raise TypeError(f"cada intervalo deve ser tupla ou lista: {item!r}")
        if len(item) != 2:
            raise ValueError(f"cada intervalo deve ter exatamente 2 elementos: {item!r}")
        inicio, fim = item
        if isinstance(inicio, bool) or not isinstance(inicio, int) or isinstance(fim, bool) or not isinstance(fim, int):
            raise TypeError(f"inicio e fim devem ser int (bool não é aceito): ({inicio!r}, {fim!r})")
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
        validados.append((inicio, fim))

    if not validados:
        return []

    validados.sort()
    resultado = []
    curr_inicio, curr_fim = validados[0]
    for inicio, fim in validados[1:]:
        if inicio <= curr_fim:
            if fim > curr_fim:
                curr_fim = fim
        else:
            resultado.append((curr_inicio, curr_fim))
            curr_inicio, curr_fim = inicio, fim
    resultado.append((curr_inicio, curr_fim))
    return resultado


def total_coberto(intervalos):
    """Comprimento total coberto pela união dos intervalos (soma de fim - inicio).

    Aceita as mesmas entradas e faz as mesmas validações de mesclar_intervalos.
    Lista vazia retorna 0.
    """
    return sum(fim - inicio for inicio, fim in mesclar_intervalos(intervalos))
