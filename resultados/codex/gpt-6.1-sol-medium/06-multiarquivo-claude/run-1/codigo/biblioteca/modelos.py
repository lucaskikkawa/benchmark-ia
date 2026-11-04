"""Modelos imutáveis e exceções da biblioteca."""

from dataclasses import dataclass
from datetime import date


class BibliotecaErro(Exception):
    """Erro de domínio da biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """O ISBN não está no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """O livro já possui um empréstimo ativo."""


class LimiteEmprestimos(BibliotecaErro):
    """O usuário atingiu seu limite de empréstimos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """O livro não possui um empréstimo ativo."""


class RenovacaoNegada(BibliotecaErro):
    """O empréstimo não pode ser renovado."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for campo in ("isbn", "titulo", "autor"):
            valor = getattr(self, campo)
            if not isinstance(valor, str):
                raise TypeError(f"{campo} deve ser str")
            if not valor.strip():
                raise ValueError(f"{campo} não pode ser vazio")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: date
    data_prevista: date
    renovacoes: int = 0
