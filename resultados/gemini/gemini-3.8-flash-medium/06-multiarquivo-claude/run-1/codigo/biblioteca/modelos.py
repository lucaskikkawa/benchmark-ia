from dataclasses import dataclass
import datetime


class BibliotecaErro(Exception):
    """Exceção base da biblioteca."""
    pass


class LivroNaoEncontrado(BibliotecaErro):
    """Livro não encontrado no acervo."""
    pass


class LivroIndisponivel(BibliotecaErro):
    """Livro já está emprestado."""
    pass


class LimiteEmprestimos(BibliotecaErro):
    """Usuário atingiu o limite de empréstimos."""
    pass


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Empréstimo não encontrado."""
    pass


class RenovacaoNegada(BibliotecaErro):
    """Renovação de empréstimo negada."""
    pass


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for campo, valor in (("isbn", self.isbn), ("titulo", self.titulo), ("autor", self.autor)):
            if not isinstance(valor, str):
                raise TypeError(f"O campo '{campo}' deve ser str")
        for campo, valor in (("isbn", self.isbn), ("titulo", self.titulo), ("autor", self.autor)):
            if not valor.strip():
                raise ValueError(f"O campo '{campo}' não pode ser vazio ou conter apenas espaços")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
