# Suposições e decisões de projeto

Este documento registra as decisões tomadas para casos não especificados em `enunciado.md`.

## 1. Tipos de entrada inválidos (`None`, números, etc.) e string vazia
- **Dúvida:** O que fazer se `normalizar_telefone` ou `extrair_telefones` receber um valor que não seja `str` (como `None` ou `int`), ou se `normalizar_telefone` receber string vazia/apenas espaços.
- **Decisão:** Levantar `ValueError` em ambos os casos (e retornar `[]` em `extrair_telefones("")`).
- **Motivo:** O enunciado pede explicitamente para levantar `ValueError` quando não for possível interpretar o texto como telefone. Padronizar em `ValueError` simplifica o tratamento de erros por quem consome dados sujos de CRM.

## 2. Uso do sinal `+` e código do país `55`
- **Dúvida:** Onde o `+` é aceito e como tratar números com `+` mas sem o código `55` (ex.: `+11 98765-4321`) ou com `55` em formato `(+55)`.
- **Decisão:** O `+` só é aceito no início da string (ou dentro de parênteses iniciais, como `(+55)`), nunca no meio ou no fim, e exige obrigatoriamente o código `55` seguido de 10 ou 11 dígitos nacionais (total de 12 ou 13 dígitos). Assim, `+11 98765-4321` e `+55 98765-4321` (11 dígitos) levantam `ValueError`.
- **Motivo:** No padrão E.164, `+` introduz o código do país. Aceitar `+` sem `55` ou com 11 dígitos interpretando `55` como DDD violaria a semântica do `+` e causaria falsos positivos.

## 3. Zero antes do DDD e códigos de operadora (`011`, `015 11`, `0055`)
- **Dúvida:** Aceitar ou rejeitar prefixo `0` de longa distância (ex.: `(011) 98765-4321`), código de operadora (`015 11 98765-4321`) ou `0055`.
- **Decisão:** Rejeitar (levantar `ValueError` em `normalizar_telefone` e ignorar em `extrair_telefones`).
- **Motivo:** O enunciado define que apenas o código do país `55` (com ou sem `+`) é opcional, que o DDD tem 2 dígitos sem `0`, e que nunca se deve cortar dígitos.

## 4. Parênteses e caracteres permitidos em `normalizar_telefone`
- **Dúvida:** Como lidar com parênteses desbalanceados (ex.: `(11 98765-4321`), vazios (`()`), aninhados, ou caracteres fora do conjunto especificado (ex.: letras, `/`, `,`, `;`).
- **Decisão:** Aceitar apenas dígitos, `+`, `-`, `.`, `(`, `)` e espaços em branco (`\s`). Parênteses devem estar balanceados, não aninhados e conter ao menos um dígito. Qualquer outro caractere ou parêntese malformado levanta `ValueError`.
- **Motivo:** `normalizar_telefone` recebe um único telefone; aceitar letras ou pontuação arbitrária mascararia textos inválidos. Exigir parênteses balanceados evita aceitar strings corrompidas mantendo flexibilidade para `( 11 )  98765 - 4321` e `(+55) (11) ...`.

## 5. Segundo dígito de celulares e validação de DDDs pela ANATEL
- **Dúvida:** Restringir o segundo dígito de celulares (ex.: impedir `90...`) ou filtrar DDDs que não estão atribuídos pela ANATEL (como `23`, `25`, `26`).
- **Decisão:** Seguir estritamente a regra do enunciado: DDD válido é qualquer par de dígitos de `1` a `9` (sem `0`), e celular válido é qualquer número de 9 dígitos iniciado por `9`.
- **Motivo:** Evita divergir da especificação explícita do time ("`11` a `99`, exceto `20`, `30`, ..., `90`"; "celulares têm 9 dígitos e começam com `9`").

## 6. Quebras de linha dentro de um número em `extrair_telefones`
- **Dúvida:** Espaços horizontais podem separar partes de um telefone, mas e quebras de linha (`\n`)?
- **Decisão:** Em `extrair_telefones`, quebras de linha sempre encerram um candidato a telefone (não são aceitas como separador interno do número).
- **Motivo:** O enunciado lista quebra de linha como separador *entre* telefones; permitir `\n` dentro do padrão uniria números em linhas consecutivas de uma lista.

## 7. Falsos positivos com CPF formatado em `extrair_telefones`
- **Dúvida:** Um CPF no formato `XXX.XXX.XXX-XX` que comece com DDD válido seguido de `9` (ex.: `119.876.543-21`) possui 11 dígitos e separadores aceitos (`.` e `-`).
- **Decisão:** Ignorar trechos que correspondam exatamente ao padrão clássico de CPF (`^\d{3}\.\d{3}\.\d{3}-\d{2}$`) em `extrair_telefones`.
- **Motivo:** O enunciado pede explicitamente que CPFs sejam ignorados sem erro em textos livres, e `XXX.XXX.XXX-XX` não é um formato usado para telefones brasileiros.

## 8. Telefones consecutivos separados por espaço, ponto ou hífen com espaços
- **Dúvida:** Em `"11 98765-4321. 21 3456-7890."` ou `"11 98765-4321 - 21 3456-7890"`, `.` e `-` também são separadores válidos dentro de um número.
- **Decisão:** Exigir fronteira de não-dígito antes e depois da correspondência e não permitir que um número termine imediatamente antes de `-<dígito>` ou `.<dígito>` (nem comece imediatamente após `<dígito>-` ou `<dígito>.`). Assim, `11-98765-4321-00` não é recortado, mas `11 98765-4321. 21 3456-7890` e `11 98765-4321 - 21 3456-7890` extraem ambos os telefones.
- **Motivo:** Garante que sequências maiores conectadas por hífen/ponto não tenham telefones recortados de dentro delas, ao mesmo tempo em que preserva pontuação final e separação entre múltiplos telefones no mesmo texto.
