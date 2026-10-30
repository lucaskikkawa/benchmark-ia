# Tarefa: escrever testes do módulo de cupons

O arquivo `descontos.py` já está no diretório de trabalho e está correto. **Não altere `descontos.py`.** Escreva a suíte em `tests/test_descontos.py` (pode haver outros `tests/test_*.py`). Os testes importam a função do módulo:

```python
from descontos import aplicar_desconto
```

A avaliação roda a sua suíte duas formas:

1. Contra este `descontos.py`. Tudo precisa passar.
2. Contra cópias com um bug cada. Para cada cópia, a suíte precisa **falhar**. Uma suíte que passa num módulo errado não serve. Uma suíte que falha no módulo correto também não.

Use `pytest` e apenas a biblioteca padrão. Não dependa de rede nem de arquivos fora de `tests/` e `descontos.py`.

## Contrato de `aplicar_desconto(preco_centavos, cupom, hoje) -> dict`

```python
{
    "preco_final": int,
    "desconto": int,          # preco_centavos - preco_final
    "cupom_aplicado": str | None,
}
```

O dict tem exatamente essas três chaves.

- `preco_centavos` é `int` ≥ 0. `bool` e `float` → `TypeError`. Negativo → `ValueError`.
- `cupom` é `None` ou `str`. Outro tipo → `TypeError`. Não há `strip`: `" OFF10"` e `"off10"` não são o código `"OFF10"`.
- `hoje` é `str` `YYYY-MM-DD` de um dia real no calendário gregoriano de `datetime.date` (anos 1 a 9999). `2000-02-29` e `0001-12-25` existem; `1900-02-29` e `2100-02-29` não. 29 de fevereiro só em ano bissexto, com a regra do século. Senão `ValueError`. Outro tipo → `TypeError`.
- `None` ou `""` não dão desconto: `cupom_aplicado` é `None` e o preço não muda. `" "` e `"\t"` não são vazio: são texto desconhecido e levantam `ValueError`.
- `"OFF10"`: preço final `(preco * 90) // 100` (não é `preco - preco // 10`). A regra foi aplicada mesmo se o piso zerar o desconto (preço 1 → final 0, desconto 1, cupom `"OFF10"`).
- `"OFF5"`: `(preco * 95) // 100`. Exemplo: 200 → 190; 101 → 95.
- `"FIXO500"`: tira 500 centavos, com piso 0. Preço 100 → final 0 e desconto 100, nunca negativo. Preço 0 continua 0 e o cupom conta como aplicado. `desconto` é sempre `preco_centavos - preco_final`, também no piso.
- `"BEMVINDO"`: 20% com a conta `(preco * 80) // 100` (não é `preco - (preco * 20) // 100`) somente se `hoje` está entre `2024-01-01` e `2024-12-31`, **inclusive**. Fora da janela o preço não muda e `cupom_aplicado` é `None` (não é erro).
- `"NATAL"`: 15% com a conta `(preco * 85) // 100` (não é `preco - (preco * 15) // 100`) somente em 24 ou 25 de dezembro, em qualquer ano de 1 a 9999. Preço 1 em 25/12 → final 0. Nos outros dias, igual ao BEMVINDO fora da janela.
- Qualquer outro texto → `ValueError`.

Exemplos que a suíte deve ser capaz de segurar sozinha: percentuais com piso, piso do valor fixo, os dois extremos de BEMVINDO, 24 e 25 de dezembro, cupom vazio, cupom desconhecido, preço negativo e data inválida.
