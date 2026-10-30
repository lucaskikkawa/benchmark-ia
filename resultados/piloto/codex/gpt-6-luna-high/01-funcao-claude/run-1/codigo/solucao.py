def parse_duracao(texto: str) -> int:
    """Converte uma duração como ``1h30m`` no total de segundos."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    texto = texto.strip()
    if not texto:
        raise ValueError("a duração não pode ser vazia")

    unidades = {"d": (0, 86_400), "h": (1, 3_600), "m": (2, 60), "s": (3, 1)}
    total = 0
    ultima_ordem = -1
    posicao = 0
    componentes = 0

    while posicao < len(texto):
        inicio_numero = posicao
        while posicao < len(texto) and "0" <= texto[posicao] <= "9":
            posicao += 1
        if posicao == inicio_numero:
            raise ValueError("componente inválido")

        if posicao == len(texto):
            raise ValueError("número sem unidade")

        unidade = texto[posicao].lower()
        if unidade not in unidades:
            raise ValueError("unidade inválida")
        ordem, fator = unidades[unidade]
        if ordem <= ultima_ordem:
            raise ValueError("unidades fora de ordem ou repetidas")

        valor = 0
        for digito in texto[inicio_numero:posicao]:
            valor = valor * 10 + (ord(digito) - ord("0"))
        total += valor * fator
        ultima_ordem = ordem
        componentes += 1
        posicao += 1

        # Espaços são permitidos apenas entre componentes.
        while posicao < len(texto) and texto[posicao].isspace():
            posicao += 1

    if componentes == 0:
        raise ValueError("a duração deve conter ao menos um componente")

    return total
