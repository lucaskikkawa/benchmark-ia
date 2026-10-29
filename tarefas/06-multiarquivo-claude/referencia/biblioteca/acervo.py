"""Catálogo de livros."""

from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    """Coleção de livros indexada por ISBN."""

    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if livro.isbn in self._livros:
            raise ValueError(f"ISBN já cadastrado: {livro.isbn}")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError:
            raise LivroNaoEncontrado(isbn) from None

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        alvo = trecho.casefold()
        encontrados = (livro for livro in self._livros.values() if alvo in livro.autor.casefold())
        return sorted(encontrados, key=lambda livro: (livro.titulo, livro.isbn))

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isbn in self._livros
