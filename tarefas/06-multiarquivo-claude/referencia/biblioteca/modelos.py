"""Entidades e exceções do domínio."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: date
    data_prevista: date


class BibliotecaErro(Exception):
    """Base de todos os erros do pacote."""


class LivroNaoEncontrado(BibliotecaErro):
    """ISBN não cadastrado no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """Livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """Usuário atingiu o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Não há empréstimo ativo para o livro."""
