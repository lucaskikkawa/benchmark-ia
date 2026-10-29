"""Utilitários para intervalos fechados de inteiros."""


def _validar(intervalos):
    """Materializa ``intervalos`` numa nova lista de tuplas, validando cada par."""
    validados = []
    for inicio, fim in intervalos:
        for valor in (inicio, fim):
            # bool é subclasse de int, mas não é aceito.
            if not isinstance(valor, int) or isinstance(valor, bool):
                raise TypeError(f"esperado int, recebido {type(valor).__name__}: {valor!r}")
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
        validados.append((inicio, fim))
    return validados


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
    # Copia validada: o iterável é percorrido uma única vez e a entrada não é alterada.
    resultado = []
    for inicio, fim in sorted(_validar(intervalos)):
        if resultado and inicio <= resultado[-1][1]:
            # Sobreposição ou contato: estende o último sem encolhê-lo
            # (o intervalo atual pode estar contido no anterior).
            resultado[-1][1] = max(resultado[-1][1], fim)
        else:
            resultado.append([inicio, fim])
    return [tuple(i) for i in resultado]


def total_coberto(intervalos):
    """Comprimento total coberto pela união dos intervalos (soma de fim - inicio).

    Aceita as mesmas entradas e faz as mesmas validações de mesclar_intervalos.
    Lista vazia retorna 0.
    """
    return sum(fim - inicio for inicio, fim in mesclar_intervalos(intervalos))
