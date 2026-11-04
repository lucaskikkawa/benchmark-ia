from dataclasses import dataclass
import datetime


class BibliotecaErro(Exception):
    """Exceção base do pacote biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """Livro não encontrado no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """Livro já está emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """Usuário atingiu o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Empréstimo ativo não encontrado para o livro."""


class RenovacaoNegada(BibliotecaErro):
    """Renovação não permitida para o empréstimo."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for nome_campo, valor in (
            ("isbn", self.isbn),
            ("titulo", self.titulo),
            ("autor", self.autor),
        ):
            if not isinstance(valor, str):
                raise TypeError(f"{nome_campo} deve ser str")
            if not valor.strip():
                raise ValueError(f"{nome_campo} não pode ser vazio")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
