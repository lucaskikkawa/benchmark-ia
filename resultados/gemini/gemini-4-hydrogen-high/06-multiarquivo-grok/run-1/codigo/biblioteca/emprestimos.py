from __future__ import annotations

from datetime import date, timedelta

from .catalogo import Catalogo
from .models import ErroBiblioteca

PRAZO_DIAS = 14


def _validar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário deve ser uma string.")
    usuario_limpo = usuario.strip()
    if not usuario_limpo:
        raise ErroBiblioteca("Usuário não pode ser vazio.")
    return usuario_limpo


def _parse_dia(dia: str) -> date:
    if not isinstance(dia, str) or len(dia) != 10 or dia[4] != "-" or dia[7] != "-":
        raise ErroBiblioteca("Data deve estar no formato YYYY-MM-DD.")
    ano_str, mes_str, dia_str = dia[:4], dia[5:7], dia[8:10]
    if not all(
        all("0" <= c <= "9" for c in parte) for parte in (ano_str, mes_str, dia_str)
    ):
        raise ErroBiblioteca("Data deve conter apenas dígitos ASCII em YYYY-MM-DD.")
    try:
        return date(int(ano_str), int(mes_str), int(dia_str))
    except ValueError as exc:
        raise ErroBiblioteca(f"Data inválida no calendário gregoriano: {dia}") from exc


class ServicoEmprestimos:
    """Gerencia empréstimos e devoluções sobre um catálogo sem alterar o catálogo."""

    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("O catálogo deve ser uma instância de Catalogo.")
        self._catalogo = catalogo
        self._ativos: dict[tuple[str, str], tuple[date, str]] = {}

    def _contar_ativos(self, isbn: str) -> int:
        return sum(1 for isbn_ativo, _ in self._ativos if isbn_ativo == isbn)

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        """Registra um empréstimo ativo se houver exemplar livre e usuário elegível."""
        livro = self._catalogo.buscar(isbn)
        usuario_limpo = _validar_usuario(usuario)
        data_emprestimo = _parse_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave in self._ativos:
            raise ErroBiblioteca(
                f"Usuário {usuario_limpo!r} já possui empréstimo ativo do ISBN {isbn}."
            )
        if livro.exemplares - self._contar_ativos(isbn) <= 0:
            raise ErroBiblioteca(f"Sem exemplares disponíveis para o ISBN {isbn}.")

        self._ativos[chave] = (data_emprestimo, dia)

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        """Conclui um empréstimo ativo e retorna os dias de atraso."""
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser uma string.")
        usuario_limpo = _validar_usuario(usuario)
        data_devolucao = _parse_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave not in self._ativos:
            raise ErroBiblioteca("Empréstimo inexistente ou já devolvido.")

        data_emprestimo, _ = self._ativos[chave]
        if data_devolucao < data_emprestimo:
            raise ErroBiblioteca("Data de devolução não pode ser anterior ao empréstimo.")

        del self._ativos[chave]
        data_prevista = data_emprestimo + timedelta(days=PRAZO_DIAS)
        return max(0, (data_devolucao - data_prevista).days)

    def disponiveis(self, isbn: str) -> int:
        """Retorna a quantidade de exemplares livres deste serviço para o ISBN."""
        livro = self._catalogo.buscar(isbn)
        return livro.exemplares - self._contar_ativos(isbn)

    def ativos(self) -> list[tuple[str, str, str]]:
        """Lista empréstimos ativos como (isbn, usuario, dia) ordenados."""
        itens = [
            (isbn, usuario, dia_str)
            for (isbn, usuario), (_, dia_str) in self._ativos.items()
        ]
        return sorted(itens, key=lambda item: (item[2], item[0], item[1]))
