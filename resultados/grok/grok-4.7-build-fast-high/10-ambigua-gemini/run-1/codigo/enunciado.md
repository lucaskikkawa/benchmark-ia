# 10 - Classificação de Clientes e Score de Fidelidade (Especificação com Pontos Abertos)

Implemente a função `classificar_cliente` no arquivo `solucao.py` na raiz do seu diretório de trabalho.

## Assinatura

```python
def classificar_cliente(dados: dict) -> dict:
    ...
```

## Núcleo Explícito Obrigatório

O dicionário `dados` de entrada possui as seguintes informações sobre o cliente:
- `id` (str): identificador único do cliente.
- `nome` (str): nome do cliente.
- `compras` (list[float | int]): histórico de valores de compras realizadas.
- `anos_ativo` (int): número de anos em que o cliente é usuário ativo.

### Regras Inequívocas de Cálculo do Score:
1. O score base de compras corresponde a **10% da soma dos valores das compras** (`soma_compras * 0.1`).
2. O score de fidelidade concede **5 pontos por cada ano ativo** (`anos_ativo * 5`).
3. O score final é a soma do score base de compras com o score de fidelidade, devendo ser arredondado para 2 casas decimais (`round(..., 2)`).
4. O dicionário de retorno deve conter obrigatoriamente as chaves:
   - `"id"`: mesmo id de entrada (preservado).
   - `"nome"`: mesmo nome de entrada (preservado).
   - `"score"`: número (float ou int) correspondente ao score final calculado.
   - `"categoria"`: uma string não vazia representando o segmento/nível do cliente.
5. **Imutabilidade**: A função não deve modificar o dicionário `dados` fornecido na entrada nem a lista `compras` nele contida.
6. A função deve suportar grande volume de compras e entradas com caracteres Unicode em `id` e `nome`.

## Pontos Abertos e Arquivo `SUPOSICOES.md` (OBRIGATÓRIO)

Alguns aspectos do comportamento não foram fechados na especificação, tais como:
- Quais nomes de categorias atribuir e quais faixas/critérios de pontuação utilizar para categorizar o cliente.
- Como lidar com valores negativos na lista de compras (ex.: estornos/devoluções vs. ignorar).
- Como interpretar ou ajustar anos ativos negativos caso ocorram.
- Como tratar campos adicionais presentes na entrada.

Você **DEVE** criar um arquivo chamado `SUPOSICOES.md` na raiz do diretório de trabalho documentando detalhadamente suas decisões de design, critérios de categorização adotados e premissas assumidas.

> **Importante:** A suíte de testes automatizados valida exclusivamente o **núcleo explícito inequívoco** e a presença do arquivo `SUPOSICOES.md`. A qualidade e profundidade da sua documentação de suposições serão avaliadas pela rubrica qualitativa.
