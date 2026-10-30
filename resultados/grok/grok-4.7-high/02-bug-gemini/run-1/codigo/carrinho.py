class CarrinhoDeCompras:
    # BUG 1: argumento mutável default compartilha estado entre instâncias
    def __init__(self, itens={}):
        self.itens = itens
        self.cupom_desconto = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        # BUG 2: não valida preço nem quantidade <= 0
        if nome in self.itens:
            self.itens[nome]["quantidade"] += quantidade
            self.itens[nome]["preco"] = preco
        else:
            self.itens[nome] = {"preco": preco, "quantidade": quantidade}

    def remover_item(self, nome: str, quantidade: int | None = None) -> None:
        if nome not in self.itens:
            raise KeyError(f"Item '{nome}' não encontrado no carrinho.")

        # BUG 3: não valida quantidade <= 0 (deveria lançar ValueError)
        # e não remove o item se quantidade for >= ao total atual
        if quantidade is None:
            del self.itens[nome]
        else:
            self.itens[nome]["quantidade"] -= quantidade
            # BUG: não remove a chave se quantidade resultante for <= 0

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        # BUG 4: não valida limites 0 a 100 de desconto_porcentagem
        self.cupom_desconto = {"codigo": codigo, "porcentagem": desconto_porcentagem}

    def remover_cupom(self) -> None:
        self.cupom_desconto = None

    def calcular_subtotal(self) -> float:
        # BUG 5: ponto flutuante sem arredondamento
        subtotal = 0.0
        for item in self.itens.values():
            subtotal += item["preco"] * item["quantidade"]
        return subtotal

    def calcular_desconto(self) -> float:
        # BUG 6: lógica de desconto errada
        if not self.cupom_desconto:
            return 0.0
        return self.calcular_subtotal() * self.cupom_desconto["porcentagem"]

    def calcular_total(self) -> float:
        return self.calcular_subtotal() - self.calcular_desconto()

    def listar_itens(self) -> list[dict]:
        resultado = []
        for nome, dados in self.itens.items():
            resultado.append({
                "nome": nome,
                "preco": dados["preco"],
                "quantidade": dados["quantidade"],
                "total": round(dados["preco"] * dados["quantidade"], 2)
            })
        return resultado
