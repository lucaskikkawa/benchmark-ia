"""Modelos de dados e exceções do pacote biblioteca."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for nome, valor in (("isbn", self.isbn), ("titulo", self.titulo), ("autor", self.autor)):
            if not isinstance(valor, str):
                raise TypeError(f"{nome} deve ser str")
            if not valor.strip():
                raise ValueError(f"{nome} não pode ser vazio")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: date
    data_prevista: date
    renovacoes: int = 0


class BibliotecaErro(Exception):
    """Classe base para erros de domínio da biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """O ISBN solicitado não pertence ao acervo."""


class LivroIndisponivel(BibliotecaErro):
    """O livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """O usuário atingiu o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Não há empréstimo ativo para o livro solicitado."""


class RenovacaoNegada(BibliotecaErro):
    """O empréstimo não pode ser renovado."""
