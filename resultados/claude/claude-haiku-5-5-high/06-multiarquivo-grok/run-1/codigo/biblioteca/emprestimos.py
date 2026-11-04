import re
from datetime import date

from .catalogo import Catalogo
from .models import ErroBiblioteca, Livro

PRAZO_DIAS = 14
_FORMATO_DIA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _ler_dia(dia: str) -> date:
    if not isinstance(dia, str) or not _FORMATO_DIA.fullmatch(dia):
        raise ErroBiblioteca(f"dia inválido: {dia!r}")
    try:
        return date.fromisoformat(dia)
    except ValueError as erro:
        raise ErroBiblioteca(f"dia inexistente: {dia!r}") from erro


def _ler_usuario(usuario: str) -> str:
    if not isinstance(usuario, str) or not usuario.strip():
        raise ErroBiblioteca(f"usuário inválido: {usuario!r}")
    return usuario.strip()


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("o serviço exige um Catalogo")
        self._catalogo = catalogo
        self._ativos: dict[tuple[str, str], date] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        usuario = _ler_usuario(usuario)
        data = _ler_dia(dia)
        if (isbn, usuario) in self._ativos:
            raise ErroBiblioteca(f"{usuario!r} já tem empréstimo ativo de {isbn}")
        if self._livres(livro) <= 0:
            raise ErroBiblioteca(f"sem exemplar disponível para {isbn}")
        self._ativos[(isbn, usuario)] = data

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        usuario = _ler_usuario(usuario)
        devolucao = _ler_dia(dia)
        emprestimo = self._ativos.get((isbn, usuario)) if isinstance(isbn, str) else None
        if emprestimo is None:
            raise ErroBiblioteca(f"empréstimo inexistente: {isbn!r}, {usuario!r}")
        if devolucao < emprestimo:
            raise ErroBiblioteca("devolução anterior ao dia do empréstimo")
        del self._ativos[(isbn, usuario)]
        # ordinal evita estouro de date quando o prazo passa de 9999-12-31
        return max(0, devolucao.toordinal() - emprestimo.toordinal() - PRAZO_DIAS)

    def disponiveis(self, isbn: str) -> int:
        return self._livres(self._catalogo.buscar(isbn))

    def ativos(self) -> list[tuple[str, str, str]]:
        itens = sorted(self._ativos.items(), key=lambda item: (item[1], item[0][0], item[0][1]))
        return [(isbn, usuario, dia.isoformat()) for (isbn, usuario), dia in itens]

    def _livres(self, livro: Livro) -> int:
        emprestados = sum(1 for isbn, _ in self._ativos if isbn == livro.isbn)
        return livro.exemplares - emprestados
