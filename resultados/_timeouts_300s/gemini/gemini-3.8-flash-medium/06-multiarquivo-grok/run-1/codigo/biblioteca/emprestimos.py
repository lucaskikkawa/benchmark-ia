import datetime
import re
from .catalogo import Catalogo
from .models import ErroBiblioteca


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("catalogo deve ser uma instância de Catalogo")
        self.catalogo = catalogo
        # (isbn, usuario_limpo) -> (dia_emprestimo_str, data_emprestimo_date)
        self._emprestimos_ativos: dict[tuple[str, str], tuple[str, datetime.date]] = {}

    def _validar_usuario(self, usuario: str) -> str:
        if not isinstance(usuario, str):
            raise ErroBiblioteca("Usuário deve ser string")
        usuario_limpo = usuario.strip()
        if not usuario_limpo:
            raise ErroBiblioteca("Usuário não pode ser vazio")
        return usuario_limpo

    def _validar_dia(self, dia: str) -> datetime.date:
        if not isinstance(dia, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", dia):
            raise ErroBiblioteca("Data inválida; formato deve ser YYYY-MM-DD")
        try:
            return datetime.date.fromisoformat(dia)
        except ValueError as err:
            raise ErroBiblioteca("Data inválida no calendário gregoriano") from err

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self.catalogo.buscar(isbn)
        usuario_limpo = self._validar_usuario(usuario)
        data_emp = self._validar_dia(dia)

        if (isbn, usuario_limpo) in self._emprestimos_ativos:
            raise ErroBiblioteca("Usuário já possui empréstimo ativo deste ISBN")

        ativos_isbn = sum(1 for (i, _) in self._emprestimos_ativos if i == isbn)
        if ativos_isbn >= livro.exemplares:
            raise ErroBiblioteca("Sem exemplar livre")

        self._emprestimos_ativos[(isbn, usuario_limpo)] = (dia, data_emp)

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser string")
        usuario_limpo = self._validar_usuario(usuario)
        data_dev = self._validar_dia(dia)

        if (isbn, usuario_limpo) not in self._emprestimos_ativos:
            raise ErroBiblioteca("Empréstimo inexistente ou já devolvido")

        _, data_emp = self._emprestimos_ativos[(isbn, usuario_limpo)]

        if data_dev < data_emp:
            raise ErroBiblioteca("Devolução anterior ao dia do empréstimo")

        data_prevista = data_emp + datetime.timedelta(days=14)
        atraso = max(0, (data_dev - data_prevista).days)

        del self._emprestimos_ativos[(isbn, usuario_limpo)]
        return atraso

    def disponiveis(self, isbn: str) -> int:
        livro = self.catalogo.buscar(isbn)
        ativos_isbn = sum(1 for (i, _) in self._emprestimos_ativos if i == isbn)
        return livro.exemplares - ativos_isbn

    def ativos(self) -> list[tuple[str, str, str]]:
        resultado = [
            (isbn, usuario, dia)
            for (isbn, usuario), (dia, _) in self._emprestimos_ativos.items()
        ]
        resultado.sort(key=lambda item: (item[2], item[0], item[1]))
        return resultado
