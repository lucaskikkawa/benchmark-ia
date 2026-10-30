import re
from datetime import date, timedelta

from .catalogo import Catalogo
from .models import ErroBiblioteca

PRAZO_DIAS = 14
_PADRAO_DIA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("usuário deve ser string")
    nome = usuario.strip()
    if not nome:
        raise ErroBiblioteca("usuário não pode ser vazio")
    return nome


def _validar_dia(dia: str) -> date:
    if not isinstance(dia, str) or not _PADRAO_DIA.fullmatch(dia):
        raise ErroBiblioteca(f"dia inválido: {dia!r}")
    try:
        return date.fromisoformat(dia)
    except ValueError as erro:
        raise ErroBiblioteca(f"dia inválido: {dia!r}") from erro


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise TypeError("o serviço exige um Catalogo")
        self._catalogo = catalogo
        # (isbn, usuario) -> dia do empréstimo; só empréstimos ativos
        self._ativos: dict[tuple[str, str], date] = {}

    def _emprestados(self, isbn: str) -> int:
        return sum(1 for chave in self._ativos if chave[0] == isbn)

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        nome = _validar_usuario(usuario)
        data = _validar_dia(dia)
        if (isbn, nome) in self._ativos:
            raise ErroBiblioteca("usuário já tem empréstimo ativo deste ISBN")
        if livro.exemplares - self._emprestados(isbn) < 1:
            raise ErroBiblioteca("sem exemplar disponível")
        self._ativos[(isbn, nome)] = data

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        nome = _validar_usuario(usuario)
        data = _validar_dia(dia)
        if not isinstance(isbn, str) or (isbn, nome) not in self._ativos:
            raise ErroBiblioteca("empréstimo inexistente")
        inicio = self._ativos[(isbn, nome)]
        if data < inicio:
            raise ErroBiblioteca("devolução anterior ao empréstimo")
        # (devolucao - (inicio + prazo)).days, sem somar o prazo para não estourar date
        atraso = max(0, (data - inicio).days - PRAZO_DIAS)
        del self._ativos[(isbn, nome)]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        return livro.exemplares - self._emprestados(isbn)

    def ativos(self) -> list[tuple[str, str, str]]:
        ordenados = sorted(
            self._ativos.items(),
            key=lambda item: (item[1], item[0][0], item[0][1]),
        )
        return [(isbn, usuario, data.isoformat()) for (isbn, usuario), data in ordenados]
