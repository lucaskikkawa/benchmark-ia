import re
from datetime import date, timedelta

from .catalogo import Catalogo
from .models import ErroBiblioteca

PRAZO = timedelta(days=14)
_FORMATO_DIA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("usuário inválido")
    usuario = usuario.strip()
    if not usuario:
        raise ErroBiblioteca("usuário vazio")
    return usuario


def _validar_dia(dia: str) -> date:
    if not isinstance(dia, str) or not _FORMATO_DIA.fullmatch(dia):
        raise ErroBiblioteca("dia inválido")
    try:
        return date(int(dia[0:4]), int(dia[5:7]), int(dia[8:10]))
    except ValueError:
        raise ErroBiblioteca("dia inválido") from None


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("esperado um Catalogo")
        self.catalogo = catalogo
        self._ativos: dict[tuple[str, str], date] = {}

    def _emprestados(self, isbn: str) -> int:
        return sum(1 for (i, _) in self._ativos if i == isbn)

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self.catalogo.buscar(isbn)
        usuario = _validar_usuario(usuario)
        data = _validar_dia(dia)
        chave = (isbn, usuario)
        if chave in self._ativos:
            raise ErroBiblioteca("usuário já tem este livro emprestado")
        if livro.exemplares - self._emprestados(isbn) <= 0:
            raise ErroBiblioteca("sem exemplar disponível")
        self._ativos[chave] = data

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        usuario = _validar_usuario(usuario)
        data = _validar_dia(dia)
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN inválido")
        chave = (isbn, usuario)
        if chave not in self._ativos:
            raise ErroBiblioteca("empréstimo inexistente")
        inicio = self._ativos[chave]
        if data < inicio:
            raise ErroBiblioteca("devolução anterior ao empréstimo")
        del self._ativos[chave]
        # Equivale a (data - (inicio + PRAZO)).days sem estourar em 9999-12-31.
        return max(0, (data - inicio).days - PRAZO.days)

    def disponiveis(self, isbn: str) -> int:
        livro = self.catalogo.buscar(isbn)
        return livro.exemplares - self._emprestados(isbn)

    def ativos(self) -> list[tuple[str, str, str]]:
        ordenados = sorted(
            (inicio.isoformat(), isbn, usuario)
            for (isbn, usuario), inicio in self._ativos.items()
        )
        return [(isbn, usuario, dia) for dia, isbn, usuario in ordenados]
