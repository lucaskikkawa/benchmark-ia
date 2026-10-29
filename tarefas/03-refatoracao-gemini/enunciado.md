# 03 - Refatoração do Processador de Pedidos

Você recebeu um código legado funcional em `processador.py` com a função `processar_pedidos`. Embora o código funcione para casos básicos, ele é monolítico, desorganizado, sem tipos e viola o princípio de responsabilidade única.

Sua tarefa é refatorar `processador.py` na raiz do diretório de trabalho, mantendo a interface e o formato de retorno da função `processar_pedidos` e extraindo uma arquitetura limpa e orientada a objetos com as classes e estruturas detalhadas abaixo. Nos cálculos, prevalecem as regras detalhadas a seguir, inclusive o arredondamento por item antes de somar os subtotais e pesos.

## Classes e Métodos Exigidos

O arquivo `processador.py` deve definir e exportar:

### 1. `ItemPedido` (dataclass ou classe)
- Atributos:
  - `nome: str`
  - `preco: float`
  - `quantidade: int = 1`
  - `peso_kg: float = 0.5`
- Propriedades ou métodos:
  - `subtotal`: retorna `round(preco * quantidade, 2)`
  - `peso_total`: retorna `round(peso_kg * quantidade, 3)`

### 2. `CalculadoraFrete`
- Método:
  - `calcular(tipo: str, peso_kg: float, valor_total: float) -> float` (método de classe ou estático):
    - Se `valor_total >= 200.0`, o frete é grátis: retorna `0.0`.
    - Caso contrário, calcula conforme o tipo de frete (case-insensitive):
      - `"padrao"`: `round(10.0 + peso_kg * 1.5, 2)`
      - `"expresso"`: `round(25.0 + peso_kg * 3.0, 2)`
      - `"economico"`: `round(5.0 + peso_kg * 0.8, 2)`
      - Qualquer outro tipo: levanta `ValueError(f"Tipo de frete desconhecido: {tipo}")`.

### 3. `CalculadoraDesconto`
- Método:
  - `calcular(categoria_cliente: str, valor_total: float) -> float` (método de classe ou estático):
    - Conforme a categoria do cliente (case-insensitive):
      - `"bronze"`: `0.0`
      - `"prata"`: `round(0.05 * valor_total, 2)` se `valor_total >= 100.0`, senão `0.0`
      - `"ouro"`: `round(0.10 * valor_total, 2)` se `valor_total >= 50.0`, senão `round(0.05 * valor_total, 2)`
      - `"vip"`: `round(0.15 * valor_total, 2)` incondicional
      - Outras categorias: `0.0`

### 4. `Pedido` (dataclass ou classe)
- Atributos:
  - `id: str`
  - `cliente: str`
  - `categoria_cliente: str = "bronze"`
  - `itens: list[ItemPedido]` (padrão lista vazia)
  - `tipo_frete: str = "padrao"`
- Métodos:
  - `calcular_total_itens() -> float`: soma dos subtotais dos itens (arredondado em 2 casas).
  - `calcular_peso_total() -> float`: soma dos pesos totais dos itens.
  - `calcular_desconto() -> float`: delega para `CalculadoraDesconto`.
  - `calcular_frete() -> float`: delega para `CalculadoraFrete`.
  - `calcular_total_final() -> float`: `total_itens - desconto + frete` (arredondado em 2 casas).
  - `para_dict() -> dict`:
    ```python
    {
        "id": self.id,
        "cliente": self.cliente,
        "subtotal": self.calcular_total_itens(),
        "desconto": self.calcular_desconto(),
        "frete": self.calcular_frete(),
        "total": self.calcular_total_final(),
    }
    ```

### 5. `processar_pedidos(pedidos: list[dict]) -> list[dict]`
- Recebe a lista de pedidos no formato de dicionário bruto, instancia as entidades modeladas e retorna a lista de dicionários resultantes de cada `pedido.para_dict()`.
