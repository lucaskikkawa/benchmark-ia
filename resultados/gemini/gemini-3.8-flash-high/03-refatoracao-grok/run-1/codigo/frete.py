# cotador antigo — planilha copiada em cada ramo. funciona, mas ninguém quer mexer.

def cotar(peso_g, distancia_km, expresso):
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

    # carta / pac / sedex / transportadora — números repetidos de propósito
    if peso_g >= 1 and peso_g <= 300:
        nome = "carta"
        base = 800
        por_km = 0
        total = base + por_km * distancia_km
        if expresso is True:
            total = (total * 3) // 2
        return {"faixa": nome, "valor_centavos": total, "expresso": expresso}
    if peso_g >= 301 and peso_g <= 2000:
        nome = "pac"
        base = 1500
        por_km = 2
        total = base + por_km * distancia_km
        if expresso is True:
            total = (total * 3) // 2
        return {"faixa": nome, "valor_centavos": total, "expresso": expresso}
    if peso_g >= 2001 and peso_g <= 10000:
        nome = "sedex"
        base = 2500
        por_km = 5
        total = base + por_km * distancia_km
        if expresso is True:
            total = (total * 3) // 2
        return {"faixa": nome, "valor_centavos": total, "expresso": expresso}
    if peso_g >= 10001 and peso_g <= 30000:
        nome = "transportadora"
        base = 4000
        por_km = 8
        total = base + por_km * distancia_km
        if expresso is True:
            total = (total * 3) // 2
        return {"faixa": nome, "valor_centavos": total, "expresso": expresso}
    raise ValueError("peso fora da faixa")
