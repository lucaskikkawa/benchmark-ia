def _obter_faixa(peso_g: int) -> tuple[str, int, int, int, int]:
    if type(peso_g) is not int:
        raise TypeError("peso_g")
    if peso_g <= 0 or peso_g > 30000:
        raise ValueError("peso fora da faixa")
    for faixa in TabelaFrete.FAIXAS:
        nome, peso_min, peso_max, base_centavos, centavos_por_km = faixa
        if peso_min <= peso_g <= peso_max:
            return faixa
    raise ValueError("peso fora da faixa")


class TabelaFrete:
    FAIXAS: tuple[tuple[str, int, int, int, int], ...] = (
        ("carta", 1, 300, 800, 0),
        ("pac", 301, 2000, 1500, 2),
        ("sedex", 2001, 10000, 2500, 5),
        ("transportadora", 10001, 30000, 4000, 8),
    )

    def cotar(self, peso_g: int, distancia_km: int, expresso: bool) -> dict:
        """Mesmo contrato da função cotar."""
        if type(peso_g) is not int:
            raise TypeError("peso_g")
        if type(distancia_km) is not int:
            raise TypeError("distancia_km")
        if type(expresso) is not bool:
            raise TypeError("expresso")
        if peso_g <= 0 or peso_g > 30000:
            raise ValueError("peso fora da faixa")
        if distancia_km < 0 or distancia_km > 3000:
            raise ValueError("distancia fora da faixa")

        nome, _, _, base_centavos, centavos_por_km = _obter_faixa(peso_g)
        valor = base_centavos + centavos_por_km * distancia_km
        if expresso is True:
            valor = (valor * 3) // 2
        return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}


def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa. Mesmas regras de tipo e intervalo de cotar para o peso."""
    nome, _, _, _, _ = _obter_faixa(peso_g)
    return nome


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)

