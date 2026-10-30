from .modelos import Livro, LivroNaoEncontrado


class Acervo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise TypeError("O objeto adicionado deve ser uma instância de Livro.")
        if livro.isbn in self._livros:
            raise ValueError(f"Já existe um livro com o ISBN '{livro.isbn}'.")
        self._livros[livro.isbn] = livro

    def obter(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except KeyError as exc:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado.") from exc

    def buscar_por_autor(self, trecho: str) -> list[Livro]:
        alvo = trecho.casefold()
        encontrados = (
            livro for livro in self._livros.values() if alvo in livro.autor.casefold()
        )
        return sorted(encontrados, key=lambda l: (l.titulo, l.isbn))

    def __len__(self) -> int:
        return len(self._livros)

    def __contains__(self, isbn: object) -> bool:
        return isbn in self._livros
