from dataclasses import dataclass
from datetime import date, timedelta
import re

from .catalogo import Catalogo
from .models import ErroBiblioteca

_DATE_REGEX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def _validar_dia(dia: str) -> date:
    if not isinstance(dia, str):
        raise ErroBiblioteca("Dia deve ser uma string no formato YYYY-MM-DD")
    if not _DATE_REGEX.fullmatch(dia):
        raise ErroBiblioteca("Formato de data inválido, esperado YYYY-MM-DD")
    try:
        d = date.fromisoformat(dia)
    except (ValueError, OverflowError) as e:
        raise ErroBiblioteca(f"Data inválida no calendário gregoriano: {dia}") from e
    if d.year < 1 or d.year > 9999:
        raise ErroBiblioteca(f"Ano fora do intervalo permitido (1 a 9999): {d.year}")
    return d


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário deve ser uma string")
    u = usuario.strip()
    if not u:
        raise ErroBiblioteca("Usuário não pode ser vazio")
    return u


@dataclass
class _Emprestimo:
    isbn: str
    usuario: str
    dia: str
    data_emprestimo: date
    data_prevista: date


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("catalogo deve ser uma instância de Catalogo")
        self.catalogo = catalogo
        self._ativos: dict[tuple[str, str], _Emprestimo] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        d_emp = _validar_dia(dia)
        u = _validar_usuario(usuario)
        livro = self.catalogo.buscar(isbn)

        chave = (isbn, u)
        if chave in self._ativos:
            raise ErroBiblioteca(f"Usuário '{u}' já possui empréstimo ativo do livro '{isbn}'")

        ativos_isbn = sum(1 for k_isbn, _ in self._ativos if k_isbn == isbn)
        if ativos_isbn >= livro.exemplares:
            raise ErroBiblioteca(f"Não há exemplares livres para o ISBN '{isbn}'")

        try:
            d_prev = d_emp + timedelta(days=14)
        except OverflowError as e:
            raise ErroBiblioteca("Data prevista de devolução excede o limite do calendário") from e

        self._ativos[chave] = _Emprestimo(
            isbn=isbn,
            usuario=u,
            dia=dia,
            data_emprestimo=d_emp,
            data_prevista=d_prev,
        )

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        d_dev = _validar_dia(dia)
        u = _validar_usuario(usuario)
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser uma string")

        chave = (isbn, u)
        if chave not in self._ativos:
            raise ErroBiblioteca("Empréstimo inexistente ou já devolvido")

        emp = self._ativos[chave]
        if d_dev < emp.data_emprestimo:
            raise ErroBiblioteca("Devolução anterior ao dia do empréstimo")

        atraso = max(0, (d_dev - emp.data_prevista).days)
        del self._ativos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self.catalogo.buscar(isbn)
        ativos_isbn = sum(1 for k_isbn, _ in self._ativos if k_isbn == isbn)
        return livro.exemplares - ativos_isbn

    def ativos(self) -> list[tuple[str, str, str]]:
        res = [
            (emp.isbn, emp.usuario, emp.dia)
            for emp in self._ativos.values()
        ]
        res.sort(key=lambda item: (item[2], item[0], item[1]))
        return res
