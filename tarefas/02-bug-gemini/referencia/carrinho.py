class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        self.itens: dict[str, dict] = {}
        if itens is not None:
            for nome, dados in itens.items():
                self.itens[str(nome)] = {
                    "preco": float(dados["preco"]),
                    "quantidade": int(dados["quantidade"]),
                }
        self.cupom_desconto: dict | None = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        if not isinstance(nome, str):
            raise TypeError("Nome do item deve ser string.")
        if not nome.strip():
            raise ValueError("Nome do item não pode ser vazio.")

        if type(preco) is bool or type(preco) not in (int, float):
            raise TypeError("Preço deve ser um valor numérico.")
        if preco <= 0:
            raise ValueError("O preço deve ser maior que zero.")

        if type(quantidade) is not int:
            raise TypeError("A quantidade deve ser um inteiro.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        if nome in self.itens:
            self.itens[nome]["quantidade"] += quantidade
            self.itens[nome]["preco"] = float(preco)
        else:
            self.itens[nome] = {"preco": float(preco), "quantidade": int(quantidade)}

    def remover_item(self, nome: str, quantidade: int | None = None) -> None:
        if nome not in self.itens:
            raise KeyError(f"Item '{nome}' não encontrado no carrinho.")

        if quantidade is not None:
            if type(quantidade) is not int:
                raise TypeError("Quantidade a remover deve ser um inteiro.")
            if quantidade <= 0:
                raise ValueError("Quantidade a remover deve ser maior que zero.")
            if quantidade >= self.itens[nome]["quantidade"]:
                del self.itens[nome]
            else:
                self.itens[nome]["quantidade"] -= quantidade
        else:
            del self.itens[nome]

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        if not isinstance(codigo, str):
            raise TypeError("Código do cupom deve ser string.")
        if not codigo.strip():
            raise ValueError("Código do cupom não pode ser vazio.")

        if type(desconto_porcentagem) is bool or type(desconto_porcentagem) not in (int, float):
            raise TypeError("Porcentagem de desconto deve ser numérica.")
        if not (0 <= desconto_porcentagem <= 100):
            raise ValueError("O desconto deve estar entre 0 e 100%.")

        self.cupom_desconto = {
            "codigo": codigo,
            "porcentagem": float(desconto_porcentagem),
        }

    def remover_cupom(self) -> None:
        self.cupom_desconto = None

    def calcular_subtotal(self) -> float:
        subtotal = sum(item["preco"] * item["quantidade"] for item in self.itens.values())
        return round(subtotal, 2)

    def calcular_desconto(self) -> float:
        if not self.cupom_desconto:
            return 0.0
        subtotal = self.calcular_subtotal()
        desconto = subtotal * (self.cupom_desconto["porcentagem"] / 100.0)
        return round(desconto, 2)

    def calcular_total(self) -> float:
        total = self.calcular_subtotal() - self.calcular_desconto()
        return max(0.0, round(total, 2))

    def listar_itens(self) -> list[dict]:
        resultado = []
        for nome in sorted(self.itens.keys()):
            dados = self.itens[nome]
            resultado.append({
                "nome": nome,
                "preco": dados["preco"],
                "quantidade": dados["quantidade"],
                "total": round(dados["preco"] * dados["quantidade"], 2),
            })
        return resultado
