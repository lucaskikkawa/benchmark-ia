class TabelaFrete:
    FAIXAS: tuple[tuple[str, int, int, int, int], ...] = (
        ("carta", 1, 300, 800, 0),
        ("pac", 301, 2000, 1500, 2),
        ("sedex", 2001, 10000, 2500, 5),
        ("transportadora", 10001, 30000, 4000, 8),
    )

    def cotar(self, peso_g: int, distancia_km: int, expresso: bool) -> dict:
        """Calcula o frete usando a tabela de faixas atual."""
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

        for nome, peso_min, peso_max, base_centavos, centavos_por_km in TabelaFrete.FAIXAS:
            if peso_min <= peso_g <= peso_max:
                valor = base_centavos + centavos_por_km * distancia_km
                if expresso:
                    valor = (valor * 3) // 2
                return {
                    "faixa": nome,
                    "valor_centavos": valor,
                    "expresso": expresso,
                }

        raise ValueError("peso fora da faixa")


def _validar_peso(peso_g: int) -> None:
    if type(peso_g) is not int:
        raise TypeError("peso_g")
    if peso_g <= 0 or peso_g > 30000:
        raise ValueError("peso fora da faixa")


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    """Calcula o frete com a tabela de faixas padrão."""
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)


def faixa_de_peso(peso_g: int) -> str:
    """Devolve o nome da faixa correspondente ao peso."""
    _validar_peso(peso_g)
    for nome, peso_min, peso_max, _base_centavos, _centavos_por_km in TabelaFrete.FAIXAS:
        if peso_min <= peso_g <= peso_max:
            return nome
    raise ValueError("peso fora da faixa")
