def _eh_numero(valor) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_texto(valor, campo: str) -> None:
    if not isinstance(valor, str):
        raise TypeError(f"'{campo}' deve ser uma string.")
    if valor.strip() == "":
        raise ValueError(f"'{campo}' não pode ser vazio.")


class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        if itens is None:
            self.itens = {}
        else:
            if not isinstance(itens, dict):
                raise TypeError("'itens' deve ser um dicionário.")
            self.itens = {nome: dict(dados) for nome, dados in itens.items()}
        self.cupom_desconto = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        _validar_texto(nome, "nome")
        if not _eh_numero(preco):
            raise TypeError("'preco' deve ser numérico.")
        if preco <= 0:
            raise ValueError("'preco' deve ser maior que zero.")
        if type(quantidade) is not int:
            raise TypeError("'quantidade' deve ser um inteiro.")
        if quantidade <= 0:
            raise ValueError("'quantidade' deve ser maior que zero.")

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
                raise TypeError("'quantidade' deve ser um inteiro.")
            if quantidade <= 0:
                raise ValueError("'quantidade' deve ser maior que zero.")

        if quantidade is None or quantidade >= self.itens[nome]["quantidade"]:
            del self.itens[nome]
        else:
            self.itens[nome]["quantidade"] -= quantidade

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        _validar_texto(codigo, "codigo")
        if not _eh_numero(desconto_porcentagem):
            raise TypeError("'desconto_porcentagem' deve ser numérico.")
        if desconto_porcentagem < 0 or desconto_porcentagem > 100:
            raise ValueError("'desconto_porcentagem' deve estar entre 0 e 100.")
        self.cupom_desconto = {"codigo": codigo, "porcentagem": desconto_porcentagem}

    def remover_cupom(self) -> None:
        self.cupom_desconto = None

    def calcular_subtotal(self) -> float:
        subtotal = sum(item["preco"] * item["quantidade"] for item in self.itens.values())
        return round(float(subtotal), 2)

    def calcular_desconto(self) -> float:
        if not self.cupom_desconto:
            return 0.0
        porcentagem = self.cupom_desconto["porcentagem"]
        return round(self.calcular_subtotal() * (porcentagem / 100), 2)

    def calcular_total(self) -> float:
        total = round(self.calcular_subtotal() - self.calcular_desconto(), 2)
        return max(total, 0.0)

    def listar_itens(self) -> list[dict]:
        return [
            {
                "nome": nome,
                "preco": self.itens[nome]["preco"],
                "quantidade": self.itens[nome]["quantidade"],
                "total": round(self.itens[nome]["preco"] * self.itens[nome]["quantidade"], 2),
            }
            for nome in sorted(self.itens)
        ]
