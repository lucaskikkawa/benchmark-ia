CARACTERES_ESPECIAIS_PERMITIDOS = set("!@#$%^&*()-_+=")


class ValidadorSenha:
    """Validador de senhas e políticas de segurança."""

    def __init__(self, min_tam: int = 8, max_tam: int = 64) -> None:
        self.min_tam = min_tam
        self.max_tam = max_tam

    def validar(self, senha: str) -> tuple[bool, list[str]]:
        erros: list[str] = []

        if len(senha) < self.min_tam:
            erros.append(f"A senha deve ter pelo menos {self.min_tam} caracteres.")

        if len(senha) > self.max_tam:
            erros.append(f"A senha deve ter no máximo {self.max_tam} caracteres.")

        if not any(c.isupper() for c in senha):
            erros.append("A senha deve conter pelo menos uma letra maiúscula.")

        if not any(c.islower() for c in senha):
            erros.append("A senha deve conter pelo menos uma letra minúscula.")

        if not any(c.isdigit() for c in senha):
            erros.append("A senha deve conter pelo menos um dígito numérico.")

        if not any(c in CARACTERES_ESPECIAIS_PERMITIDOS for c in senha):
            erros.append("A senha deve conter pelo menos um caractere especial permitido.")

        if any(c.isspace() for c in senha):
            erros.append("A senha não pode conter espaços em branco.")

        for i in range(len(senha) - 2):
            if senha[i] == senha[i + 1] == senha[i + 2]:
                erros.append("A senha não pode conter 3 caracteres repetidos consecutivos.")
                break

        valida = len(erros) == 0
        return valida, erros

    def calcular_forca(self, senha: str) -> str:
        valida, _ = self.validar(senha)
        if not valida:
            return "invalida"

        tam = len(senha)
        if tam < 10:
            return "fraca"
        if tam < 14:
            return "media"
        return "forte"
