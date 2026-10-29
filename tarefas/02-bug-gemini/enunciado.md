# 02 - Correção de Bugs no Carrinho de Compras

Você recebeu o módulo `carrinho.py` que implementa a classe `CarrinhoDeCompras`. O código atual possui diversos bugs lógicos e falta de validações críticas.

Sua tarefa é corrigir e refatorar o arquivo `carrinho.py` na raiz do diretório de trabalho, garantindo que ele passe em todos os testes e satisfaça as especificações abaixo.

## Requisitos e Assinaturas

A classe `CarrinhoDeCompras` deve conter os seguintes métodos:

- `__init__(self, itens: dict | None = None) -> None`:
  - Inicializa o carrinho. Instâncias diferentes NÃO devem compartilhar o dicionário de itens.
  - Se `itens` for fornecido, deve criar uma cópia isolada (incluindo os dicionários internos de cada item) para garantir que alterações externas posteriores não modifiquem o carrinho.

- `adicionar_item(self, nome: str, preco: float, quantidade: int = 1) -> None`:
  - `nome` deve ser uma string não vazia (`isinstance(nome, str)` e `nome.strip() != ""`); caso contrário, levanta `ValueError` (se vazia/em branco) ou `TypeError` (se não for string).
  - `preco` deve ser `int` ou `float` (rejeitando `bool`) estritamente positivo (`preco > 0`). Se `<= 0`, levanta `ValueError`; se não for numérico, levanta `TypeError`.
  - `quantidade` deve ser um número inteiro (`type(quantidade) is int`) estritamente positivo (`quantidade > 0`). Se `<= 0`, levanta `ValueError`; se não for `int`, levanta `TypeError`.
  - Se o item já existir no carrinho, incrementa a quantidade existente e atualiza o preço unitário para o novo valor informado.

- `remover_item(self, nome: str, quantidade: int | None = None) -> None`:
  - Se `nome` não estiver no carrinho, levanta `KeyError`.
  - Se `quantidade` for informada e não for `int` (rejeitando `bool`), levanta `TypeError`.
  - Se `quantidade` for informada e for `<= 0`, levanta `ValueError`.
  - Se `quantidade is None` ou se `quantidade >= quantidade_atual`, remove completamente o item do carrinho.
  - Se `quantidade < quantidade_atual`, subtrai a quantidade correspondente.

- `aplicar_cupom(self, codigo: str, desconto_porcentagem: float) -> None`:
  - `codigo` deve ser uma string não vazia (`isinstance(codigo, str)` e `codigo.strip() != ""`); caso contrário, levanta `ValueError` (se vazia/em branco) ou `TypeError` (se não for string).
  - `desconto_porcentagem` deve ser `int` ou `float` (rejeitando `bool`) entre `0` e `100` (inclusive). Se menor que 0 ou maior que 100, levanta `ValueError`; se não for numérico, levanta `TypeError`.
  - Substitui qualquer cupom anteriormente aplicado.

- `remover_cupom(self) -> None`:
  - Remove o cupom ativo (se não houver, não faz nada).

- `calcular_subtotal(self) -> float`:
  - Retorna a soma de `preco * quantidade` de todos os itens, arredondada para 2 casas decimais (`round(..., 2)`).

- `calcular_desconto(self) -> float`:
  - Se houver cupom ativo, retorna o valor do desconto calculado como `subtotal * (porcentagem / 100)`, arredondado para 2 casas decimais. Se não houver cupom, retorna `0.0`.

- `calcular_total(self) -> float`:
  - Retorna `subtotal - desconto`, arredondado para 2 casas decimais (nunca inferior a 0.0).

- `listar_itens(self) -> list[dict]`:
  - Retorna nova lista de novos dicionários com os itens presentes, **ordenados pelo nome do item usando a ordem lexicográfica padrão do Python (`sorted`, sem locale)**, inclusive para nomes com acentos:
    ```python
    [
        {
            "nome": "Caderno",
            "preco": 15.5,
            "quantidade": 2,
            "total": 31.0,
        },
        ...
    ]
    ```
  - Alterações nos dicionários retornados não devem impactar o estado interno do carrinho.
