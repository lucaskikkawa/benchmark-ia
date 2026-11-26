from __future__ import annotations

import datetime
from dataclasses import dataclass


class BibliotecaErro(Exception):
    """Exceção base para erros do pacote biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """Livro com o ISBN informado não existe no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """Livro já se encontra emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """Usuário atingiu o limite máximo de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Não há empréstimo ativo para o ISBN informado."""


class RenovacaoNegada(BibliotecaErro):
    """Renovação não permitida (empréstimo atrasado ou limite de renovações atingido)."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for nome, valor in (("isbn", self.isbn), ("titulo", self.titulo), ("autor", self.autor)):
            if not isinstance(valor, str):
                raise TypeError(f"{nome} deve ser str, recebido {type(valor).__name__}")
            if not valor.strip():
                raise ValueError(f"{nome} não pode ser vazio ou conter apenas espaços")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
