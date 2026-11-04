# cotador de frete — a tabela vive em TabelaFrete.FAIXAS e é lida a cada chamada.

PESO_MIN_G = 1
PESO_MAX_G = 30000
DISTANCIA_MIN_KM = 0
DISTANCIA_MAX_KM = 3000


def _validar_peso(peso_g):
    if type(peso_g) is not int:
        raise TypeError("peso_g")


def _validar_faixa_peso(peso_g):
    if peso_g < PESO_MIN_G or peso_g > PESO_MAX_G:
        raise ValueError("peso fora da faixa")


def _validar_entrada(peso_g, distancia_km, expresso):
    # mesma ordem do cotador antigo: tipos primeiro, depois intervalos
    _validar_peso(peso_g)
    if type(distancia_km) is not int:
        raise TypeError("distancia_km")
    if type(expresso) is not bool:
        raise TypeError("expresso")
    _validar_faixa_peso(peso_g)
    if distancia_km < DISTANCIA_MIN_KM or distancia_km > DISTANCIA_MAX_KM:
        raise ValueError("distancia fora da faixa")


def _buscar_faixa(faixas, peso_g):
    for faixa in faixas:
        _, peso_min, peso_max, _, _ = faixa
        if peso_min <= peso_g <= peso_max:
            return faixa
    raise ValueError("peso fora da faixa")


class TabelaFrete:
    # (nome, peso_min, peso_max, base_centavos, centavos_por_km) — limites inclusivos
    FAIXAS = (
        ("carta", 1, 300, 800, 0),
        ("pac", 301, 2000, 1500, 2),
        ("sedex", 2001, 10000, 2500, 5),
        ("transportadora", 10001, 30000, 4000, 8),
    )

    def cotar(self, peso_g: int, distancia_km: int, expresso: bool) -> dict:
        """Mesmo contrato da função cotar."""
        _validar_entrada(peso_g, distancia_km, expresso)
        nome, _, _, base, por_km = _buscar_faixa(TabelaFrete.FAIXAS, peso_g)
        valor = base + por_km * distancia_km
        if expresso:
            valor = (valor * 3) // 2
        return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}


def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa. Mesmas regras de tipo e intervalo de cotar para o peso."""
    _validar_peso(peso_g)
    _validar_faixa_peso(peso_g)
    return _buscar_faixa(TabelaFrete.FAIXAS, peso_g)[0]


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)
