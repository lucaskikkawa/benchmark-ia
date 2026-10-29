"""Entidades e exceções do domínio."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for campo in ("isbn", "titulo", "autor"):
            valor = getattr(self, campo)
            if not isinstance(valor, str):
                raise TypeError(f"{campo} deve ser str, recebido {type(valor).__name__}")
            if not valor.strip():
                raise ValueError(f"{campo} não pode ser vazio")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: date
    data_prevista: date
    renovacoes: int = 0


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


class RenovacaoNegada(BibliotecaErro):
    """Empréstimo atrasado ou com o máximo de renovações."""
