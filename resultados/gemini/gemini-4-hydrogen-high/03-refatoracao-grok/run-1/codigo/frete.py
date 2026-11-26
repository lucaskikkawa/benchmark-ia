"""Cálculo de cotação de frete a partir de tabela configurável de faixas."""


def _validar_int(valor: object, nome: str) -> None:
    if type(valor) is not int:
        raise TypeError(nome)


def _validar_peso(peso_g: int) -> None:
    _validar_int(peso_g, "peso_g")
    if peso_g < 1 or peso_g > 30000:
        raise ValueError("peso fora da faixa")


def _buscar_faixa(
    faixas: tuple[tuple[str, int, int, int, int], ...],
    peso_g: int,
) -> tuple[str, int, int]:
    for nome, peso_min, peso_max, base_centavos, centavos_por_km in faixas:
        if peso_min <= peso_g <= peso_max:
            return nome, base_centavos, centavos_por_km
    raise ValueError("peso fora da faixa")


class TabelaFrete:
    """Tabela de faixas de peso e valores para cotação de frete."""

    FAIXAS: tuple[tuple[str, int, int, int, int], ...] = (
        ("carta", 1, 300, 800, 0),
        ("pac", 301, 2000, 1500, 2),
        ("sedex", 2001, 10000, 2500, 5),
        ("transportadora", 10001, 30000, 4000, 8),
    )

    def cotar(self, peso_g: int, distancia_km: int, expresso: bool) -> dict:
        """Mesmo contrato da função cotar."""
        _validar_int(peso_g, "peso_g")
        _validar_int(distancia_km, "distancia_km")
        if type(expresso) is not bool:
            raise TypeError("expresso")
        _validar_peso(peso_g)
        if distancia_km < 0 or distancia_km > 3000:
            raise ValueError("distancia fora da faixa")

        nome, base_centavos, centavos_por_km = _buscar_faixa(self.FAIXAS, peso_g)
        valor = base_centavos + centavos_por_km * distancia_km
        if expresso:
            valor = (valor * 3) // 2
        return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}


def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa. Mesmas regras de tipo e intervalo de cotar para o peso."""
    _validar_peso(peso_g)
    nome, _, _ = _buscar_faixa(TabelaFrete.FAIXAS, peso_g)
    return nome


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    """Calcula a cotação de frete usando a tabela corrente."""
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)
