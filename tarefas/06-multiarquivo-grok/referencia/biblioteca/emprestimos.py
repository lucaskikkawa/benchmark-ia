"""Empréstimos em cima de um Catalogo."""

from datetime import date, timedelta

from .catalogo import Catalogo
from .models import ErroBiblioteca

_PRAZO_DIAS = 14


class ServicoEmprestimos:
    """Empresta, devolve e informa o estoque livre."""

    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("catalogo invalido")
        self._catalogo = catalogo
        self._ativos: dict[tuple[str, str], date] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        self._catalogo.buscar(isbn)
        nome = _usuario(usuario)
        quando = _dia(dia)
        if (isbn, nome) in self._ativos:
            raise ErroBiblioteca("emprestimo duplicado")
        if self.disponiveis(isbn) < 1:
            raise ErroBiblioteca("sem exemplar")
        self._ativos[(isbn, nome)] = quando

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        nome = _usuario(usuario)
        quando = _dia(dia)
        chave = (isbn, nome)
        if chave not in self._ativos:
            raise ErroBiblioteca("emprestimo inexistente")
        inicio = self._ativos[chave]
        if quando < inicio:
            raise ErroBiblioteca("data anterior ao emprestimo")
        previsto = inicio + timedelta(days=_PRAZO_DIAS)
        del self._ativos[chave]
        return max(0, (quando - previsto).days)

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        usados = sum(1 for item, _nome in self._ativos if item == isbn)
        return livro.exemplares - usados

    def ativos(self) -> list[tuple[str, str, str]]:
        linhas = [
            (quando.isoformat(), isbn, usuario)
            for (isbn, usuario), quando in self._ativos.items()
        ]
        linhas.sort()
        return [(isbn, usuario, quando) for quando, isbn, usuario in linhas]


def _usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("usuario invalido")
    nome = usuario.strip()
    if not nome:
        raise ErroBiblioteca("usuario invalido")
    return nome


def _dia(texto: str) -> date:
    if not isinstance(texto, str) or len(texto) != 10:
        raise ErroBiblioteca("data invalida")
    try:
        convertido = date.fromisoformat(texto)
    except ValueError as exc:
        raise ErroBiblioteca("data invalida") from exc
    if convertido.isoformat() != texto:
        raise ErroBiblioteca("data invalida")
    return convertido
