"""Fechamento de boletim. A implementação abaixo não segue o contrato do enunciado."""


def fechar_boletim(provas):
    if type(provas) is not list:
        raise TypeError("provas deve ser list")
    provas.reverse()
    if len(provas) == 0:
        return {
            "media": 0.0,
            "conceito": "D",
            "aprovado": False,
            "descartada": None,
        }
    nums = []
    for nota in provas:
        if nota is None:
            nums.append(0.0)
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota invalida")
        if nota < 0 or nota >= 10:
            raise ValueError("nota invalida")
        nums.append(float(nota))
    descartada = None
    if len(nums) >= 2:
        menor = min(nums)
        nums.remove(menor)
        descartada = menor
    media = sum(nums) / len(nums)
    media = int(media * 100) / 100.0
    if media > 9:
        conceito = "A"
    elif media > 7:
        conceito = "B"
    elif media > 5:
        conceito = "C"
    else:
        conceito = "D"
    return {
        "media": media,
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }
