class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        if itens is None:
            self.itens = {}
        else:
            self.itens = {
                nome: dict(dados) for nome, dados in itens.items()
            }
        self.cupom_desconto = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        self._validar_nome(nome, "nome")
        self._validar_preco(preco)
        self._validar_quantidade_positiva(quantidade)

        if nome in self.itens:
            self.itens[nome]["quantidade"] += quantidade
            self.itens[nome]["preco"] = preco
        else:
            self.itens[nome] = {"preco": preco, "quantidade": quantidade}

    def remover_item(self, nome: str, quantidade: int | None = None) -> None:
        if nome not in self.itens:
            raise KeyError(f"Item '{nome}' não encontrado no carrinho.")

        if quantidade is not None:
            if isinstance(quantidade, bool) or type(quantidade) is not int:
                raise TypeError("quantidade deve ser um número inteiro.")
            if quantidade <= 0:
                raise ValueError("quantidade deve ser estritamente positiva.")
            if quantidade >= self.itens[nome]["quantidade"]:
                del self.itens[nome]
            else:
                self.itens[nome]["quantidade"] -= quantidade
        else:
            del self.itens[nome]

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        self._validar_nome(codigo, "codigo")
        self._validar_porcentagem(desconto_porcentagem)
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
        return round(subtotal, 2)

    def calcular_desconto(self) -> float:
        if not self.cupom_desconto:
            return 0.0
        subtotal = self.calcular_subtotal()
        desconto = subtotal * (self.cupom_desconto["porcentagem"] / 100)
        return round(desconto, 2)

    def calcular_total(self) -> float:
        total = self.calcular_subtotal() - self.calcular_desconto()
        return max(0.0, round(total, 2))

    def listar_itens(self) -> list[dict]:
        resultado = []
        for nome, dados in sorted(self.itens.items()):
            resultado.append({
                "nome": nome,
                "preco": dados["preco"],
                "quantidade": dados["quantidade"],
                "total": round(dados["preco"] * dados["quantidade"], 2),
            })
        return resultado

    @staticmethod
    def _validar_nome(valor: str, campo: str) -> None:
        if not isinstance(valor, str):
            raise TypeError(f"{campo} deve ser uma string.")
        if valor.strip() == "":
            raise ValueError(f"{campo} não pode ser vazio.")

    @staticmethod
    def _validar_preco(preco: float) -> None:
        if isinstance(preco, bool) or not isinstance(preco, (int, float)):
            raise TypeError("preco deve ser um número (int ou float).")
        if preco <= 0:
            raise ValueError("preco deve ser estritamente positivo.")

    @staticmethod
    def _validar_quantidade_positiva(quantidade: int) -> None:
        if isinstance(quantidade, bool) or type(quantidade) is not int:
            raise TypeError("quantidade deve ser um número inteiro.")
        if quantidade <= 0:
            raise ValueError("quantidade deve ser estritamente positiva.")

    @staticmethod
    def _validar_porcentagem(porcentagem: float) -> None:
        if isinstance(porcentagem, bool) or not isinstance(porcentagem, (int, float)):
            raise TypeError("desconto_porcentagem deve ser um número (int ou float).")
        if porcentagem < 0 or porcentagem > 100:
            raise ValueError("desconto_porcentagem deve estar entre 0 e 100.")
