from datetime import date

from .catalogo import Catalogo
from .models import ErroBiblioteca

PRAZO_DIAS = 14


def _normalizar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário deve ser uma string.")
    usuario_limpo = usuario.strip()
    if not usuario_limpo:
        raise ErroBiblioteca("Usuário não pode ser vazio.")
    return usuario_limpo


def _parse_dia(dia: str) -> date:
    if (
        not isinstance(dia, str)
        or len(dia) != 10
        or dia[4] != "-"
        or dia[7] != "-"
        or not all("0" <= ch <= "9" for ch in dia[:4] + dia[5:7] + dia[8:10])
    ):
        raise ErroBiblioteca(f"Data inválida (esperado YYYY-MM-DD): {dia!r}")
    try:
        return date(int(dia[:4]), int(dia[5:7]), int(dia[8:10]))
    except ValueError as exc:
        raise ErroBiblioteca(f"Data inexistente no calendário gregoriano: {dia!r}") from exc


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("É necessário fornecer uma instância de Catalogo.")
        self._catalogo = catalogo
        self._emprestimos: dict[tuple[str, str], date] = {}

    def _ativos_por_isbn(self, isbn: str) -> int:
        return sum(1 for emprestimo_isbn, _ in self._emprestimos if emprestimo_isbn == isbn)

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        usuario_limpo = _normalizar_usuario(usuario)
        data_emprestimo = _parse_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave in self._emprestimos:
            raise ErroBiblioteca(
                f"Usuário {usuario_limpo!r} já possui empréstimo ativo para o ISBN {isbn}."
            )

        if livro.exemplares - self._ativos_por_isbn(isbn) <= 0:
            raise ErroBiblioteca(f"Não há exemplares disponíveis para o ISBN {isbn}.")

        self._emprestimos[chave] = data_emprestimo

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        if not isinstance(isbn, str):
            raise ErroBiblioteca(f"ISBN inválido: {isbn!r}")
        usuario_limpo = _normalizar_usuario(usuario)
        data_devolucao = _parse_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave not in self._emprestimos:
            raise ErroBiblioteca(
                f"Não há empréstimo ativo do ISBN {isbn} para o usuário {usuario_limpo!r}."
            )

        data_emprestimo = self._emprestimos[chave]
        if data_devolucao < data_emprestimo:
            raise ErroBiblioteca("A data de devolução não pode ser anterior à data do empréstimo.")

        atraso = max(0, (data_devolucao - data_emprestimo).days - PRAZO_DIAS)
        del self._emprestimos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        return livro.exemplares - self._ativos_por_isbn(isbn)

    def ativos(self) -> list[tuple[str, str, str]]:
        return sorted(
            (
                (isbn, usuario, data.isoformat())
                for (isbn, usuario), data in self._emprestimos.items()
            ),
            key=lambda item: (item[2], item[0], item[1]),
        )
