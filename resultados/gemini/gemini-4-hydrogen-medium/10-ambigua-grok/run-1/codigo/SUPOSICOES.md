# Suposições da solução

- **Categorias existentes**: além de `"vazia"` (exclusiva para `""`), a função usa `"reclamacao"`, `"pedido"`, `"duvida"`, `"elogio"`, `"sem_palavras"` e `"outro"`.
- **Sinais e desempate**: a detecção usa palavras-chave inteiras (fronteira de palavra) e o sinal `"?"` para `"duvida"`. Quando há mais de uma correspondência, vale a ordem de prioridade: `reclamacao` > `pedido` > `duvida` > `elogio` > `outro`.
- **Maiúsculas e acentos**: apenas a escolha da `categoria` ignora maiúsculas/minúsculas (via `casefold`) e acentos (decomposição `NFD` removendo marcas `Mn`). A detecção de `urgente` continua estritamente sensível a maiúsculas e exata para a substring `"URGENTE"` no texto original.
- **Texto não vazio sem palavras**: textos compostos apenas por espaços, quebras de linha, caracteres invisíveis ou pontuação (sem caracteres alfanuméricos após normalização) recebem a categoria `"sem_palavras"`, nunca `"vazia"`.
- **Campos do dicionário**: o retorno contém apenas as três chaves obrigatórias (`"categoria"`, `"urgente"` e `"tamanho"`), sem campos extras.
