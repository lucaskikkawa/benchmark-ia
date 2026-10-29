class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        self.itens: dict[str, dict] = dict(itens) if itens is not None else {}
        self.cupom_desconto: dict | None = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        if preco <= 0:
            raise ValueError("O preço deve ser maior que zero.")
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
            if quantidade <= 0:
                raise ValueError("Quantidade a remover deve ser maior que zero.")
            if quantidade >= self.itens[nome]["quantidade"]:
                del self.itens[nome]
            else:
                self.itens[nome]["quantidade"] -= quantidade
        else:
            del self.itens[nome]

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        if not (0 <= desconto_porcentagem <= 100):
            raise ValueError("O desconto deve estar entre 0 e 100%.")
        self.cupom_desconto = {
            "codigo": str(codigo),
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
