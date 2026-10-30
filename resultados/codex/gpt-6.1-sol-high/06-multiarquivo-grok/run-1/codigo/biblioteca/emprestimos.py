"""Controle dos empréstimos ativos de cada serviço."""

from datetime import date

from .catalogo import Catalogo
from .models import ErroBiblioteca


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("O usuário deve ser uma string.")
    usuario = str.strip(usuario)
    if not usuario:
        raise ErroBiblioteca("O usuário não pode ser vazio.")
    return usuario


def _validar_dia(dia: str) -> date:
    if (
        not isinstance(dia, str)
        or len(dia) != 10
        or dia[4] != "-"
        or dia[7] != "-"
        or any(digito not in "0123456789" for digito in dia[:4] + dia[5:7] + dia[8:])
    ):
        raise ErroBiblioteca("O dia deve estar no formato YYYY-MM-DD.")
    try:
        return date.fromisoformat(dia)
    except ValueError as erro:
        raise ErroBiblioteca("O dia informado não existe no calendário.") from erro


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("O serviço exige uma instância de Catalogo.")
        self._catalogo = catalogo
        self._emprestimos: dict[tuple[str, str], date] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        self._catalogo.buscar(isbn)
        usuario = _validar_usuario(usuario)
        data_emprestimo = _validar_dia(dia)
        chave = (isbn, usuario)
        if chave in self._emprestimos:
            raise ErroBiblioteca("O usuário já possui um empréstimo ativo deste ISBN.")
        if self.disponiveis(isbn) == 0:
            raise ErroBiblioteca("Não há exemplares disponíveis deste ISBN.")
        self._emprestimos[chave] = data_emprestimo

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        self._catalogo.buscar(isbn)
        usuario = _validar_usuario(usuario)
        data_devolucao = _validar_dia(dia)
        chave = (isbn, usuario)
        if chave not in self._emprestimos:
            raise ErroBiblioteca("Empréstimo ativo não encontrado.")
        data_emprestimo = self._emprestimos[chave]
        if data_devolucao < data_emprestimo:
            raise ErroBiblioteca("A devolução não pode ser anterior ao empréstimo.")
        # Ordinais permitem o prazo de 14 dias até para empréstimos no ano 9999.
        atraso = max(0, data_devolucao.toordinal() - data_emprestimo.toordinal() - 14)
        del self._emprestimos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        emprestados = sum(1 for isbn_ativo, _ in self._emprestimos if isbn_ativo == isbn)
        return livro.exemplares - emprestados

    def ativos(self) -> list[tuple[str, str, str]]:
        return sorted(
            (
                (isbn, usuario, dia.isoformat())
                for (isbn, usuario), dia in self._emprestimos.items()
            ),
            key=lambda emprestimo: (emprestimo[2], emprestimo[0], emprestimo[1]),
        )
