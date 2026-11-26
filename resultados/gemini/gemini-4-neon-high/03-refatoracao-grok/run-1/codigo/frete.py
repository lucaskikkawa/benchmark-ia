PESO_MIN_G = 1
PESO_MAX_G = 30000
DISTANCIA_MIN_KM = 0
DISTANCIA_MAX_KM = 3000


def _buscar_faixa(
    faixas: tuple[tuple[str, int, int, int, int], ...],
    peso_g: int,
) -> tuple[str, int, int, int, int]:
    for faixa in faixas:
        _, peso_min, peso_max, _, _ = faixa
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
        """Calcula a cotação de frete usando a tabela corrente."""
        if type(peso_g) is not int:
            raise TypeError("peso_g")
        if type(distancia_km) is not int:
            raise TypeError("distancia_km")
        if type(expresso) is not bool:
            raise TypeError("expresso")
        if peso_g < PESO_MIN_G or peso_g > PESO_MAX_G:
            raise ValueError("peso fora da faixa")
        if distancia_km < DISTANCIA_MIN_KM or distancia_km > DISTANCIA_MAX_KM:
            raise ValueError("distancia fora da faixa")

        nome, _, _, base_centavos, centavos_por_km = _buscar_faixa(self.FAIXAS, peso_g)
        valor = base_centavos + centavos_por_km * distancia_km
        if expresso:
            valor = (valor * 3) // 2
        return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}


def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa. Mesmas regras de tipo e intervalo de cotar para o peso."""
    if type(peso_g) is not int:
        raise TypeError("peso_g")
    if peso_g < PESO_MIN_G or peso_g > PESO_MAX_G:
        raise ValueError("peso fora da faixa")

    nome, _, _, _, _ = _buscar_faixa(TabelaFrete.FAIXAS, peso_g)
    return nome


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)
