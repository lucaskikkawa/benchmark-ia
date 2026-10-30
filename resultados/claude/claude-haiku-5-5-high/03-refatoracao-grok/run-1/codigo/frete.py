# cotador de frete — a tabela de faixas fica em TabelaFrete.FAIXAS e é lida a cada chamada.

PESO_MIN_G = 1
PESO_MAX_G = 30000
DISTANCIA_MAX_KM = 3000


def _checar_tipo(valor, nome: str) -> None:
    if type(valor) is not int:
        raise TypeError(nome)


def _checar_peso(peso_g: int) -> None:
    if peso_g < PESO_MIN_G or peso_g > PESO_MAX_G:
        raise ValueError("peso fora da faixa")


class TabelaFrete:
    # (nome, peso_min, peso_max, base_centavos, centavos_por_km); limites de peso inclusivos
    FAIXAS: tuple[tuple[str, int, int, int, int], ...] = (
        ("carta", 1, 300, 800, 0),
        ("pac", 301, 2000, 1500, 2),
        ("sedex", 2001, 10000, 2500, 5),
        ("transportadora", 10001, 30000, 4000, 8),
    )

    def cotar(self, peso_g: int, distancia_km: int, expresso: bool) -> dict:
        """Mesmo contrato da função cotar."""
        _checar_tipo(peso_g, "peso_g")
        _checar_tipo(distancia_km, "distancia_km")
        if type(expresso) is not bool:
            raise TypeError("expresso")
        _checar_peso(peso_g)
        if distancia_km < 0 or distancia_km > DISTANCIA_MAX_KM:
            raise ValueError("distancia fora da faixa")

        nome, _, _, base, por_km = self._faixa(peso_g)
        valor = base + por_km * distancia_km
        if expresso:
            valor = (valor * 3) // 2
        return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}

    def _faixa(self, peso_g: int) -> tuple[str, int, int, int, int]:
        for faixa in TabelaFrete.FAIXAS:
            if faixa[1] <= peso_g <= faixa[2]:
                return faixa
        raise ValueError("peso fora da faixa")


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)


def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa. Mesmas regras de tipo e intervalo de cotar para o peso."""
    _checar_tipo(peso_g, "peso_g")
    _checar_peso(peso_g)
    return TabelaFrete()._faixa(peso_g)[0]
