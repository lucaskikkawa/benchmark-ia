# Código legado funcional, mas macarrônico, sem classes e difícil de manter.

def processar_pedidos(pedidos: list[dict]) -> list[dict]:
    out = []
    for p in pedidos:
        pid = p["id"]
        c = p["cliente"]
        cat = str(p.get("categoria_cliente", "bronze")).lower()
        items = p.get("itens", [])
        tf = str(p.get("tipo_frete", "padrao")).lower()

        # calcula subtotal e peso total (assume peso 0.5kg por item se não fornecido)
        sub = 0.0
        peso_total = 0.0
        for it in items:
            pr = float(it["preco"])
            q = int(it.get("quantidade", 1))
            sub += pr * q
            peso_total += float(it.get("peso_kg", 0.5)) * q
        sub = round(sub, 2)

        # calcula desconto
        desc = 0.0
        if cat == "bronze":
            desc = 0.0
        elif cat == "prata":
            if sub >= 100.0:
                desc = 0.05 * sub
            else:
                desc = 0.0
        elif cat == "ouro":
            if sub >= 50.0:
                desc = 0.10 * sub
            else:
                desc = 0.05 * sub
        elif cat == "vip":
            desc = 0.15 * sub
        else:
            desc = 0.0
        desc = round(desc, 2)

        # calcula frete
        if sub >= 200.0:
            fr = 0.0
        else:
            if tf == "padrao":
                fr = 10.0 + peso_total * 1.5
            elif tf == "expresso":
                fr = 25.0 + peso_total * 3.0
            elif tf == "economico":
                fr = 5.0 + peso_total * 0.8
            else:
                raise ValueError(f"Tipo de frete desconhecido: {tf}")
        fr = round(fr, 2)

        tot = round(sub - desc + fr, 2)
        out.append({
            "id": pid,
            "cliente": c,
            "subtotal": sub,
            "desconto": desc,
            "frete": fr,
            "total": tot
        })
    return out
