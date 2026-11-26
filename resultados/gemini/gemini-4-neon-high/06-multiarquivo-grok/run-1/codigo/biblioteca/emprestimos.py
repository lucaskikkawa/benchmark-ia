from datetime import date

from .catalogo import Catalogo
from .models import ErroBiblioteca

_PRAZO_DIAS = 14


def _normalizar_usuario(usuario: str) -> str:
    if not isinstance(usuario, str):
        raise ErroBiblioteca("Usuário deve ser uma string.")
    normalizado = usuario.strip()
    if not normalizado:
        raise ErroBiblioteca("Usuário não pode ser vazio.")
    return normalizado


def _parse_dia(dia: str) -> date:
    if not isinstance(dia, str) or len(dia) != 10:
        raise ErroBiblioteca("Data deve ser uma string no formato YYYY-MM-DD.")
    if dia[4] != "-" or dia[7] != "-":
        raise ErroBiblioteca("Data deve ser uma string no formato YYYY-MM-DD.")
    ano_s, mes_s, dia_s = dia[0:4], dia[5:7], dia[8:10]
    if not all("0" <= c <= "9" for c in (ano_s + mes_s + dia_s)):
        raise ErroBiblioteca("Data deve conter apenas dígitos ASCII no formato YYYY-MM-DD.")
    try:
        return date(int(ano_s), int(mes_s), int(dia_s))
    except ValueError as exc:
        raise ErroBiblioteca(f"Data inválida: {dia!r}.") from exc


class ServicoEmprestimos:
    def __init__(self, catalogo: Catalogo) -> None:
        if not isinstance(catalogo, Catalogo):
            raise ErroBiblioteca("O catálogo deve ser uma instância de Catalogo.")
        self._catalogo = catalogo
        self._ativos_por_isbn: dict[str, dict[str, date]] = {}

    def emprestar(self, isbn: str, usuario: str, dia: str) -> None:
        livro = self._catalogo.buscar(isbn)
        usuario_norm = _normalizar_usuario(usuario)
        data_emprestimo = _parse_dia(dia)

        ativos_livro = self._ativos_por_isbn.get(isbn)
        if ativos_livro is not None:
            if usuario_norm in ativos_livro:
                raise ErroBiblioteca(
                    f"Usuário {usuario_norm!r} já possui empréstimo ativo do ISBN {isbn}."
                )
            if len(ativos_livro) >= livro.exemplares:
                raise ErroBiblioteca(f"Não há exemplares disponíveis para o ISBN {isbn}.")
            ativos_livro[usuario_norm] = data_emprestimo
        else:
            self._ativos_por_isbn[isbn] = {usuario_norm: data_emprestimo}

    def devolver(self, isbn: str, usuario: str, dia: str) -> int:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser uma string.")
        usuario_norm = _normalizar_usuario(usuario)
        data_devolucao = _parse_dia(dia)

        ativos_livro = self._ativos_por_isbn.get(isbn)
        if ativos_livro is None or usuario_norm not in ativos_livro:
            raise ErroBiblioteca(
                f"Não há empréstimo ativo do ISBN {isbn!r} para o usuário {usuario_norm!r}."
            )

        data_emprestimo = ativos_livro[usuario_norm]
        dias_decorridos = (data_devolucao - data_emprestimo).days
        if dias_decorridos < 0:
            raise ErroBiblioteca(
                "Data de devolução não pode ser anterior à data do empréstimo."
            )

        del ativos_livro[usuario_norm]
        if not ativos_livro:
            del self._ativos_por_isbn[isbn]

        return max(0, dias_decorridos - _PRAZO_DIAS)

    def disponiveis(self, isbn: str) -> int:
        livro = self._catalogo.buscar(isbn)
        ativos_livro = self._ativos_por_isbn.get(isbn)
        emprestados = len(ativos_livro) if ativos_livro is not None else 0
        return livro.exemplares - emprestados

    def ativos(self) -> list[tuple[str, str, str]]:
        resultado: list[tuple[str, str, str]] = []
        for isbn, usuarios in self._ativos_por_isbn.items():
            for usuario, data_emprestimo in usuarios.items():
                resultado.append((isbn, usuario, data_emprestimo.isoformat()))
        resultado.sort(key=lambda item: (item[2], item[0], item[1]))
        return resultado
