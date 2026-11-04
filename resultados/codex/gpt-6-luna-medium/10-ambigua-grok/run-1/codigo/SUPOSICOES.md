# Suposições da classificação

A categoria `vazia` é reservada exclusivamente à string vazia. Mensagens não vazias
são verificadas, nesta ordem de prioridade, como reclamação, dúvida, elogio e pedido;
se não houver correspondência, recebem a categoria `outro`.

A busca de termos da categoria ignora maiúsculas e minúsculas usando `lower()`, mas
preserva acentos; não há normalização Unicode. Os termos são procurados como
substrings, e o sinal `?` também caracteriza uma dúvida. Espaços, pontuação sem `?`
e outros conteúdos sem correspondência ficam em `outro`.

O campo `urgente` é independente da categoria e só é verdadeiro para a substring
literal `URGENTE`, respeitando maiúsculas. O dicionário contém apenas categoria,
urgente e tamanho; tamanho usa diretamente `len()` da string original.
