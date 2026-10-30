from dataclasses import dataclass
import datetime


class BibliotecaErro(Exception):
    """Exceção base para erros do pacote biblioteca."""


class LivroNaoEncontrado(BibliotecaErro):
    """Livro não encontrado no acervo."""


class LivroIndisponivel(BibliotecaErro):
    """Livro já se encontra emprestado."""


class LimiteEmprestimos(BibliotecaErro):
    """Usuário atingiu o limite de empréstimos ativos."""


class EmprestimoNaoEncontrado(BibliotecaErro):
    """Não há empréstimo ativo para o livro informado."""


class RenovacaoNegada(BibliotecaErro):
    """Renovação não permitida para o empréstimo."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    autor: str

    def __post_init__(self) -> None:
        for nome, valor in (("isbn", self.isbn), ("titulo", self.titulo), ("autor", self.autor)):
            if not isinstance(valor, str):
                raise TypeError(f"O campo '{nome}' deve ser uma str.")
            if not valor.strip():
                raise ValueError(f"O campo '{nome}' não pode ser vazio ou conter apenas espaços.")


@dataclass(frozen=True)
class Emprestimo:
    isbn: str
    usuario: str
    data_emprestimo: datetime.date
    data_prevista: datetime.date
    renovacoes: int = 0
