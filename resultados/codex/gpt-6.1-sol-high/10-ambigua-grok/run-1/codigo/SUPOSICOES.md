# Decisões de classificação

- As categorias são `vazia`, `reclamacao`, `duvida`, `pedido`, `elogio` e `outro`. Somente a string exatamente vazia recebe `vazia`.
- Para escolher a categoria, aplica-se `casefold`, decomposição Unicode NFD e remoção dos caracteres de categoria Unicode `Mn` (marcas não espaçadoras). Assim, maiúsculas e acentos usuais não distinguem palavras-chave. Essa transformação ocorre apenas numa cópia usada para classificar.
- Uma palavra é uma sequência máxima reconhecida pela expressão regular Unicode `[^\W\d_]+`: caracteres de palavra, exceto dígitos decimais e sublinhado. As palavras-chave precisam coincidir com uma dessas sequências inteiras; não basta aparecerem dentro de outra palavra.
- `reclamacao`: palavras `ruim`, `pessimo`, `problema`, `defeito` ou `reclamacao`.
- `duvida`: presença literal do sinal ASCII `?`, ou palavras `duvida`, `como`, `qual`, `quando`, `onde` ou `porque`.
- `pedido`: palavras `preciso`, `solicito`, `gostaria` ou `ajuda`.
- `elogio`: palavras `obrigado`, `obrigada`, `otimo`, `excelente` ou `parabens`.
- Havendo múltiplas correspondências, a prioridade é `reclamacao`, depois `duvida`, depois `pedido`, depois `elogio`. Não há inferência de contexto, negação ou ironia.
- Qualquer texto não vazio sem correspondência recebe `outro`, inclusive espaços, quebras de linha, pontuação sem `?`, caracteres invisíveis e a palavra `vazia`. Pontuação que contenha `?` recebe `duvida`.
- O resultado tem exatamente os três campos solicitados, sem campos extras. `tamanho` é sempre `len(texto)` original e `urgente` é sempre o resultado de `"URGENTE" in texto`, sem nenhuma transformação ou limite de busca.
- São aceitas instâncias de `str`, inclusive subclasses; qualquer outro tipo levanta `TypeError`. Não se faz codificação em bytes, leitura de arquivos, consulta de relógio ou acesso à rede.
