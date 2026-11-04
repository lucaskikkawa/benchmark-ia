# Suposições

- **Faixa de DDDs:** interpretei “11 a 99, exceto 20, 30, ..., 90” como DDD numérico de 11 a 99 cujo segundo algarismo não seja zero. Assim, `10` e `20` são inválidos, enquanto `19` é aceito. Isso segue a faixa e as exceções descritas no enunciado.
- **Código do país sem `+`:** removo o prefixo `55` somente quando o total tem 12 ou 13 algarismos. Com 10 ou 11 algarismos, `55` pode ser o próprio DDD/número local e não é removido. Isso evita alterar telefones locais por engano.
- **Sinal `+`:** quando presente, deve anteceder o código `55`; não aceito sinais em outra posição nem outros caracteres além de algarismos, espaços, hífens, pontos e parênteses. O enunciado define esses separadores e o E.164 brasileiro.
- **Parênteses:** aceito no máximo um par balanceado envolvendo dois algarismos, como no DDD. O time citou parênteses ao redor do DDD como formato válido; exigir o par reduz interpretações acidentais.
- **Extração em texto livre:** considero telefone um trecho com 10 ou 11 algarismos locais ou 12/13 com `55`, possivelmente separados por espaços, hífens e pontos, com parênteses no DDD. Não uso barra como separador interno, pois o enunciado a cita como separador entre telefones. Limites de algarismos impedem extrair telefones de dentro de sequências numéricas maiores; candidatos inválidos são ignorados.
- **Tipo de entrada de extração:** se `extrair_telefones` receber algo que não seja `str`, devolve lista vazia. O enunciado especifica texto livre; a escolha mantém a função tolerante a valores ausentes de CRM.
