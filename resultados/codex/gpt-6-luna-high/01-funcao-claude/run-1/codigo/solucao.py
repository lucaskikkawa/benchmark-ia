"""Parser de durações humanas para segundos."""


_UNIDADES = {
    "w": (0, 604800),
    "d": (1, 86400),
    "h": (2, 3600),
    "m": (3, 60),
    "s": (4, 1),
}


def _valor_decimal(texto: str, inicio: int, fim: int) -> int:
    """Converte os dígitos ASCII do intervalo sem limite de tamanho textual."""
    valor = 0
    posicao = inicio
    while posicao < fim:
        # Cada conversão abaixo contém no máximo nove dígitos, abaixo do
        # limite de segurança de conversão decimal de int do Python.
        proximo = min(posicao + 9, fim)
        bloco = int(texto[posicao:proximo])
        tamanho = proximo - posicao
        valor = valor * (10 ** tamanho) + bloco
        posicao = proximo
    return valor


def parse_duracao(texto: str) -> int:
    """Interpreta uma duração como ``1w 2d3h`` e retorna seus segundos."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    tamanho = len(texto)
    i = 0
    anterior = -1
    quantidade = 0
    total = 0

    while i < tamanho:
        # Espaços em branco só podem separar componentes ou envolver a duração.
        while i < tamanho and texto[i].isspace():
            i += 1
        if i == tamanho:
            break

        inicio_digitos = i
        while i < tamanho and "0" <= texto[i] <= "9":
            i += 1
        if i == inicio_digitos:
            raise ValueError("esperado um número ASCII seguido de uma unidade")

        fim_digitos = i
        if i == tamanho:
            raise ValueError("número sem unidade")

        unidade = texto[i]
        # Comparações explícitas impedem que letras Unicode parecidas sejam aceitas.
        if "A" <= unidade <= "Z":
            unidade = chr(ord(unidade) + (ord("a") - ord("A")))
        info = _UNIDADES.get(unidade)
        if info is None:
            raise ValueError("unidade desconhecida")

        ordem, multiplicador = info
        if ordem <= anterior:
            raise ValueError("unidades fora de ordem ou repetidas")

        valor = _valor_decimal(texto, inicio_digitos, fim_digitos)
        total += valor * multiplicador
        anterior = ordem
        quantidade += 1
        i += 1

        # Próximo caractere deve iniciar outro componente ou ser espaço.
        if i < tamanho and not texto[i].isspace() and not ("0" <= texto[i] <= "9"):
            raise ValueError("texto extra após componente")

    if quantidade == 0:
        raise ValueError("duração vazia")
    return total
