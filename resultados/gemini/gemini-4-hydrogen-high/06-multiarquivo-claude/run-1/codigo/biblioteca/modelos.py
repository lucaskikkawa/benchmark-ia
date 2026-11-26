from dataclasses import dataclass
import datetime


class BibliotecaErro(Exception):
    """Exceção base para erros do pacote biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """Lançada quando o ISBN não existe no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """Lançada quando o livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """Lançada quando o usuário atinge o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Lançada quando não há empréstimo ativo para o livro."""


class RenovacaoNegada(BibliotecaErro):
    """Lançada quando a renovação do empréstimo não é permitida."""


@dataclass(frozen=True)
class Livro:
    """Representa um livro cadastrado no acervo."""

    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for campo, valor in (
            ("isbn", self.isbn),
            ("titulo", self.titulo),
            ("autor", self.autor),
        ):
            if not isinstance(valor, str):
                raise TypeError(f"{campo} deve ser str")
            if not valor.strip():
                raise ValueError(f"{campo} não pode ser vazio nem só espaços")


@dataclass(frozen=True)
class Emprestimo:
    """Representa um empréstimo ativo de um livro."""

    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
