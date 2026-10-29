"""Utilitários para intervalos fechados de inteiros."""


def mesclar_intervalos(intervalos):
    """Une intervalos fechados [inicio, fim] que se sobrepõem ou se tocam.

    - Cada intervalo é uma tupla (inicio, fim) de inteiros com inicio <= fim;
      caso contrário, levanta ValueError.
    - Intervalos que se sobrepõem ou se tocam (fim de um == inicio do outro)
      viram um só.
    - A entrada pode estar em qualquer ordem e NÃO deve ser modificada.
    - Retorna uma nova lista de tuplas, ordenada por inicio, sem sobreposições.
    - Lista vazia retorna lista vazia.
    """
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio}, {fim})")

    resultado = []
    for inicio, fim in sorted(intervalos):
        if resultado and inicio <= resultado[-1][1]:
            # Sobreposição ou contato: estende o último sem encolhê-lo
            # (o intervalo atual pode estar contido no anterior).
            resultado[-1][1] = max(resultado[-1][1], fim)
        else:
            resultado.append([inicio, fim])
    return [tuple(i) for i in resultado]


def total_coberto(intervalos):
    """Comprimento total coberto pela união dos intervalos (soma de fim - inicio).

    Lista vazia retorna 0. Mesmas validações de mesclar_intervalos.
    """
    return sum(fim - inicio for inicio, fim in mesclar_intervalos(intervalos))
