import copy


class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        # Cópia isolada: evita compartilhar estado entre instâncias e com o dicionário externo
        self.itens = copy.deepcopy(itens) if itens is not None else {}
        self.cupom_desconto = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        if not isinstance(nome, str):
            raise TypeError("O nome do item deve ser uma string.")
        if nome.strip() == "":
            raise ValueError("O nome do item não pode ser vazio.")

        if isinstance(preco, bool) or not isinstance(preco, (int, float)):
            raise TypeError("O preço deve ser int ou float.")
        if preco <= 0:
            raise ValueError("O preço deve ser maior que zero.")

        if type(quantidade) is not int:
            raise TypeError("A quantidade deve ser um inteiro.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        if nome in self.itens:
            self.itens[nome]["quantidade"] += quantidade
            self.itens[nome]["preco"] = preco
        else:
            self.itens[nome] = {"preco": preco, "quantidade": quantidade}

    def remover_item(self, nome: str, quantidade: int | None = None) -> None:
        if nome not in self.itens:
            raise KeyError(f"Item '{nome}' não encontrado no carrinho.")

        if quantidade is not None:
            if isinstance(quantidade, bool) or not isinstance(quantidade, int):
                raise TypeError("A quantidade deve ser um inteiro.")
            if quantidade <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")

        quantidade_atual = self.itens[nome]["quantidade"]
        if quantidade is None or quantidade >= quantidade_atual:
            del self.itens[nome]
        else:
            self.itens[nome]["quantidade"] -= quantidade

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        if not isinstance(codigo, str):
            raise TypeError("O código do cupom deve ser uma string.")
        if codigo.strip() == "":
            raise ValueError("O código do cupom não pode ser vazio.")

        if isinstance(desconto_porcentagem, bool) or not isinstance(desconto_porcentagem, (int, float)):
            raise TypeError("A porcentagem de desconto deve ser int ou float.")
        if not 0 <= desconto_porcentagem <= 100:
            raise ValueError("A porcentagem de desconto deve estar entre 0 e 100.")

        self.cupom_desconto = {"codigo": codigo, "porcentagem": desconto_porcentagem}

    def remover_cupom(self) -> None:
        self.cupom_desconto = None

    def calcular_subtotal(self) -> float:
        subtotal = sum(item["preco"] * item["quantidade"] for item in self.itens.values())
        return round(subtotal, 2)

    def calcular_desconto(self) -> float:
        if not self.cupom_desconto:
            return 0.0
        desconto = self.calcular_subtotal() * (self.cupom_desconto["porcentagem"] / 100)
        return round(desconto, 2)

    def calcular_total(self) -> float:
        total = self.calcular_subtotal() - self.calcular_desconto()
        return round(max(total, 0.0), 2)

    def listar_itens(self) -> list[dict]:
        return [
            {
                "nome": nome,
                "preco": dados["preco"],
                "quantidade": dados["quantidade"],
                "total": round(dados["preco"] * dados["quantidade"], 2),
            }
            for nome, dados in sorted(self.itens.items())
        ]
