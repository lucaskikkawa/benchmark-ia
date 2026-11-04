# Tarefa: corrigir bugs em `intervalos.py`

O arquivo `intervalos.py` (no diretório de trabalho) tem duas funções públicas:

```python
def mesclar_intervalos(intervalos: Iterable[tuple[int, int] | list[int]]) -> list[tuple[int, int]]: ...
def total_coberto(intervalos: Iterable[tuple[int, int] | list[int]]) -> int: ...
```

O comportamento esperado está descrito nas docstrings do próprio arquivo e é a especificação oficial
(as docstrings foram atualizadas recentemente; o código não acompanhou todas as mudanças).
Usuários relataram que:

- `mesclar_intervalos([])` levanta uma exceção em vez de retornar `[]`;
- em alguns casos o resultado vem errado (intervalos não unidos ou com tamanho menor que o esperado),
  e `total_coberto` herda esses erros.

Pode haver mais de um bug, inclusive desvios da docstring que nenhum usuário relatou. **Edite `intervalos.py`** para que as duas funções sigam as docstrings.
Não mude os nomes nem as assinaturas, não crie outros arquivos obrigatórios e use apenas a biblioteca padrão.

Exemplos esperados:

```python
mesclar_intervalos([(5, 7), (1, 3)])          # [(1, 3), (5, 7)]
mesclar_intervalos([(1, 3), (3, 6)])          # [(1, 6)]   (se tocam)
mesclar_intervalos([(1, 10), (2, 3), (4, 5)]) # [(1, 10)]
total_coberto([(1, 3), (2, 6), (8, 9)])       # 6
```
