from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError("livro deve ser uma instância de Livro")
        if livro.isbn in self._livros:
            raise ValueError(f"Livro com ISBN {livro.isbn!r} já existe no acervo")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        if isbn not in self._livros:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado")
        return self._livros[isbn]

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        termo = trecho.casefold()
        encontrados = [
            livro
            for livro in self._livros.values()
            if termo in livro.autor.casefold()
        ]
        encontrados.sort(key=lambda livro: (livro.titulo, livro.isbn))
        return encontrados

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isbn in self._livros
