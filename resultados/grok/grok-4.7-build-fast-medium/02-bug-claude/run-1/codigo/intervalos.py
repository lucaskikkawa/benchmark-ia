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
    for intervalo in intervalos:
        inicio, fim = intervalo
        if (
            not isinstance(inicio, int)
            or not isinstance(fim, int)
            or isinstance(inicio, bool)
            or isinstance(fim, bool)
        ):
            raise TypeError(
                f"inicio e fim devem ser int, obtido ({inicio!r}, {fim!r})"
            )
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
        validados.append((inicio, fim))

    validados.sort()
    if not validados:
        return []

    resultado = [validados[0]]
    for inicio, fim in validados[1:]:
        ultimo_inicio, ultimo_fim = resultado[-1]
        # Fechados: fim == início seguinte também se toca e deve unir.
        if inicio <= ultimo_fim:
            if fim > ultimo_fim:
                resultado[-1] = (ultimo_inicio, fim)
        else:
            resultado.append((inicio, fim))
    return resultado


def total_coberto(intervalos):
    """Comprimento total coberto pela união dos intervalos (soma de fim - inicio).

    Aceita as mesmas entradas e faz as mesmas validações de mesclar_intervalos.
    Lista vazia retorna 0.
    """
    return sum(fim - inicio for inicio, fim in mesclar_intervalos(intervalos))
