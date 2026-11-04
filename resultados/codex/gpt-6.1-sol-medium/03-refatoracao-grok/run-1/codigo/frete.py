"""Cotação de frete baseada em uma tabela compartilhada de faixas de peso."""


def _validar_peso(peso_g: int) -> None:
    if type(peso_g) is not int:
        raise TypeError("peso_g")
    if peso_g <= 0 or peso_g > 30000:
        raise ValueError("peso fora da faixa")


def _buscar_faixa(peso_g: int) -> tuple[str, int, int, int, int]:
    for faixa in TabelaFrete.FAIXAS:
        if faixa[1] <= peso_g <= faixa[2]:
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
        """Calcula o frete usando a tabela corrente e valores em centavos."""
        if type(peso_g) is not int:
            raise TypeError("peso_g")
        if type(distancia_km) is not int:
            raise TypeError("distancia_km")
        if type(expresso) is not bool:
            raise TypeError("expresso")
        _validar_peso(peso_g)
        if distancia_km < 0 or distancia_km > 3000:
            raise ValueError("distancia fora da faixa")

        nome, _, _, base, por_km = _buscar_faixa(peso_g)
        valor = base + por_km * distancia_km
        if expresso:
            valor = (valor * 3) // 2
        return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    """Calcula o frete com o mesmo contrato de TabelaFrete.cotar."""
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)


def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa, com as mesmas regras de tipo e intervalo de peso."""
    _validar_peso(peso_g)
    return _buscar_faixa(peso_g)[0]
