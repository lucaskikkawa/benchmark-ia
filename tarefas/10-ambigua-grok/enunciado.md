# Tarefa: classificar uma mensagem curta

Crie dois arquivos no diretório de trabalho:

- `solucao.py` com `classificar_mensagem(texto: str) -> dict`
- `SUPOSICOES.md` em UTF-8, com as decisões que você tomar nos pontos abertos

Só a biblioteca padrão. A função é pura: o mesmo texto sempre devolve o mesmo dict, sem ler arquivo, relógio ou rede.

## O que está fechado

O dict tem **pelo menos** estas chaves (pode ter outras):

```python
{
    "categoria": str,
    "urgente": bool,
    "tamanho": int,
}
```

- `tamanho` é `len(texto)`, em caracteres Unicode, **sem** `strip` e sem contar largura de tela. `"ação"` tem tamanho 4. `"🙂"` tem tamanho 1. Quebra de linha conta.
- `urgente` é `True` exatamente quando a substring `"URGENTE"` aparece em `texto` (maiúsculas, sem exigir palavra inteira). `"urgente"`, `"Urgente"` e `"URGEN" ` são `False`. `"XURGENTEY"` e `" URGENTE"` são `True`.
- `texto == ""` (string vazia, e só ela) devolve `categoria == "vazia"`, `urgente is False` e `tamanho == 0`.
- Qualquer outro texto, inclusive só espaços, tem `categoria` string não vazia e **diferente** de `"vazia"`.
- Se `texto` não for `str` (`None`, `bytes`, `int`), levante `TypeError`.

Os testes automáticos cobrem só este núcleo.

## O que fica em aberto

Você escolhe e **registra em `SUPOSICOES.md`** (pelo menos duas linhas não vazias; o texto todo, sem contar espaços das pontas, com 80 caracteres ou mais):

- Quais categorias existem além de `"vazia"` (por exemplo reclamação, dúvida, elogio, pedido, outro — a lista não é obrigatória).
- Quais palavras ou sinais disparam cada categoria, e o que acontece quando o texto casa com mais de uma.
- Se a classificação ignora maiúsculas e acentos. Isso **não** muda a regra de `"URGENTE"`, que continua sensível a maiúsculas.
- Como classificar texto que não é vazio mas não tem palavra (espaços, pontuação). Lembre que ele não pode usar a categoria `"vazia"`.
- Se o dict leva campos extras (idioma, confiança, etc.).

Não há resposta única. O arquivo existe para outro avaliador entender o que você assumiu. Os testes não comparam o texto das suposições com um gabarito.
