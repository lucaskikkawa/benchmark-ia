# Pacote de movimentos de estoque

Complete o pacote `estoque/`, mantendo exatamente seus quatro módulos Python:
`__init__.py`, `modelos.py`, `operacoes.py`, `persistencia.py`. Todos já existem.
Não crie outros módulos. Exporte estas três APIs de `estoque`:

```python
# modelos.py
@dataclass(frozen=True)
class Movimento:
    sku: str
    delta: int

# operacoes.py
def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]: ...

# persistencia.py
def carregar_movimentos(caminho) -> list[Movimento]: ...
```

`Movimento` é uma dataclass imutável com igualdade por campos, sem validação no
construtor. `calcular_saldos` aceita um iterável de movimentos válidos e um dict
opcional de saldos iniciais inteiros. Copie os saldos iniciais (não os altere).
SKU novo começa em zero. Aplique movimentos NA ORDEM e lance `ValueError` se
algum saldo inicial ou intermediário for negativo, mesmo que um movimento posterior
reponha o estoque. Retenha entradas de saldo zero e SKUs iniciais sem movimentos.
Retorne um dict novo inclusive na entrada vazia. Não precisa validar tipos nessa função.

`carregar_movimentos` lê um arquivo JSON UTF-8 (str ou Path) contendo lista de
objetos. Cada objeto precisa de `sku` string com ao menos um caractere não branco
(preserve a string original) e `delta` inteiro; bool não é aceito como inteiro.
Campos extras são ignorados. Forma inválida, campos ausentes, SKU inválido ou delta
inválido lançam `ValueError`; JSON inválido também deve ser `ValueError` (a exceção
nativa de json atende). Erros de arquivo podem propagar. A ordem deve ser mantida.
Lista vazia gera `[]`. Use imports relativos entre os módulos do pacote.

Movimentos podem vir de um iterável de passagem única. O construtor de
`Movimento` apenas armazena os campos, mesmo para valores que o carregador
rejeitaria; a validação de JSON pertence a `persistencia.py`. Inteiros de saldos
e deltas têm precisão arbitrária, sem conversão para float. SKUs são chaves
exatas, sem strip, casefold ou normalização Unicode. Falhas na aplicação de
movimentos também não podem alterar `iniciais`. Chamadas independentes não
compartilham resultados. Os testes podem carregar 20.000 movimentos.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
