from dataclasses import dataclass
import datetime


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self):
        for nome in ("isbn", "titulo", "autor"):
            valor = getattr(self, nome)
            if not isinstance(valor, str):
                raise TypeError(f"{nome} deve ser str")
            if not valor.strip():
                raise ValueError(f"{nome} não pode ser vazio")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0


class BibliotecaErro(Exception):
    """Exceção base para erros do pacote biblioteca."""


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
