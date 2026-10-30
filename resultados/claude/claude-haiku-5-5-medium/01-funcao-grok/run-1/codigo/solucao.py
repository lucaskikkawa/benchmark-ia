DIGITOS = "0123456789"


def _para_minutos(horario: str) -> int:
    """Converte 'HH:MM' (ou '24:00') em minutos desde 00:00. Qualquer outro texto é ValueError."""
    if not isinstance(horario, str):
        raise TypeError(f"horário deve ser str, não {type(horario).__name__}")
    if len(horario) != 5 or horario[2] != ":":
        raise ValueError(f"horário inválido: {horario!r}")
    if any(c not in DIGITOS for c in horario[:2] + horario[3:]):
        raise ValueError(f"horário inválido: {horario!r}")
    horas = int(horario[:2])
    minutos = int(horario[3:])
    if minutos > 59:
        raise ValueError(f"minutos inválidos: {horario!r}")
    if horas == 24 and minutos == 0:
        return 1440
    if horas > 23:
        raise ValueError(f"horas inválidas: {horario!r}")
    return horas * 60 + minutos


def _para_texto(minutos: int) -> str:
    """Converte minutos em 'HH:MM'. 1440 vira '24:00'."""
    if minutos == 1440:
        return "24:00"
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    janela_ini = _para_minutos(inicio)
    janela_fim = _para_minutos(fim)
    if janela_ini >= janela_fim:
        raise ValueError("inicio deve ser estritamente anterior a fim")

    if not isinstance(ocupados, list):
        raise TypeError(f"ocupados deve ser list, não {type(ocupados).__name__}")

    intervalos = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError("cada ocupado deve ser um par (ini, fim)")
        ini = _para_minutos(item[0])
        fim_ocupado = _para_minutos(item[1])
        if ini > fim_ocupado:
            raise ValueError(f"intervalo ocupado invertido: {item!r}")
        if ini == fim_ocupado:
            continue
        # Recorte para a janela; o que ficar fora some.
        ini = max(ini, janela_ini)
        fim_ocupado = min(fim_ocupado, janela_fim)
        if ini < fim_ocupado:
            intervalos.append((ini, fim_ocupado))

    # Une sobreposições e encostados (depois do recorte).
    intervalos.sort()
    unidos = []
    for ini, fim_ocupado in intervalos:
        if unidos and ini <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fim_ocupado)
        else:
            unidos.append([ini, fim_ocupado])

    # Os trechos livres são os espaços entre os ocupados unidos dentro da janela.
    livres = []
    cursor = janela_ini
    for ini, fim_ocupado in unidos:
        if cursor < ini:
            livres.append((_para_texto(cursor), _para_texto(ini)))
        cursor = max(cursor, fim_ocupado)
    if cursor < janela_fim:
        livres.append((_para_texto(cursor), _para_texto(janela_fim)))
    return livres
