# cotador de frete: a tabela de faixas fica em TabelaFrete.FAIXAS e é lida a cada chamada.


def _checar_tipo_peso(peso_g):
    if type(peso_g) is not int:
        raise TypeError("peso_g")


def _checar_tipo_distancia(distancia_km):
    if type(distancia_km) is not int:
        raise TypeError("distancia_km")


def _checar_tipo_expresso(expresso):
    if type(expresso) is not bool:
        raise TypeError("expresso")


def _checar_peso(peso_g):
    if peso_g <= 0 or peso_g > 30000:
        raise ValueError("peso fora da faixa")


def _checar_distancia(distancia_km):
    if distancia_km < 0 or distancia_km > 3000:
        raise ValueError("distancia fora da faixa")


class TabelaFrete:
    # (nome, peso_min, peso_max, base_centavos, centavos_por_km); limites de peso inclusivos
    FAIXAS = (
        ("carta", 1, 300, 800, 0),
        ("pac", 301, 2000, 1500, 2),
        ("sedex", 2001, 10000, 2500, 5),
        ("transportadora", 10001, 30000, 4000, 8),
    )

    def cotar(self, peso_g, distancia_km, expresso):
        _checar_tipo_peso(peso_g)
        _checar_tipo_distancia(distancia_km)
        _checar_tipo_expresso(expresso)
        _checar_peso(peso_g)
        _checar_distancia(distancia_km)

        for nome, peso_min, peso_max, base, por_km in TabelaFrete.FAIXAS:
            if peso_min <= peso_g <= peso_max:
                valor = base + por_km * distancia_km
                if expresso:
                    valor = (valor * 3) // 2
                return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}
        raise ValueError("peso fora da faixa")


def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    return TabelaFrete().cotar(peso_g, distancia_km, expresso)


def faixa_de_peso(peso_g: int) -> str:
    _checar_tipo_peso(peso_g)
    _checar_peso(peso_g)

    for nome, peso_min, peso_max, _base, _por_km in TabelaFrete.FAIXAS:
        if peso_min <= peso_g <= peso_max:
            return nome
    raise ValueError("peso fora da faixa")
