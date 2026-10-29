"""Catálogo de livros, sem regras de empréstimo."""

from .models import ErroBiblioteca, Livro


class Catalogo:
    """Guarda livros pelo ISBN e devolve a coleção ordenada."""

    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise ErroBiblioteca("livro invalido")
        if livro.isbn in self._livros:
            raise ErroBiblioteca("isbn duplicado")
        self._livros[livro.isbn] = livro

    def buscar(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError as exc:
            raise ErroBiblioteca("isbn desconhecido") from exc

    def listar(self) -> list[Livro]:
        return [self._livros[isbn] for isbn in sorted(self._livros)]
