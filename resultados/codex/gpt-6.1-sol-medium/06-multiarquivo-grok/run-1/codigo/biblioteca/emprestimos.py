from datetime import date
import re

from .catalogo import Catalogo
from .models import ErroBiblioteca


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str) or not usuario.strip():
        raise ErroBiblioteca("Usuário deve ser uma string não vazia.")
    return usuario.strip()


def _validar_dia(dia: str) -> date:
    if not isinstance(dia, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", dia) is None:
        raise ErroBiblioteca("Dia deve estar no formato YYYY-MM-DD.")
    try:
        return date.fromisoformat(dia)
    except ValueError as erro:
        raise ErroBiblioteca("Dia inexistente no calendário.") from erro


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("É necessário fornecer um Catalogo.")
        self._catalogo = catalogo
        self._emprestimos: dict[tuple[str, str], date] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        self._catalogo.buscar(isbn)
        usuario = _validar_usuario(usuario)
        data = _validar_dia(dia)
        chave = (isbn, usuario)
        if chave in self._emprestimos:
            raise ErroBiblioteca("Usuário já possui um empréstimo ativo deste ISBN.")
        if self.disponiveis(isbn) == 0:
            raise ErroBiblioteca("Não há exemplares disponíveis.")
        self._emprestimos[chave] = data

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        self._catalogo.buscar(isbn)
        usuario = _validar_usuario(usuario)
        data = _validar_dia(dia)
        chave = (isbn, usuario)
        if chave not in self._emprestimos:
            raise ErroBiblioteca("Empréstimo ativo não encontrado.")
        inicio = self._emprestimos[chave]
        if data < inicio:
            raise ErroBiblioteca("Devolução anterior ao empréstimo.")
        # Equivale à diferença para inicio + 14 dias, sem ultrapassar date.max.
        atraso = max(0, (data - inicio).days - 14)
        del self._emprestimos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        ocupados = sum(1 for codigo, _ in self._emprestimos if codigo == isbn)
        return livro.exemplares - ocupados

    def ativos(self) -> list[tuple[str, str, str]]:
        registros = [
            (isbn, usuario, inicio.isoformat())
            for (isbn, usuario), inicio in self._emprestimos.items()
        ]
        return sorted(registros, key=lambda item: (item[2], item[0], item[1]))
