from dataclasses import dataclass
import datetime


class BibliotecaErro(Exception):
    pass


class LivroNaoEncontrado(BibliotecaErro):
    pass


class LivroIndisponivel(BibliotecaErro):
    pass


class LimiteEmprestimos(BibliotecaErro):
    pass


class EmprestimoNaoEncontrado(BibliotecaErro):
    pass


class RenovacaoNegada(BibliotecaErro):
    pass


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
        for nome, valor in (
            ("isbn", self.isbn),
            ("titulo", self.titulo),
            ("autor", self.autor),
        ):
            if not valor.strip():
                raise ValueError(f"{nome} não pode ser vazio")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
