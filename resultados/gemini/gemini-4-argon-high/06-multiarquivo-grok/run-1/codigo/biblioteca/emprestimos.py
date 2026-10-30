from datetime import date

from .catalogo import Catalogo
from .models import ErroBiblioteca

PRAZO_EMPRESTIMO_DIAS = 14


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário deve ser uma string.")
    usuario_limpo = usuario.strip()
    if not usuario_limpo:
        raise ErroBiblioteca("Usuário não pode ser vazio.")
    return usuario_limpo


def _validar_dia(dia: str) -> date:
    if (
        not isinstance(dia, str)
        or len(dia) != 10
        or dia[4] != "-"
        or dia[7] != "-"
        or not all("0" <= c <= "9" for c in (dia[:4] + dia[5:7] + dia[8:10]))
    ):
        raise ErroBiblioteca("Data deve estar no formato YYYY-MM-DD.")
    ano = int(dia[:4])
    mes = int(dia[5:7])
    dia_mes = int(dia[8:10])
    try:
        return date(ano, mes, dia_mes)
    except ValueError as exc:
        raise ErroBiblioteca("Data inválida no calendário gregoriano.") from exc


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("O catálogo deve ser uma instância de Catalogo.")
        self.catalogo = catalogo
        self._ativos: dict[tuple[str, str], date] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self.catalogo.buscar(isbn)
        usuario_limpo = _validar_usuario(usuario)
        data_emprestimo = _validar_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave in self._ativos:
            raise ErroBiblioteca("O usuário já possui um empréstimo ativo deste ISBN.")

        emprestados = sum(1 for isbn_ativo, _ in self._ativos if isbn_ativo == isbn)
        if emprestados >= livro.exemplares:
            raise ErroBiblioteca("Não há exemplares disponíveis para empréstimo.")

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
            raise ErroBiblioteca("A data de devolução não pode ser anterior à data do empréstimo.")

        del self._ativos[chave]
        atraso = (data_devolucao - data_emprestimo).days - PRAZO_EMPRESTIMO_DIAS
        return max(0, atraso)

    def disponiveis(self, isbn: str) -> int:
        livro = self.catalogo.buscar(isbn)
        emprestados = sum(1 for isbn_ativo, _ in self._ativos if isbn_ativo == isbn)
        return livro.exemplares - emprestados

    def ativos(self) -> list[tuple[str, str, str]]:
        lista = [
            (isbn, usuario, data_emp.isoformat())
            for (isbn, usuario), data_emp in self._ativos.items()
        ]
        lista.sort(key=lambda item: (item[2], item[0], item[1]))
        return lista
