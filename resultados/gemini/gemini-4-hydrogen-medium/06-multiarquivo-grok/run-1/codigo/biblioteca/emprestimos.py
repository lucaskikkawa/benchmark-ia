from datetime import date, timedelta

from .catalogo import Catalogo
from .models import ErroBiblioteca


def _normalizar_usuario(usuario: object) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário deve ser uma string.")
    usuario_limpo = usuario.strip()
    if not usuario_limpo:
        raise ErroBiblioteca("Usuário não pode ser vazio.")
    return usuario_limpo


def _parse_dia(dia: object) -> tuple[date, str]:
    if (
        not isinstance(dia, str)
        or len(dia) != 10
        or dia[4] != "-"
        or dia[7] != "-"
        or not all("0" <= c <= "9" for c in (dia[:4] + dia[5:7] + dia[8:10]))
    ):
        raise ErroBiblioteca("Data deve estar no formato YYYY-MM-DD.")
    try:
        data = date(int(dia[:4]), int(dia[5:7]), int(dia[8:10]))
    except ValueError as exc:
        raise ErroBiblioteca(f"Data inválida: {dia}") from exc
    return data, dia


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("Serviço exige uma instância de Catalogo.")
        self._catalogo = catalogo
        self._emprestimos: dict[tuple[str, str], tuple[date, str]] = {}

    def _ativos_por_isbn(self, isbn: str) -> int:
        return sum(1 for (emp_isbn, _) in self._emprestimos if emp_isbn == isbn)

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        usuario_limpo = _normalizar_usuario(usuario)
        data_emprestimo, dia_str = _parse_dia(dia)

        chave = (livro.isbn, usuario_limpo)
        if chave in self._emprestimos:
            raise ErroBiblioteca("Usuário já possui empréstimo ativo deste livro.")

        if self._ativos_por_isbn(livro.isbn) >= livro.exemplares:
            raise ErroBiblioteca("Não há exemplares disponíveis para empréstimo.")

        self._emprestimos[chave] = (data_emprestimo, dia_str)

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN inválido.")
        usuario_limpo = _normalizar_usuario(usuario)
        data_devolucao, _ = _parse_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave not in self._emprestimos:
            raise ErroBiblioteca("Empréstimo ativo não encontrado.")

        data_emprestimo, _ = self._emprestimos[chave]
        if data_devolucao < data_emprestimo:
            raise ErroBiblioteca("Data de devolução anterior à data de empréstimo.")

        data_prevista = data_emprestimo + timedelta(days=14)
        atraso = max(0, (data_devolucao - data_prevista).days)
        del self._emprestimos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        return livro.exemplares - self._ativos_por_isbn(livro.isbn)

    def ativos(self) -> list[tuple[str, str, str]]:
        itens = [(isbn, usuario, dia_str) for (isbn, usuario), (_, dia_str) in self._emprestimos.items()]
        itens.sort(key=lambda item: (item[2], item[0], item[1]))
        return itens
