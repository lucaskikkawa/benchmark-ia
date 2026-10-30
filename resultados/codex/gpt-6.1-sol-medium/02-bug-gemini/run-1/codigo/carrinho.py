from copy import deepcopy


class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        self.itens = deepcopy(itens) if itens is not None else {}
        self.cupom_desconto = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        if not isinstance(nome, str):
            raise TypeError("O nome deve ser uma string.")
        if not nome.strip():
            raise ValueError("O nome não pode ser vazio.")
        if isinstance(preco, bool) or not isinstance(preco, (int, float)):
            raise TypeError("O preço deve ser um número.")
        if not preco > 0:
            raise ValueError("O preço deve ser estritamente positivo.")
        if type(quantidade) is not int:
            raise TypeError("A quantidade deve ser um inteiro.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser estritamente positiva.")

        if nome in self.itens:
            self.itens[nome]["quantidade"] += quantidade
            self.itens[nome]["preco"] = preco
        else:
            self.itens[nome] = {"preco": preco, "quantidade": quantidade}

    def remover_item(self, nome: str, quantidade: int | None = None) -> None:
        if nome not in self.itens:
            raise KeyError(f"Item '{nome}' não encontrado no carrinho.")

        if quantidade is not None:
            if type(quantidade) is not int:
                raise TypeError("A quantidade deve ser um inteiro.")
            if quantidade <= 0:
                raise ValueError("A quantidade deve ser estritamente positiva.")

        if quantidade is None or quantidade >= self.itens[nome]["quantidade"]:
            del self.itens[nome]
        else:
            self.itens[nome]["quantidade"] -= quantidade

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        if not isinstance(codigo, str):
            raise TypeError("O código deve ser uma string.")
        if not codigo.strip():
            raise ValueError("O código não pode ser vazio.")
        if isinstance(desconto_porcentagem, bool) or not isinstance(
            desconto_porcentagem, (int, float)
        ):
            raise TypeError("O desconto deve ser um número.")
        if not 0 <= desconto_porcentagem <= 100:
            raise ValueError("O desconto deve estar entre 0 e 100.")

        self.cupom_desconto = {"codigo": codigo, "porcentagem": desconto_porcentagem}

    def remover_cupom(self) -> None:
        self.cupom_desconto = None

    def calcular_subtotal(self) -> float:
        subtotal = 0.0
        for item in self.itens.values():
            subtotal += item["preco"] * item["quantidade"]
        return round(subtotal, 2)

    def calcular_desconto(self) -> float:
        if not self.cupom_desconto:
            return 0.0
        return round(
            self.calcular_subtotal() * (self.cupom_desconto["porcentagem"] / 100),
            2,
        )

    def calcular_total(self) -> float:
        return max(0.0, round(self.calcular_subtotal() - self.calcular_desconto(), 2))

    def listar_itens(self) -> list[dict]:
        resultado = []
        for nome in sorted(self.itens):
            dados = self.itens[nome]
            resultado.append({
                "nome": nome,
                "preco": dados["preco"],
                "quantidade": dados["quantidade"],
                "total": round(dados["preco"] * dados["quantidade"], 2)
            })
        return resultado
