"""Modelos e exceções do acervo e dos empréstimos."""

import datetime
from dataclasses import dataclass


class BibliotecaErro(Exception):
    """Erro base das operações da biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """O ISBN não existe no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """O livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """O usuário atingiu o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Não há empréstimo ativo para o ISBN."""


class RenovacaoNegada(BibliotecaErro):
    """A renovação não é permitida para este empréstimo."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for nome, valor in (
            ("isbn", self.isbn),
            ("titulo", self.titulo),
            ("autor", self.autor),
        ):
            if not isinstance(valor, str):
                raise TypeError(f"{nome} deve ser str")
            if valor.strip() == "":
                raise ValueError(f"{nome} não pode ser vazio")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
