from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    """Gerencia o catálogo de livros indexados por ISBN."""

    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        """Adiciona um livro ao acervo."""
        if not isinstance(livro, Livro):
            raise TypeError("livro deve ser uma instância de Livro")
        if livro.isbn in self._livros:
            raise ValueError(f"já existe livro com ISBN {livro.isbn!r}")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        """Retorna o livro correspondente ao ISBN informado."""
        try:
            return self._livros[isbn]
        except KeyError as exc:
            raise LivroNaoEncontrado(f"livro {isbn!r} não encontrado") from exc

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        """Busca livros cujo autor contém o trecho (sem distinguir maiúsculas/minúsculas)."""
        alvo = trecho.casefold()
        encontrados = [
            livro
            for livro in self._livros.values()
            if alvo in livro.autor.casefold()
        ]
        encontrados.sort(key=lambda livro: (livro.titulo, livro.isbn))
        return encontrados

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isinstance(isbn, str) and isbn in self._livros
