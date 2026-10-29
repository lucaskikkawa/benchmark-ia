# Suposições

Decisões tomadas onde o enunciado não especifica o comportamento.

1. **Tipo da entrada.** Se `texto` não for `str`, levanto `TypeError` (e não `ValueError`), pois é erro de
   programação, não de dado. Vale para as duas funções.
2. **Separadores.** Aceito apenas espaço/tab, `-`, `.`, `(` e `)`. Qualquer outro caractere (letras, `/`, `#`,
   "ramal") torna o texto inválido em `normalizar_telefone`. Ramais não são suportados.
3. **`+` só no início.** Um `+` fora do início é inválido. Com `+`, o código do país precisa ser `55`;
   números de outros países (`+1 ...`) geram `ValueError`, pois o formato pedido é brasileiro.
4. **`55` sem `+`.** Só é tratado como código do país quando o total tem 12 ou 13 dígitos; com 10 ou 11
   dígitos, `55` é o DDD do RS. Assim `55987654321` → `+5555987654321`.
5. **Prefixo `0` de longa distância.** Aceito um `0` antes do DDD (`0 11 98765-4321`, 11 ou 12 dígitos) e o
   descarto. Códigos de operadora (`0 15 11 ...`) não são suportados (ficam inválidos).
6. **Validação do DDD.** Rejeito DDDs com dígito `0` (`00`–`09`, `10`, `20`, ...), que não existem.
   Não verifico a lista oficial de DDDs ativos, para não depender de uma tabela que muda.
7. **Validação do número.** Celular: 9 dígitos começando com `9`. Fixo: 8 dígitos começando com `2`–`5`
   (faixas de fixos da Anatel). Celulares antigos de 8 dígitos (sem o 9) são inválidos: não adiciono o 9
   automaticamente porque isso poderia inventar um número errado.
8. **Números sem DDD.** Inválidos (o enunciado diz que o DDD é sempre informado).
9. **Números curtos/especiais** (`190`, `0800 ...`, `4004-xxxx`) são inválidos: não seguem o formato DDD+número.
10. **Extração em texto livre.** Um candidato é uma sequência que começa com `+`, `(` ou dígito, segue com dígitos
    e separadores e termina num dígito, sem estar colada a letras. Candidatos que não normalizam (datas,
    CPFs, valores) são ignorados silenciosamente em vez de levantar erro.
    Limitação conhecida: dois telefones separados apenas por espaço/hífen podem ser lidos como um só
    candidato e descartados; separe-os por vírgula, `/` ou palavra.
11. **Duplicatas.** Comparadas após a normalização (`(11) 98765-4321` e `+5511987654321` são o mesmo).
12. **Dígitos não ASCII** (ex.: dígitos arábicos) são rejeitados.
