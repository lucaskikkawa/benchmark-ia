from __future__ import annotations

from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    """Repositório de livros indexados por ISBN."""

    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError(f"Esperado Livro, recebido {type(livro).__name__}")
        if livro.isbn in self._livros:
            raise ValueError(f"Já existe livro cadastrado com o ISBN {livro.isbn!r}")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError as exc:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado") from exc

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        termo = trecho.casefold()
        encontrados = [
            livro for livro in self._livros.values() if termo in livro.autor.casefold()
        ]
        encontrados.sort(key=lambda livro: (livro.titulo, livro.isbn))
        return encontrados

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isbn in self._livros
