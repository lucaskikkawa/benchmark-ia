from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError("Esperado um objeto Livro")
        if livro.isbn in self._livros:
            raise ValueError(f"Livro com ISBN {livro.isbn!r} já existe no acervo")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError as exc:
            raise LivroNaoEncontrado(isbn) from exc

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        alvo = trecho.casefold()
        encontrados = [
            livro
            for livro in self._livros.values()
            if alvo in livro.autor.casefold()
        ]
        encontrados.sort(key=lambda l: (l.titulo, l.isbn))
        return encontrados

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isbn in self._livros
