"""Armazenamento e consultas do acervo."""

from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError("livro deve ser uma instância de Livro")
        if livro.isbn in self._livros:
            raise ValueError(f"Já existe um livro com ISBN {livro.isbn!r}")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado") from None

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        termo = trecho.casefold()
        encontrados = [livro for livro in self._livros.values() if termo in livro.autor.casefold()]
        return sorted(encontrados, key=lambda livro: (livro.titulo, livro.isbn))

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isbn in self._livros
