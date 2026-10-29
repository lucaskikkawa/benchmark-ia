"""Cotação de frete a partir de uma tabela única."""

_PESO_MIN = 1
_PESO_MAX = 30000
_DIST_MAX = 3000


class TabelaFrete:
    """Tabela de faixas de peso. O construtor não recebe argumentos."""

    FAIXAS = (
        ("carta", 1, 300, 800, 0),
        ("pac", 301, 2000, 1500, 2),
        ("sedex", 2001, 10000, 2500, 5),
        ("transportadora", 10001, 30000, 4000, 8),
    )

    def cotar(self, peso_g: int, distancia_km: int, expresso: bool) -> dict:
        """Mesmo contrato da função cotar."""
        _validar_distancia(distancia_km)
        _validar_expresso(expresso)
        nome, base, por_km = _componentes(peso_g)
        valor = base + por_km * distancia_km
        if expresso:
            valor = (valor * 3) // 2
        return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}


def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa para o peso, com as mesmas validações de peso de cotar."""
    return _componentes(peso_g)[0]


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    """Calcula o frete em centavos.

    peso_g em 1..30000, distancia_km em 0..3000, expresso bool.
    bool não é aceito como inteiro. Expresso multiplica por 3 // 2.
    """
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)


def _componentes(peso_g: int) -> tuple[str, int, int]:
    _validar_peso(peso_g)
    for nome, minimo, maximo, base, por_km in TabelaFrete.FAIXAS:
        if minimo <= peso_g <= maximo:
            return nome, base, por_km
    raise ValueError("peso fora da faixa")


def _validar_peso(peso_g: int) -> None:
    if isinstance(peso_g, bool) or not isinstance(peso_g, int):
        raise TypeError("peso_g")
    if peso_g < _PESO_MIN or peso_g > _PESO_MAX:
        raise ValueError("peso fora da faixa")


def _validar_distancia(distancia_km: int) -> None:
    if isinstance(distancia_km, bool) or not isinstance(distancia_km, int):
        raise TypeError("distancia_km")
    if distancia_km < 0 or distancia_km > _DIST_MAX:
        raise ValueError("distancia fora da faixa")


def _validar_expresso(expresso: bool) -> None:
    if not isinstance(expresso, bool):
        raise TypeError("expresso")
