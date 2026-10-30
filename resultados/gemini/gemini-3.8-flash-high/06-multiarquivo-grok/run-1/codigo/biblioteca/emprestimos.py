from dataclasses import dataclass
from datetime import date, timedelta
import re

from .catalogo import Catalogo
from .models import ErroBiblioteca


@dataclass
class _Emprestimo:
    isbn: str
    usuario: str
    dia_str: str
    data_emprestimo: date
    data_prevista: date


def _validar_dia(dia: str) -> date:
    if not isinstance(dia, str):
        raise ErroBiblioteca("Dia deve ser string")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dia):
        raise ErroBiblioteca(f"Data deve estar no formato YYYY-MM-DD: {dia!r}")
    try:
        d = date.fromisoformat(dia)
    except (ValueError, OverflowError) as exc:
        raise ErroBiblioteca(f"Data inválida no calendário gregoriano: {dia!r}") from exc
    if not (1 <= d.year <= 9999):
        raise ErroBiblioteca(f"Ano fora do intervalo 1 a 9999: {dia!r}")
    return d


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário deve ser string")
    usuario_limpo = usuario.strip()
    if not usuario_limpo:
        raise ErroBiblioteca("Usuário não pode ser vazio")
    return usuario_limpo


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("catalogo deve ser uma instância de Catalogo")
        self.catalogo = catalogo
        self._emprestimos_ativos: dict[tuple[str, str], _Emprestimo] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser string")
        usuario_limpo = _validar_usuario(usuario)
        data_emp = _validar_dia(dia)

        livro = self.catalogo.buscar(isbn)

        chave = (isbn, usuario_limpo)
        if chave in self._emprestimos_ativos:
            raise ErroBiblioteca(
                f"Usuário {usuario_limpo!r} já possui empréstimo ativo do livro {isbn!r}"
            )

        ativos_deste_isbn = sum(
            1 for (k_isbn, _) in self._emprestimos_ativos if k_isbn == isbn
        )
        if livro.exemplares - ativos_deste_isbn <= 0:
            raise ErroBiblioteca(
                f"Não há exemplares livres para o livro {isbn!r}"
            )

        try:
            data_prevista = data_emp + timedelta(days=14)
        except OverflowError as exc:
            raise ErroBiblioteca(
                f"Data prevista excede limite do calendário: {exc}"
            ) from exc

        self._emprestimos_ativos[chave] = _Emprestimo(
            isbn=isbn,
            usuario=usuario_limpo,
            dia_str=dia,
            data_emprestimo=data_emp,
            data_prevista=data_prevista,
        )

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser string")
        usuario_limpo = _validar_usuario(usuario)
        data_dev = _validar_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave not in self._emprestimos_ativos:
            raise ErroBiblioteca(
                f"Empréstimo inexistente ou já devolvido para ISBN {isbn!r} e usuário {usuario_limpo!r}"
            )

        emprestimo = self._emprestimos_ativos[chave]
        if data_dev < emprestimo.data_emprestimo:
            raise ErroBiblioteca(
                f"Data de devolução ({dia}) anterior à data de empréstimo ({emprestimo.dia_str})"
            )

        atraso = max(0, (data_dev - emprestimo.data_prevista).days)
        del self._emprestimos_ativos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self.catalogo.buscar(isbn)
        ativos_deste_isbn = sum(
            1 for (k_isbn, _) in self._emprestimos_ativos if k_isbn == isbn
        )
        return livro.exemplares - ativos_deste_isbn

    def ativos(self) -> list[tuple[str, str, str]]:
        itens = [
            (emp.isbn, emp.usuario, emp.dia_str)
            for emp in self._emprestimos_ativos.values()
        ]
        return sorted(itens, key=lambda t: (t[2], t[0], t[1]))
