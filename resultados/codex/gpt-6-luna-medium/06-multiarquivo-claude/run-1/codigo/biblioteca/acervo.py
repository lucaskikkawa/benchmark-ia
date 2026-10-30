from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    def __init__(self):
        self._livros = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError("livro deve ser uma instância de Livro")
        if livro.isbn in self._livros:
            raise ValueError(f"ISBN já cadastrado: {livro.isbn}")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError:
            raise LivroNaoEncontrado(f"Livro não encontrado: {isbn}") from None

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        consulta = trecho.casefold()
        encontrados = [livro for livro in self._livros.values()
                       if consulta in livro.autor.casefold()]
        return sorted(encontrados, key=lambda livro: (livro.titulo, livro.isbn))

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn) -> bool:
        return isbn in self._livros
