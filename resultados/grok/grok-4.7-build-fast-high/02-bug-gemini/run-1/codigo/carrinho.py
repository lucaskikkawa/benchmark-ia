import copy


class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        if itens is None:
            self.itens = {}
        else:
            # Cópia isolada do mapeamento e de cada dicionário interno.
            self.itens = {
                nome: copy.deepcopy(dados) for nome, dados in itens.items()
            }
        self.cupom_desconto = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        _validar_texto_nao_vazio(nome, "nome")
        _validar_numero(preco, "preco", minimo=0, exclusivo=True)
        _validar_quantidade_positiva(quantidade)

        if nome in self.itens:
            self.itens[nome]["quantidade"] += quantidade
            self.itens[nome]["preco"] = preco
        else:
            self.itens[nome] = {"preco": preco, "quantidade": quantidade}

    def remover_item(self, nome: str, quantidade: int | None = None) -> None:
        if nome not in self.itens:
            raise KeyError(f"Item '{nome}' não encontrado no carrinho.")

        if quantidade is not None:
            _validar_quantidade_positiva(quantidade)
            if quantidade >= self.itens[nome]["quantidade"]:
                del self.itens[nome]
            else:
                self.itens[nome]["quantidade"] -= quantidade
        else:
            del self.itens[nome]

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        _validar_texto_nao_vazio(codigo, "codigo")
        _validar_numero(
            desconto_porcentagem,
            "desconto_porcentagem",
            minimo=0,
            maximo=100,
        )
        self.cupom_desconto = {
            "codigo": codigo,
            "porcentagem": desconto_porcentagem,
        }

    def remover_cupom(self) -> None:
        self.cupom_desconto = None

    def calcular_subtotal(self) -> float:
        subtotal = 0.0
        for item in self.itens.values():
            subtotal += item["preco"] * item["quantidade"]
        return float(round(subtotal, 2))

    def calcular_desconto(self) -> float:
        if not self.cupom_desconto:
            return 0.0
        subtotal = self.calcular_subtotal()
        porcentagem = self.cupom_desconto["porcentagem"]
        return float(round(subtotal * (porcentagem / 100), 2))

    def calcular_total(self) -> float:
        total = round(self.calcular_subtotal() - self.calcular_desconto(), 2)
        return float(max(0.0, total))

    def listar_itens(self) -> list[dict]:
        resultado = []
        for nome in sorted(self.itens):
            dados = self.itens[nome]
            resultado.append(
                {
                    "nome": nome,
                    "preco": dados["preco"],
                    "quantidade": dados["quantidade"],
                    "total": float(round(dados["preco"] * dados["quantidade"], 2)),
                }
            )
        return resultado


def _validar_texto_nao_vazio(valor: object, campo: str) -> None:
    if not isinstance(valor, str):
        raise TypeError(f"{campo} deve ser uma string.")
    if valor.strip() == "":
        raise ValueError(f"{campo} não pode ser vazio.")


def _validar_numero(
    valor: object,
    campo: str,
    *,
    minimo: float,
    maximo: float | None = None,
    exclusivo: bool = False,
) -> None:
    # bool é subclasse de int e não conta como número neste carrinho.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{campo} deve ser int ou float.")
    if exclusivo:
        invalido = valor <= minimo or (maximo is not None and valor >= maximo)
    else:
        invalido = valor < minimo or (maximo is not None and valor > maximo)
    if invalido:
        if maximo is None:
            raise ValueError(f"{campo} deve ser estritamente positivo.")
        raise ValueError(f"{campo} deve estar entre {minimo} e {maximo}.")


def _validar_quantidade_positiva(quantidade: object) -> None:
    if type(quantidade) is not int:
        raise TypeError("quantidade deve ser um int.")
    if quantidade <= 0:
        raise ValueError("quantidade deve ser estritamente positiva.")
