import datetime
import re

from .catalogo import Catalogo
from .models import ErroBiblioteca


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("catalogo deve ser uma instância de Catalogo")
        self.catalogo = catalogo
        self._catalogo = catalogo
        self._emprestimos_ativos: dict[tuple[str, str], tuple[str, datetime.date]] = {}

    @staticmethod
    def _validar_dia(dia: str) -> datetime.date:
        if not isinstance(dia, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", dia):
            raise ErroBiblioteca(f"Formato de data inválido: {dia!r}")
        try:
            data = datetime.date.fromisoformat(dia)
        except ValueError as exc:
            raise ErroBiblioteca(f"Data inválida no calendário gregoriano: {dia!r}") from exc
        return data

    @staticmethod
    def _validar_usuario(usuario: str) -> str:
        if not isinstance(usuario, str):
            raise ErroBiblioteca("usuario deve ser string")
        usuario_limpo = usuario.strip()
        if not usuario_limpo:
            raise ErroBiblioteca("usuario não pode ser vazio")
        return usuario_limpo

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        usuario_limpo = self._validar_usuario(usuario)
        data_emp = self._validar_dia(dia)
        livro = self._catalogo.buscar(isbn)

        chave = (isbn, usuario_limpo)
        if chave in self._emprestimos_ativos:
            raise ErroBiblioteca(f"Usuário {usuario_limpo!r} já possui empréstimo ativo do ISBN {isbn}")

        ativos_count = sum(1 for (i, _) in self._emprestimos_ativos if i == isbn)
        if livro.exemplares - ativos_count <= 0:
            raise ErroBiblioteca(f"Não há exemplares disponíveis do livro {isbn}")

        self._emprestimos_ativos[chave] = (dia, data_emp)

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        usuario_limpo = self._validar_usuario(usuario)
        data_dev = self._validar_dia(dia)

        chave = (isbn, usuario_limpo)
        if chave not in self._emprestimos_ativos:
            raise ErroBiblioteca(f"Empréstimo não encontrado ou já devolvido para ISBN {isbn} e usuário {usuario_limpo!r}")

        dia_emp_str, data_emp = self._emprestimos_ativos[chave]
        if data_dev < data_emp:
            raise ErroBiblioteca("Devolução anterior ao dia do empréstimo")

        dias_decorridos = (data_dev - data_emp).days
        atraso = max(0, dias_decorridos - 14)

        del self._emprestimos_ativos[chave]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        ativos_count = sum(1 for (i, _) in self._emprestimos_ativos if i == isbn)
        return livro.exemplares - ativos_count

    def ativos(self) -> list[tuple[str, str, str]]:
        itens = [
            (isbn, usuario, dia_str)
            for (isbn, usuario), (dia_str, _) in self._emprestimos_ativos.items()
        ]
        return sorted(itens, key=lambda item: (item[2], item[0], item[1]))
