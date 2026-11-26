from __future__ import annotations

from .models import ErroBiblioteca, Livro


class Catalogo:
    """Armazena e consulta livros indexados exatamente pelo ISBN."""

    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        """Adiciona um livro ao catálogo, rejeitando duplicidade de ISBN."""
        if not isinstance(livro, Livro):
            raise ErroBiblioteca("O item adicionado deve ser uma instância de Livro.")
        if livro.isbn in self._livros:
            raise ErroBiblioteca(f"ISBN já cadastrado no catálogo: {livro.isbn}")
        self._livros[livro.isbn] = livro

    def buscar(self, isbn: str) -> Livro:
        """Retorna o livro com o ISBN exato ou levanta ErroBiblioteca."""
        if not isinstance(isbn, str) or isbn not in self._livros:
            raise ErroBiblioteca(f"ISBN não encontrado no catálogo: {isbn!r}")
        return self._livros[isbn]

    def listar(self) -> list[Livro]:
        """Retorna uma nova lista de livros ordenada pelo ISBN."""
        return sorted(self._livros.values(), key=lambda livro: livro.isbn)
