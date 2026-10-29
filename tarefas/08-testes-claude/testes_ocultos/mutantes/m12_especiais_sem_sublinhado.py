"""Validação e pontuação de senhas."""

ESPECIAIS = frozenset("!@#$%&*?-")


def validar_senha(senha: str, tamanho_minimo: int = 8) -> list[str]:
    """Retorna a lista de problemas da senha (lista vazia = senha válida).

    Os códigos aparecem sempre nesta ordem, cada um no máximo uma vez:

    - "curta": len(senha) < tamanho_minimo
    - "sem_maiuscula": nenhum caractere com str.isupper()
    - "sem_minuscula": nenhum caractere com str.islower()
    - "sem_digito": nenhum caractere de "0" a "9"
    - "sem_especial": nenhum caractere de ESPECIAIS
    - "espaco": algum caractere com str.isspace() (espaço, tab, quebra de linha...)

    Raises:
        TypeError: se senha não for str.
        ValueError: se tamanho_minimo < 1.
    """
    if not isinstance(senha, str):
        raise TypeError("senha deve ser str")
    if tamanho_minimo < 1:
        raise ValueError("tamanho_minimo deve ser >= 1")

    problemas = []
    if len(senha) < tamanho_minimo:
        problemas.append("curta")
    if not any(c.isupper() for c in senha):
        problemas.append("sem_maiuscula")
    if not any(c.islower() for c in senha):
        problemas.append("sem_minuscula")
    if not any(c in "0123456789" for c in senha):
        problemas.append("sem_digito")
    if not any(c in ESPECIAIS for c in senha):
        problemas.append("sem_especial")
    if any(c.isspace() for c in senha):
        problemas.append("espaco")
    return problemas


def pontuar_senha(senha: str) -> int:
    """Pontuação de 0 a 100.

    - +2 por caractere, contando no máximo 20 caracteres (até 40 pontos);
    - +15 para cada categoria presente: maiúscula, minúscula, dígito, especial
      (mesmas definições de validar_senha);
    - -10 para cada trinca de caracteres iguais consecutivos, em janela
      deslizante ("aaa" conta 1 trinca, "aaaa" conta 2, "aaaaa" conta 3);
    - o resultado é limitado ao intervalo [0, 100].
    """
    pontos = min(len(senha), 20) * 2
    categorias = [
        any(c.isupper() for c in senha),
        any(c.islower() for c in senha),
        any(c in "0123456789" for c in senha),
        any(c in ESPECIAIS for c in senha),
    ]
    pontos += 15 * sum(categorias)
    trincas = sum(1 for i in range(len(senha) - 2) if senha[i] == senha[i + 1] == senha[i + 2])
    pontos -= 10 * trincas
    return max(0, min(100, pontos))


def classificar(senha: str) -> str:
    """Classifica a senha.

    - "invalida" se validar_senha(senha) contiver "espaco";
    - senão, pela pontuação: < 50 -> "fraca"; < 80 -> "media"; caso contrário "forte".
    """
    if "espaco" in validar_senha(senha):
        return "invalida"
    pontos = pontuar_senha(senha)
    if pontos < 50:
        return "fraca"
    if pontos < 80:
        return "media"
    return "forte"
