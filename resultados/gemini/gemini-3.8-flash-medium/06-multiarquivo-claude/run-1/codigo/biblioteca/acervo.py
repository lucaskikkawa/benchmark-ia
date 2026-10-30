from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError("O objeto adicionado deve ser uma instância de Livro")
        if livro.isbn in self._livros:
            raise ValueError(f"Livro com ISBN '{livro.isbn}' já existe no acervo")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        if isbn not in self._livros:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado")
        return self._livros[isbn]

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        trecho_casefold = trecho.casefold()
        encontrados = [
            livro for livro in self._livros.values()
            if trecho_casefold in livro.autor.casefold()
        ]
        return sorted(encontrados, key=lambda l: (l.titulo, l.isbn))

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Livro):
            return item.isbn in self._livros
        try:
            return item in self._livros
        except TypeError:
            return False
