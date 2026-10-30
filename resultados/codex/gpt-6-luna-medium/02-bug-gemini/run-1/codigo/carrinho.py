from copy import deepcopy


class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        # Cada carrinho mantém seu próprio estado, inclusive os registros dos itens.
        self.itens = deepcopy(itens) if itens is not None else {}
        self.cupom_desconto = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        if not isinstance(nome, str):
            raise TypeError("O nome do item deve ser uma string.")
        if nome.strip() == "":
            raise ValueError("O nome do item não pode ser vazio.")

        if isinstance(preco, bool) or not isinstance(preco, (int, float)):
            raise TypeError("O preço deve ser um número.")
        if not preco > 0:
            raise ValueError("O preço deve ser estritamente positivo.")

        if type(quantidade) is not int:
            raise TypeError("A quantidade deve ser um número inteiro.")
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
                raise TypeError("A quantidade deve ser um número inteiro.")
            if quantidade <= 0:
                raise ValueError("A quantidade deve ser estritamente positiva.")

            quantidade_atual = self.itens[nome]["quantidade"]
            if quantidade < quantidade_atual:
                self.itens[nome]["quantidade"] -= quantidade
                return

        del self.itens[nome]

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        if not isinstance(codigo, str):
            raise TypeError("O código do cupom deve ser uma string.")
        if codigo.strip() == "":
            raise ValueError("O código do cupom não pode ser vazio.")

        if isinstance(desconto_porcentagem, bool) or not isinstance(
            desconto_porcentagem, (int, float)
        ):
            raise TypeError("O desconto deve ser um número.")
        if not 0 <= desconto_porcentagem <= 100:
            raise ValueError("O desconto deve estar entre 0 e 100.")

        self.cupom_desconto = {
            "codigo": codigo,
            "porcentagem": desconto_porcentagem,
        }

    def remover_cupom(self) -> None:
        self.cupom_desconto = None

    def calcular_subtotal(self) -> float:
        subtotal = sum(
            item["preco"] * item["quantidade"]
            for item in self.itens.values()
        )
        return round(subtotal, 2)

    def calcular_desconto(self) -> float:
        if self.cupom_desconto is None:
            return 0.0
        desconto = self.calcular_subtotal() * (
            self.cupom_desconto["porcentagem"] / 100
        )
        return round(desconto, 2)

    def calcular_total(self) -> float:
        return max(0.0, round(self.calcular_subtotal() - self.calcular_desconto(), 2))

    def listar_itens(self) -> list[dict]:
        return [
            {
                "nome": nome,
                "preco": self.itens[nome]["preco"],
                "quantidade": self.itens[nome]["quantidade"],
                "total": round(
                    self.itens[nome]["preco"] * self.itens[nome]["quantidade"],
                    2,
                ),
            }
            for nome in sorted(self.itens)
        ]
