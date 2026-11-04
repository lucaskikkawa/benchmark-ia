import copy


class CarrinhoDeCompras:
    def __init__(self, itens: dict | None = None) -> None:
        if itens is None:
            self.itens: dict = {}
        else:
            self.itens = copy.deepcopy(itens)
        self.cupom_desconto: dict | None = None

    def adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None:
        self._validar_nome(nome)
        self._validar_numero_positivo(preco, "preco")
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
            if type(quantidade) is not int:
                raise TypeError("quantidade deve ser um inteiro.")
            if quantidade <= 0:
                raise ValueError("quantidade deve ser estritamente positiva.")

            quantidade_atual = self.itens[nome]["quantidade"]
            if quantidade >= quantidade_atual:
                del self.itens[nome]
            else:
                self.itens[nome]["quantidade"] -= quantidade
        else:
            del self.itens[nome]

    def aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None:
        self._validar_nome(codigo, campo="codigo")
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
        return float(round(subtotal, 2))

    def calcular_desconto(self) -> float:
        if not self.cupom_desconto:
            return 0.0
        desconto = self.calcular_subtotal() * (self.cupom_desconto["porcentagem"] / 100)
        return float(round(desconto, 2))

    def calcular_total(self) -> float:
        total = round(self.calcular_subtotal() - self.calcular_desconto(), 2)
        if total > 0:
            return float(total)
        return 0.0

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

    @staticmethod
    def _validar_nome(nome: str, campo: str = "nome") -> None:
        if not isinstance(nome, str):
            raise TypeError(f"{campo} deve ser uma string.")
        if nome.strip() == "":
            raise ValueError(f"{campo} não pode ser vazio.")

    @staticmethod
    def _validar_numero_positivo(valor: float, campo: str) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError(f"{campo} deve ser numérico.")
        if valor <= 0:
            raise ValueError(f"{campo} deve ser estritamente positivo.")

    @staticmethod
    def _validar_quantidade_positiva(quantidade: int) -> None:
        if type(quantidade) is not int:
            raise TypeError("quantidade deve ser um inteiro.")
        if quantidade <= 0:
            raise ValueError("quantidade deve ser estritamente positiva.")

    @staticmethod
    def _validar_porcentagem(desconto_porcentagem: float) -> None:
        if isinstance(desconto_porcentagem, bool) or not isinstance(
            desconto_porcentagem, (int, float)
        ):
            raise TypeError("desconto_porcentagem deve ser numérico.")
        if desconto_porcentagem < 0 or desconto_porcentagem > 100:
            raise ValueError("desconto_porcentagem deve estar entre 0 e 100.")
