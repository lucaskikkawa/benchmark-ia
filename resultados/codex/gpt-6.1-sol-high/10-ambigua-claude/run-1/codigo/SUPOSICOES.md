# Decisões sobre casos não especificados

1. **Dúvida: quais caracteres representam dígitos?**
   Decisão: somente `0` a `9` ASCII são aceitos. Algarismos Unicode, como `１`
   ou `١`, invalidam o candidato inteiro. Motivo: manter a saída E.164 em ASCII
   sem converter caracteres não previstos ou extrair parte de uma sequência.

2. **Dúvida: quais espaços são separadores?**
   Decisão: `normalizar_telefone` aceita todos os caracteres reconhecidos por
   `str.isspace()`, inclusive tabulações e quebras de linha. Na extração,
   quebras reconhecidas por `str.splitlines()` delimitam candidatos; os demais
   espaços podem separar dígitos dentro de um telefone. Motivo: aceitar espaços
   de textos colados e respeitar a quebra de linha como separador de telefones.

3. **Dúvida: parênteses e separadores precisam seguir uma disposição exata?**
   Decisão: pontos, hífens, parênteses e espaços são descartados independentemente
   de posição, repetição ou balanceamento. Assim, parênteses incompletos e
   pontuação antes/depois do número são aceitos. Motivo: o enunciado permite
   separadores repetidos e combinados, sem exigir uma gramática de formatação.
   Outros caracteres, como `/`, `,`, `:`, letras ou travessões, são inválidos
   dentro da entrada de `normalizar_telefone`.

4. **Dúvida: como interpretar `+`, prefixos e o DDD `55`?**
   Decisão: depois de remover separadores, pode haver um único `+`, antes de
   todos os dígitos, e ele exige o código de país `55`. Sem `+`, entradas com
   10/11 dígitos são nacionais e entradas com 12/13 precisam começar com `55`.
   Motivo: preservar telefones nacionais com DDD `55`. Prefixos `00`, zero de
   operadora, outros países e ramais não são convertidos nem removidos.

5. **Dúvida: validar o DDD por uma tabela de localidades?**
   Decisão: aceitar qualquer par de dígitos de `1` a `9`, inclusive pares não
   atribuídos a localidades. Motivo: essa é a regra explícita do enunciado;
   não foi solicitada consulta a uma tabela externa.

6. **Dúvida: onde termina um candidato no texto livre?**
   Decisão: cada trecho máximo de dígitos, `+` e separadores aceitos dentro de
   uma linha é um candidato indivisível. Vírgulas, ponto e vírgula, barras,
   quebras de linha, palavras e outros caracteres fora desse conjunto delimitam
   candidatos. Separadores nas extremidades não interferem na validação.
   Motivo: impedir que um telefone seja recortado de um trecho numérico maior,
   mesmo quando esse trecho usa formatação.

7. **Dúvida: como separar dois telefones unidos apenas por espaços, pontos,
   hífens ou parênteses?**
   Decisão: não tentar dividi-los; o trecho inteiro é validado e, se inválido,
   ignorado. O mesmo vale para um telefone seguido de um código numérico
   separado apenas por espaços. Por exemplo, `11987654321 2134567890` não
   produz resultados; `11987654321 / 2134567890` produz dois. Motivo: esses
   caracteres também são separadores internos válidos e não permitem distinguir
   com segurança a intenção de separar telefones.

8. **Dúvida: aceitar dígitos colados a letras ou sublinhados?**
   Decisão: ignorar candidatos cujo primeiro ou último caractere significativo
   (`+` ou dígito) esteja diretamente colado a uma letra, algarismo ou `_` fora
   do candidato. Por exemplo, `id11987654321` é ignorado e
   `tel:11987654321` é aceito. Motivo: evitar extrair números embutidos em
   identificadores. Letras e algarismos Unicode também contam nessa verificação.

9. **Dúvida: e se um CPF, valor, data ou código tiver exatamente a sintaxe
   e os dígitos de um telefone válido?**
   Decisão: aceitar o candidato quando ele passa pelas regras sintáticas, sem
   inferir seu significado pelo contexto. Por exemplo, `119.876.543-21` tem
   os mesmos dígitos de um celular válido. Uma vírgula sempre delimita candidatos,
   inclusive em valores decimais. Motivo: a formatação permitida se sobrepõe
   à de outros dados; não existe uma regra contextual no enunciado que resolva
   essa ambiguidade. Trechos que falham na validação são simplesmente ignorados.

10. **Dúvida: como tratar entradas vazias, valores de outro tipo e duplicatas?**
    Decisão: entrada vazia ou só com separadores gera `ValueError` na
    normalização e `[]` na extração. Valores que não são `str` geram `ValueError`
    em ambas as funções. Duplicatas são comparadas pelo telefone já normalizado,
    preservando a primeira ocorrência. Motivo: manter os erros de entrada
    previsíveis e deduplicar representações diferentes do mesmo telefone.
