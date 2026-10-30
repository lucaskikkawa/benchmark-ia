"""Modelos e exceções do acervo e dos empréstimos."""

import datetime
from dataclasses import dataclass


class BibliotecaErro(Exception):
    """Erro base do pacote biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """O ISBN não existe no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """O livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """O usuário atingiu o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Não há empréstimo ativo para o ISBN."""


class RenovacaoNegada(BibliotecaErro):
    """A renovação foi recusada por atraso ou limite de renovações."""


def _validar_texto(nome: str, valor: object) -> None:
    if not isinstance(valor, str):
        raise TypeError(f"{nome} deve ser str")
    if valor.strip() == "":
        raise ValueError(f"{nome} não pode ser vazio nem conter só espaços")


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        _validar_texto("isbn", self.isbn)
        _validar_texto("titulo", self.titulo)
        _validar_texto("autor", self.autor)


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
