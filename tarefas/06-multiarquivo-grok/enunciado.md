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

- `isbn`: string com exatamente 13 dígitos ASCII (`0-9`), sem hífen e sem espaços. Não confira o dígito verificador: `9780000000001` é válido mesmo que o verificador ISBN-13 não feche. Não dê `strip` no ISBN.
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
- `buscar` devolve o livro ou `ErroBiblioteca` se o ISBN não está no catálogo. A comparação é exata, sem `strip`.
- `listar` devolve uma **lista nova** com os livros ordenados pelo ISBN. Alterar essa lista não muda o catálogo.

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

- O construtor exige um `Catalogo`. Guarde essa instância. Dois serviços no mesmo catálogo **não compartilham** empréstimos: o estoque livre é o do próprio serviço.
- `usuario` é string; use `str.strip` (inclui espaço Unicode, como `\u00a0`). Vazio depois do strip → `ErroBiblioteca`. Espaços internos permanecem e distinguem usuários (`"Ana Maria"` e `"Ana  Maria"` são pessoas diferentes).
- `dia` é `YYYY-MM-DD` de um dia real no calendário gregoriano (`datetime.date`, anos 1 a 9999). `1900-02-29` não existe. Qualquer outra coisa → `ErroBiblioteca`.
- `emprestar` exige o ISBN no catálogo, comparado sem `strip`. O mesmo usuário não pode ter dois empréstimos ativos do mesmo ISBN, mesmo que ainda haja exemplar. Sem exemplar livre → `ErroBiblioteca`.
- Exemplares livres = `exemplares` do livro menos os empréstimos ativos **deste serviço** para aquele ISBN.
- O prazo é 14 dias corridos a partir do dia do empréstimo. A data prevista é `dia_emprestimo + 14 dias`, inclusive quando isso muda de mês ou de ano (`2024-12-20` → `2025-01-03`; `2024-01-31` → `2024-02-14`).
- `devolver` devolve o atraso em dias inteiros: `max(0, (dia_devolucao - data_prevista).days)`. No dia do empréstimo ou até a data prevista, inclusive, o atraso é 0. Devolução anterior ao dia do empréstimo → `ErroBiblioteca`. Empréstimo inexistente (ou já devolvido) → `ErroBiblioteca`. A devolução libera o exemplar.
- Se `emprestar` ou `devolver` levantar `ErroBiblioteca`, o estado anterior permanece (nada de reservar e desfazer pela metade).
- `disponiveis` levanta `ErroBiblioteca` se o ISBN não está no catálogo.
- `ativos` lista só o que ainda não foi devolvido, como tuplas `(isbn, usuario, dia_emprestimo)` com o dia em `YYYY-MM-DD`. Ordem: dia, depois ISBN, depois usuário, a mesma de `sorted` em code point (`"A"` antes de `"a"` antes de `"á"`).

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
