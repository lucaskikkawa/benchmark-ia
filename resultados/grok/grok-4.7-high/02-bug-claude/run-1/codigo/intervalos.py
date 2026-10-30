"""Utilitários para intervalos fechados de inteiros."""


def _como_intervalo(par):
    """Valida um par (inicio, fim) e devolve uma tupla de int.

    bool é rejeitado porque é subclasse de int. A exceção de formato
    (não-iterável ou tamanho diferente de 2) é a mesma do desempacotamento.
    """
    inicio, fim = par
    if (
        isinstance(inicio, bool)
        or isinstance(fim, bool)
        or not isinstance(inicio, int)
        or not isinstance(fim, int)
    ):
        raise TypeError(
            f"inicio e fim devem ser int (bool não é aceito): ({inicio!r}, {fim!r})"
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
    # Materializa e valida tudo antes de ordenar ou unir, sem alterar a entrada.
    validados = [_como_intervalo(par) for par in intervalos]
    if not validados:
        return []

    validados.sort()
    resultado = [validados[0]]
    for inicio, fim in validados[1:]:
        ultimo_inicio, ultimo_fim = resultado[-1]
        # Fechados: fim == inicio do seguinte também se tocam.
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
