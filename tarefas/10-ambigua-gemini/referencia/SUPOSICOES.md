# Premissas e Suposições de Projeto

Este documento detalha as decisões de engenharia e suposições adotadas para os pontos abertos da especificação de classificação de clientes.

## 1. Faixas e Nomes de Categorias
Como os critérios de corte e os nomes de categoria não foram estipulados no enunciado, definimos três faixas intuitivas baseadas no score final calculado:
- **Ouro**: `score >= 100.0`
- **Prata**: `50.0 <= score < 100.0`
- **Bronze**: `score < 50.0`

## 2. Tratamento de Compras com Valores Negativos
Assumimos que entradas com valores negativos na lista `compras` representam estornos ou devoluções de mercadorias. Por conseguinte, tais valores são somados algebricamente (diminuindo o montante total de compras do cliente). Caso o somatório resulte negativo, ele é ponderado normalmente pelo fator de 10%.

## 3. Tratamento de Anos Ativos Negativos ou Inválidos
Por coerência temporal, um cliente não pode possuir tempo negativo de atividade na plataforma. Valores negativos informados em `anos_ativo` são normalizados para `0` (zero) anos de atividade, evitando penalização indevida de score de fidelidade.

## 4. Campos Adicionais no Dicionário de Entrada
Campos opcionais ou não especificados presentes no payload de entrada (como e-mail, telefone, endereço) são ignorados na geração do objeto de saída, preservando apenas as chaves explicitamente requeridas (`id`, `nome`, `score`, `categoria`).
