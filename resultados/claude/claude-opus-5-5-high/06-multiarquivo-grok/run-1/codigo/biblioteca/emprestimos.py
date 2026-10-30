import re
from datetime import date

from .catalogo import Catalogo
from .models import ErroBiblioteca

_DIA_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
PRAZO_DIAS = 14


def _parse_dia(dia: str) -> date:
    if not isinstance(dia, str):
        raise ErroBiblioteca("dia deve ser string YYYY-MM-DD")
    m = _DIA_RE.fullmatch(dia)
    if not m:
        raise ErroBiblioteca(f"dia inválido: {dia!r}")
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        raise ErroBiblioteca(f"dia inexistente: {dia!r}") from None


def _normalizar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("usuário deve ser string")
    usuario = usuario.strip()
    if not usuario:
        raise ErroBiblioteca("usuário vazio")
    return usuario


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("esperado um Catalogo")
        self._catalogo = catalogo
        # (isbn, usuario) -> dia do empréstimo
        self._ativos: dict[tuple[str, str], date] = {}

    def _em_uso(self, isbn: str) -> int:
        return sum(1 for (i, _u) in self._ativos if i == isbn)

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        usuario = _normalizar_usuario(usuario)
        data = _parse_dia(dia)
        if (isbn, usuario) in self._ativos:
            raise ErroBiblioteca("usuário já tem empréstimo ativo deste livro")
        if livro.exemplares - self._em_uso(isbn) <= 0:
            raise ErroBiblioteca("sem exemplar disponível")
        self._ativos[(isbn, usuario)] = data

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        self._catalogo.buscar(isbn)
        usuario = _normalizar_usuario(usuario)
        data = _parse_dia(dia)
        chave = (isbn, usuario)
        if chave not in self._ativos:
            raise ErroBiblioteca("empréstimo inexistente")
        inicio = self._ativos[chave]
        decorridos = (data - inicio).days
        if decorridos < 0:
            raise ErroBiblioteca("devolução anterior ao empréstimo")
        del self._ativos[chave]
        # equivale a (data - (inicio + 14 dias)).days, sem estourar date.max
        return max(0, decorridos - PRAZO_DIAS)

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        return livro.exemplares - self._em_uso(isbn)

    def ativos(self) -> list[tuple[str, str, str]]:
        return sorted(
            ((isbn, usuario, dia.isoformat()) for (isbn, usuario), dia in self._ativos.items()),
            key=lambda t: (t[2], t[0], t[1]),
        )
