"""Utilitários para intervalos fechados de inteiros."""


def _eh_int(valor):
    """Retorna True se valor for int e não bool."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def _validar_intervalo(par):
    """Valida um par (inicio, fim) e o retorna como tupla de dois ints."""
    if not isinstance(par, (tuple, list)):
        raise TypeError(
            f"cada intervalo deve ser tupla ou lista, recebido {type(par).__name__}"
        )
    if len(par) != 2:
        raise ValueError(
            f"cada intervalo deve ter exatamente 2 elementos, recebido {len(par)}"
        )
    inicio, fim = par
    if not (_eh_int(inicio) and _eh_int(fim)):
        raise TypeError(
            f"inicio e fim devem ser int (não bool): ({inicio!r}, {fim!r})"
        )
    if inicio > fim:
        raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
    return (inicio, fim)


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
    validados = [_validar_intervalo(par) for par in intervalos]
    if not validados:
        return []

    validados.sort()
    resultado = [validados[0]]
    for inicio, fim in validados[1:]:
        ultimo_inicio, ultimo_fim = resultado[-1]
        if inicio <= ultimo_fim:
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
