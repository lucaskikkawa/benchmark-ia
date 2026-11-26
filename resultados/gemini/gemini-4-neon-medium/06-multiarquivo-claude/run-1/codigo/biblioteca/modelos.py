from __future__ import annotations

from dataclasses import dataclass
import datetime


class BibliotecaErro(Exception):
    """Exceção base para erros do pacote biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """Exceção lançada quando o livro não é encontrado no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """Exceção lançada quando o livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """Exceção lançada quando o usuário atinge o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Exceção lançada quando não existe empréstimo ativo para o livro."""


class RenovacaoNegada(BibliotecaErro):
    """Exceção lançada quando a renovação do empréstimo não é permitida."""


@dataclass(frozen=True)
class Livro:
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
                raise TypeError(f"{campo} deve ser uma str")
            if not valor.strip():
                raise ValueError(f"{campo} não pode ser vazio nem conter apenas espaços")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
