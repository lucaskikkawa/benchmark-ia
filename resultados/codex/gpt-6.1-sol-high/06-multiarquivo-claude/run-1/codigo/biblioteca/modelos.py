"""Modelos imutáveis e exceções da biblioteca."""

from dataclasses import dataclass
from datetime import date


class BibliotecaErro(Exception):
    """Erro de domínio da biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """O livro não pertence ao acervo."""


class LivroIndisponivel(BibliotecaErro):
    """O livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """O usuário atingiu o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """O livro não possui empréstimo ativo."""


class RenovacaoNegada(BibliotecaErro):
    """O empréstimo não pode ser renovado."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for nome in ("isbn", "titulo", "autor"):
            valor = getattr(self, nome)
            if not isinstance(valor, str):
                raise TypeError(f"{nome} deve ser str")
            if not valor.strip():
                raise ValueError(f"{nome} não pode ser vazio ou conter só espaços")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: date
    data_prevista: date
    renovacoes: int = 0
