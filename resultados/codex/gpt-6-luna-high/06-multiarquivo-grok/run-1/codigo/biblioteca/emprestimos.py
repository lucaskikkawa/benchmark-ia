from datetime import date, timedelta
import re

from .catalogo import Catalogo
from .models import ErroBiblioteca


_FORMATO_DIA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _parse_dia(dia: str) -> date:
    if not isinstance(dia, str) or _FORMATO_DIA.fullmatch(dia) is None:
        raise ErroBiblioteca("Dia deve estar no formato YYYY-MM-DD")
    try:
        ano, mes, dia_mes = (int(parte) for parte in dia.split("-"))
        return date(ano, mes, dia_mes)
    except ValueError:
        raise ErroBiblioteca("Dia não é uma data válida") from None


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("É necessário fornecer uma instância de Catalogo")
        self._catalogo = catalogo
        # Chaveia por ISBN e usuário já normalizado; o valor é a data do empréstimo.
        self._emprestimos: dict[tuple[str, str], date] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        if not isinstance(usuario, str):
            raise ErroBiblioteca("Usuário deve ser uma string")
        usuario_normalizado = usuario.strip()
        if not usuario_normalizado:
            raise ErroBiblioteca("Usuário não pode ser vazio")
        data_emprestimo = _parse_dia(dia)
        chave = (isbn, usuario_normalizado)
        if chave in self._emprestimos:
            raise ErroBiblioteca("Usuário já tem este livro emprestado")
        if self.disponiveis(isbn) < 1:
            raise ErroBiblioteca("Não há exemplares disponíveis")
        try:
            data_emprestimo + timedelta(days=14)
        except OverflowError:
            raise ErroBiblioteca("Data prevista ultrapassa o calendário suportado") from None
        self._emprestimos[chave] = data_emprestimo

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        if not isinstance(usuario, str):
            raise ErroBiblioteca("Usuário deve ser uma string")
        usuario_normalizado = usuario.strip()
        if not usuario_normalizado:
            raise ErroBiblioteca("Usuário não pode ser vazio")
        data_devolucao = _parse_dia(dia)
        chave = (isbn, usuario_normalizado)
        try:
            data_emprestimo = self._emprestimos.get(chave)
        except TypeError:
            raise ErroBiblioteca("Empréstimo ativo não encontrado") from None
        if data_emprestimo is None:
            raise ErroBiblioteca("Empréstimo ativo não encontrado")
        if data_devolucao < data_emprestimo:
            raise ErroBiblioteca("Devolução não pode anteceder o empréstimo")
        data_prevista = data_emprestimo + timedelta(days=14)
        atraso = max(0, (data_devolucao - data_prevista).days)
        del self._emprestimos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        emprestados = sum(1 for (isbn_ativo, _), _dia in self._emprestimos.items() if isbn_ativo == isbn)
        return livro.exemplares - emprestados

    def ativos(self) -> list[tuple[str, str, str]]:
        ativos = [(isbn, usuario, dia.isoformat()) for (isbn, usuario), dia in self._emprestimos.items()]
        return sorted(ativos, key=lambda emprestimo: (emprestimo[2], emprestimo[0], emprestimo[1]))
