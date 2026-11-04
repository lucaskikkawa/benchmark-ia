"""Modelos de dados e exceções da biblioteca."""

from __future__ import annotations

import datetime
from dataclasses import dataclass


class BibliotecaErro(Exception):
    """Exceção base para erros da biblioteca."""
    pass


class LivroNaoEncontrado(BibliotecaErro):
    """Exceção lançada quando um livro não é encontrado no acervo."""
    pass


class LivroIndisponivel(BibliotecaErro):
    """Exceção lançada quando um livro já está emprestado."""
    pass


class LimiteEmprestimos(BibliotecaErro):
    """Exceção lançada quando o usuário atinge o limite de empréstimos ativos."""
    pass


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Exceção lançada quando um livro não possui empréstimo ativo."""
    pass


class RenovacaoNegada(BibliotecaErro):
    """Exceção lançada quando a renovação de empréstimo é negada."""
    pass


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for campo, nome in ((self.isbn, "isbn"), (self.titulo, "titulo"), (self.autor, "autor")):
            if not isinstance(campo, str):
                raise TypeError(f"O campo '{nome}' deve ser str.")
            if not campo.strip():
                raise ValueError(f"O campo '{nome}' não pode ser vazio nem conter apenas espaços.")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
