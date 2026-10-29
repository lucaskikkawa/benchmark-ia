# Escrever testes para um carrinho

O módulo `carrinho.py` já está correto. Não o edite. Sua entrega é uma suíte
`tests/test_*.py` (pode entregar um único `tests/test_carrinho.py`) usando pytest.
A biblioteca do produto usa somente stdlib; pytest já está disponível no avaliador.
Todos os arquivos auxiliares da suíte devem ficar dentro de `tests/`.

API pública:

```python
def calcular_total(itens: list[tuple[int, int]], desconto: int = 0, frete: int = 0) -> int:
    ...
```

Cada tupla é `(quantidade, preco_em_centavos)`. Os argumentos são inteiros; tipos
fora desse contrato não precisam ser testados. Quantidade e preço devem ser >= 0,
`desconto` deve estar entre 0 e 100 inclusive, e `frete` deve ser >= 0. Qualquer
violação lança `ValueError`, inclusive em carrinho vazio ou quantidade zero.
O total bruto é a soma de quantidade vezes preço. Aplique o desconto UMA VEZ sobre
o bruto e trunque para baixo: `bruto * (100 - desconto) // 100`. Depois acrescente
frete sem desconto SOMENTE se a soma de quantidades for maior que zero. Logo, item
gratuito com quantidade positiva paga frete; linhas com quantidade zero não.
A lista recebida não deve ser alterada. Chamadas são independentes.

Teste exclusivamente o comportamento público com asserts, incluindo bordas e
exceções. Não inspecione fonte, bytecode, nomes de arquivos de mutantes, variáveis
do avaliador ou o ambiente para distinguir implementações. Não substitua a função
que está testando nem escreva implementações alternativas de carrinho.

A avaliação primeiro roda sua suíte no módulo correto (deve passar) e depois em
10 cópias com um bug cada. Cada mutante é um teste independente do benchmark,
aprovado quando sua suíte tem falha de teste nele (exit code 1). Erros de coleta,
nenhum teste ou timeout não contam como mutante morto. Cada execução da suíte
precisa terminar em até 8 segundos. Não é necessário usar plugins de pytest.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
