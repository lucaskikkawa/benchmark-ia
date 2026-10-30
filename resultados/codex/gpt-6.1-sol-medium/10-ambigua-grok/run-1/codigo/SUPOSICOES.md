# Decisões de classificação

- As categorias são `vazia`, `pergunta` e `outro`.
- Apenas a string exatamente vazia recebe `vazia`, com prioridade sobre as demais regras.
- Qualquer texto contendo o sinal ASCII `?` recebe `pergunta`, independentemente de palavras ou da posição do sinal. Sinais semelhantes, como `？`, não disparam essa regra.
- Todo texto não vazio sem `?` recebe `outro`. Isso inclui espaços, quebras de linha, pontuação isolada, caracteres invisíveis e a palavra literal `vazia`.
- Nenhuma palavra dispara categorias. Maiúsculas e acentos não influenciam a categoria, pois a única busca é pelo sinal `?`; não se aplica normalização, remoção de acentos, `strip` ou conversão de caixa.
- A urgência é independente da categoria: somente a substring literal `URGENTE` ativa o campo `urgente`, respeitando maiúsculas e os caracteres originais.
- O tamanho é calculado diretamente com `len(texto)`, incluindo caracteres combinantes e substitutos Unicode isolados, sem codificação em bytes.
- O dict contém somente `categoria`, `urgente` e `tamanho`, sem campos extras. Instâncias de `str`, inclusive subclasses, são aceitas; outros tipos levantam `TypeError`.
