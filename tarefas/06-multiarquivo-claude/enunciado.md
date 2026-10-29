# Tarefa: pacote `biblioteca` (acervo + empréstimos)

Crie no diretório de trabalho o pacote `biblioteca/` com **exatamente estes 4 arquivos**, usando
imports relativos entre os módulos (`from .modelos import ...`) e apenas a biblioteca padrão:

```
biblioteca/
├── __init__.py      # reexporta a API pública abaixo
├── modelos.py       # dataclasses Livro, Emprestimo e as exceções
├── acervo.py        # classe Acervo
└── emprestimos.py   # classe ServicoEmprestimos
```

## `modelos.py`

```python
@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
```

`Livro` valida os campos ao ser criado (`__post_init__`): `isbn`, `titulo` e `autor` devem ser `str`
(senão `TypeError`) e não podem ser vazios nem só espaços (senão `ValueError`).

Exceções (todas herdam de `BibliotecaErro(Exception)`): `LivroNaoEncontrado`, `LivroIndisponivel`,
`LimiteEmprestimos`, `EmprestimoNaoEncontrado`, `RenovacaoNegada`.

## `acervo.py` — `class Acervo`

- `adicionar(livro: Livro) -> None` — `TypeError` se não for `Livro`; `ValueError` se já existir livro
  com o mesmo `isbn`.
- `obter(isbn: str) -> Livro` — `LivroNaoEncontrado` se não existir.
- `buscar_por_autor(trecho: str) -> list[Livro]` — livros cujo `autor` contém `trecho`, sem diferenciar
  maiúsculas/minúsculas (compare com `str.casefold()`; `"STRAUSS"` encontra `"Strauß"`), ordenados por
  `titulo` e depois `isbn`. Trecho vazio encontra todos.
- `__len__()` — quantidade de livros; `__contains__(isbn)` — `isbn in acervo`.

## `emprestimos.py` — `class ServicoEmprestimos`

```python
ServicoEmprestimos(acervo: Acervo, limite_por_usuario: int = 3, prazo_dias: int = 14,
                   multa_diaria: float = 1.0, max_renovacoes: int = 2)
```

- `ValueError` no construtor se `limite_por_usuario < 1`, `prazo_dias < 1`, `multa_diaria < 0`
  ou `max_renovacoes < 0`.

- `emprestar(isbn: str, usuario: str, data: datetime.date) -> Emprestimo`
  - `LivroNaoEncontrado` se o isbn não está no acervo;
  - `LivroIndisponivel` se o livro já está emprestado;
  - `LimiteEmprestimos` se o usuário já tem `limite_por_usuario` empréstimos ativos;
  - (verificações nesta ordem) `data_prevista = data + prazo_dias`.
  - O serviço usa o **mesmo** objeto `Acervo` recebido: livros adicionados ao acervo depois da criação
    do serviço podem ser emprestados.
- `devolver(isbn: str, data: datetime.date) -> float` — encerra o empréstimo e retorna a multa:
  `dias_de_atraso * multa_diaria` (atraso = dias após `data_prevista`; devolver até a data prevista → `0.0`),
  arredondada a 2 casas.
  - `LivroNaoEncontrado` se o isbn não está no acervo; `EmprestimoNaoEncontrado` se não está emprestado;
  - `ValueError` se `data` for anterior a `data_emprestimo` (o empréstimo continua ativo).
- `disponivel(isbn: str) -> bool` — `LivroNaoEncontrado` se o isbn não está no acervo.
- `emprestimos_de(usuario: str) -> list[Emprestimo]` — ativos do usuário, ordenados por `data_prevista` e depois `isbn`.
- `renovar(isbn: str, data: datetime.date) -> Emprestimo` — substitui o empréstimo ativo por um novo com
  `renovacoes + 1` e `data_prevista = max(data_prevista atual, data + prazo_dias)` (os demais campos não
  mudam) e o retorna. Verificações nesta ordem:
  - `LivroNaoEncontrado` se o isbn não está no acervo; `EmprestimoNaoEncontrado` se não está emprestado;
  - `ValueError` se `data` for anterior a `data_emprestimo`;
  - `RenovacaoNegada` se o empréstimo está atrasado (`data > data_prevista`) ou se já foi renovado
    `max_renovacoes` vezes. Em qualquer erro o empréstimo continua como estava.
- `atrasados(data: datetime.date) -> list[Emprestimo]` — empréstimos ativos (de todos os usuários) com
  `data_prevista < data`, ordenados por `data_prevista` e depois `isbn`.
- `devolver` usa a `data_prevista` vigente (após renovações).

`biblioteca/__init__.py` deve permitir `from biblioteca import Livro, Emprestimo, Acervo, ServicoEmprestimos,
BibliotecaErro, LivroNaoEncontrado, LivroIndisponivel, LimiteEmprestimos, EmprestimoNaoEncontrado,
RenovacaoNegada` e definir `__all__` com exatamente esses 10 nomes.
