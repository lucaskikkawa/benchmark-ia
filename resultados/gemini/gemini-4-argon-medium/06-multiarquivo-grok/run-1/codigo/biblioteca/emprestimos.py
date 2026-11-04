from datetime import date

from .catalogo import Catalogo
from .models import ErroBiblioteca


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário inválido: deve ser uma string.")
    limpo = usuario.strip()
    if not limpo:
        raise ErroBiblioteca("Usuário inválido: não pode ser vazio.")
    return limpo


def _validar_dia(dia: str) -> date:
    if (
        not isinstance(dia, str)
        or len(dia) != 10
        or dia[4] != "-"
        or dia[7] != "-"
        or not (dia[:4].isascii() and dia[:4].isdigit())
        or not (dia[5:7].isascii() and dia[5:7].isdigit())
        or not (dia[8:10].isascii() and dia[8:10].isdigit())
    ):
        raise ErroBiblioteca(f"Data inválida: {dia!r}")
    ano = int(dia[:4])
    mes = int(dia[5:7])
    dia_mes = int(dia[8:10])
    try:
        return date(ano, mes, dia_mes)
    except ValueError as exc:
        raise ErroBiblioteca(f"Data inexistente no calendário: {dia!r}") from exc


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("O catálogo deve ser uma instância de Catalogo.")
        self.catalogo: Catalogo = catalogo
        self._ativos: dict[tuple[str, str], date] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self.catalogo.buscar(isbn)
        usuario_limpo = _validar_usuario(usuario)
        data_emprestimo = _validar_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave in self._ativos:
            raise ErroBiblioteca("Usuário já possui empréstimo ativo para este ISBN.")

        em_uso = sum(1 for k_isbn, _ in self._ativos if k_isbn == isbn)
        if em_uso >= livro.exemplares:
            raise ErroBiblioteca("Não há exemplares disponíveis para este ISBN.")

        self._ativos[chave] = data_emprestimo

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN inválido.")
        usuario_limpo = _validar_usuario(usuario)
        data_devolucao = _validar_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave not in self._ativos:
            raise ErroBiblioteca("Empréstimo ativo não encontrado.")

        data_emprestimo = self._ativos[chave]
        if data_devolucao < data_emprestimo:
            raise ErroBiblioteca("Data de devolução anterior à data do empréstimo.")

        del self._ativos[chave]
        return max(0, (data_devolucao - data_emprestimo).days - 14)

    def disponiveis(self, isbn: str) -> int:
        livro = self.catalogo.buscar(isbn)
        em_uso = sum(1 for k_isbn, _ in self._ativos if k_isbn == isbn)
        return livro.exemplares - em_uso

    def ativos(self) -> list[tuple[str, str, str]]:
        lista = [
            (isbn, usuario, data_emp.isoformat())
            for (isbn, usuario), data_emp in self._ativos.items()
        ]
        lista.sort(key=lambda item: (item[2], item[0], item[1]))
        return lista
