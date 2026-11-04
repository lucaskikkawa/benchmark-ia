"""Catálogo de livros indexado por ISBN."""

from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError("livro deve ser um Livro")
        if livro.isbn in self._livros:
            raise ValueError(f"já existe livro com isbn {livro.isbn}")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError:
            raise LivroNaoEncontrado(f"isbn não encontrado: {isbn}") from None

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        trecho_cf = trecho.casefold()
        encontrados = [
            livro
            for livro in self._livros.values()
            if trecho_cf in livro.autor.casefold()
        ]
        encontrados.sort(key=lambda livro: (livro.titulo, livro.isbn))
        return encontrados

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isbn in self._livros
