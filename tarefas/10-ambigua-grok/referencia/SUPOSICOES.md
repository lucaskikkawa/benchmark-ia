# Suposições da classificação

A especificação fecha só o tamanho, a marca URGENTE e a categoria da string vazia. O restante foi decidido assim:

- Categorias usadas, nesta ordem de prioridade: reclamacao, duvida, elogio, pedido, outro. A primeira que casar ganha. Não há categoria múltipla nem pontuação de confiança.
- A busca das palavras usa `casefold` no texto inteiro, então maiúsculas e o ß alemão não mudam a categoria. Acentos diferentes não são unificados: "ótimo" e "otimo" estão os dois na lista, de propósito. Isso não afeta URGENTE, que continua uma substring exata, com essas maiúsculas.
- Texto que não é vazio e não casa com nenhuma lista — espaços, pontuação sem "?", emoji, uma palavra desconhecida — cai em "outro". Espaços não são removidos antes do len nem antes de procurar URGENTE.
- O dict não ganha campos extras. Não há idioma nem nota de confiança, porque o enunciado não pede e um campo a mais complicaria o contrato sem teste que o exija.
- "dúvida" com acento cai em duvida pelo trecho "dúvid". Uma reclamação que também pede algo ("quero reclamar") fica em reclamacao, porque essa regra vem antes.
