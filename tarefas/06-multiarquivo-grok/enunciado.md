# Tarefa: pacote de empréstimos da biblioteca

Crie um pacote `biblioteca` no diretório de trabalho, com exatamente estes quatro arquivos. Dentro do pacote use **imports relativos** (`from .models import ...`). Só a biblioteca padrão.

```text
biblioteca/__init__.py
biblioteca/models.py
biblioteca/catalogo.py
biblioteca/emprestimos.py
```

`biblioteca/__init__.py` exporta `Livro`, `ErroBiblioteca`, `Catalogo` e `ServicoEmprestimos`.

## models.py

```python
class ErroBiblioteca(Exception):
    ...

@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int
```

`Livro` valida no `__post_init__` e levanta `ErroBiblioteca`:

- `isbn`: string com exatamente 13 dígitos (`0-9`), sem hífen e sem espaços nas pontas. Não confira o dígito verificador.
- `titulo`: string. Guarde a versão com `strip`. Se ficar vazia, erro.
- `exemplares`: `int` ≥ 1. `bool` não vale.

## catalogo.py

```python
class Catalogo:
    def adicionar(self, livro: Livro) -> None: ...
    def buscar(self, isbn: str) -> Livro: ...
    def listar(self) -> list[Livro]: ...
```

- `adicionar` exige uma instância de `Livro`. ISBN repetido → `ErroBiblioteca`.
- `buscar` devolve o livro ou `ErroBiblioteca` se o ISBN não está no catálogo.
- `listar` devolve os livros ordenados pelo ISBN.

O catálogo não sabe de empréstimos.

## emprestimos.py

```python
class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None: ...
    def emprestar(self, isbn: str, usuario: str, dia: str) -> None: ...
    def devolver(self, isbn: str, usuario: str, dia: str) -> int: ...
    def disponiveis(self, isbn: str) -> int: ...
    def ativos(self) -> list[tuple[str, str, str]]: ...
```

- O construtor exige um `Catalogo`. Guarde essa instância.
- `usuario` é string; use a forma com `strip`. Vazio depois do strip → `ErroBiblioteca`.
- `dia` é `YYYY-MM-DD` de um dia real. Qualquer outra coisa → `ErroBiblioteca`.
- `emprestar` exige o ISBN no catálogo. O mesmo usuário não pode ter dois empréstimos ativos do mesmo ISBN. Sem exemplar livre → `ErroBiblioteca`.
- Exemplares livres = `exemplares` do livro menos empréstimos ativos daquele ISBN.
- O prazo é 14 dias corridos a partir do dia do empréstimo. A data prevista é `dia_emprestimo + 14 dias`.
- `devolver` devolve o atraso em dias inteiros: `max(0, (dia_devolucao - data_prevista).days)`. No dia do empréstimo ou antes da data prevista o atraso é 0. Devolução anterior ao dia do empréstimo → `ErroBiblioteca`. Empréstimo inexistente (ou já devolvido) → `ErroBiblioteca`. A devolução libera o exemplar.
- `disponiveis` levanta `ErroBiblioteca` se o ISBN não está no catálogo.
- `ativos` lista só o que ainda não foi devolvido, como tuplas `(isbn, usuario, dia_emprestimo)` com o dia em `YYYY-MM-DD`. Ordem: dia, depois ISBN, depois usuário.

Erros de regra são sempre `ErroBiblioteca`, não `ValueError`.

## Exemplos

```python
catalogo = Catalogo()
catalogo.adicionar(Livro("9780000000001", "  Dom Casmurro ", 1))
servico = ServicoEmprestimos(catalogo)
servico.emprestar("9780000000001", "Ana", "2024-01-01")
servico.disponiveis("9780000000001")          # 0
servico.devolver("9780000000001", "Ana", "2024-01-16")  # 1
# prevista = 2024-01-15; devolver em 2024-01-15 -> 0
```

`2024-02-29` mais 14 dias cai em `2024-03-14`.
