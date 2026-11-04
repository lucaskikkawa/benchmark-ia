from datetime import date, timedelta
import re

from .catalogo import Catalogo
from .models import ErroBiblioteca

_DATA_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


def _validar_dia(dia: str) -> date:
    if not isinstance(dia, str) or _DATA_RE.fullmatch(dia) is None:
        raise ErroBiblioteca("Data deve estar no formato YYYY-MM-DD.")
    try:
        return date.fromisoformat(dia)
    except ValueError:
        raise ErroBiblioteca("Data inválida.") from None


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("É necessário fornecer uma instância de Catalogo.")
        self._catalogo = catalogo
        # Cada registro é (ISBN, usuário normalizado) -> (dia emprestado, devolvido)
        self._emprestimos: dict[tuple[str, str], tuple[date, bool]] = {}

    @staticmethod
    def _usuario(usuario: str) -> str:
        if not isinstance(usuario, str):
            raise ErroBiblioteca("Usuário deve ser uma string.")
        usuario = usuario.strip()
        if not usuario:
            raise ErroBiblioteca("Usuário não pode ficar vazio.")
        return usuario

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        nome = self._usuario(usuario)
        data = _validar_dia(dia)
        chave = (isbn, nome)
        registro = self._emprestimos.get(chave)
        if registro is not None and not registro[1]:
            raise ErroBiblioteca("Esse usuário já tem esse livro emprestado.")
        if self.disponiveis(isbn) <= 0:
            raise ErroBiblioteca("Não há exemplares disponíveis.")
        self._emprestimos[chave] = (data, False)

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        nome = self._usuario(usuario)
        data_devolucao = _validar_dia(dia)
        chave = (isbn, nome)
        registro = self._emprestimos.get(chave)
        if registro is None or registro[1]:
            raise ErroBiblioteca("Empréstimo ativo não encontrado.")
        data_emprestimo = registro[0]
        if data_devolucao < data_emprestimo:
            raise ErroBiblioteca("A devolução não pode preceder o empréstimo.")
        atraso = max(0, (data_devolucao - (data_emprestimo + timedelta(days=14))).days)
        self._emprestimos[chave] = (data_emprestimo, True)
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        ativos = sum(
            1
            for (isbn_emprestimo, _), (_, devolvido) in self._emprestimos.items()
            if isbn_emprestimo == isbn and not devolvido
        )
        return livro.exemplares - ativos

    def ativos(self) -> list[tuple[str, str, str]]:
        registros = [
            (isbn, usuario, dia.isoformat())
            for (isbn, usuario), (dia, devolvido) in self._emprestimos.items()
            if not devolvido
        ]
        return sorted(registros, key=lambda registro: (registro[2], registro[0], registro[1]))
