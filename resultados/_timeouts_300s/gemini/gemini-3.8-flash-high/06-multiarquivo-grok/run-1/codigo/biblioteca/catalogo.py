from .models import ErroBiblioteca, Livro


class Catalogo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise ErroBiblioteca(
                f"adicionar exige uma instância de Livro, recebido {type(livro).__name__}"
            )
        if livro.isbn in self._livros:
            raise ErroBiblioteca(f"Livro com ISBN {livro.isbn} já existe no catálogo")
        self._livros[livro.isbn] = livro

    def buscar(self, isbn: str) -> Livro:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser uma string")
        if isbn not in self._livros:
            raise ErroBiblioteca(f"Livro com ISBN {isbn!r} não encontrado no catálogo")
        return self._livros[isbn]

    def listar(self) -> list[Livro]:
        return sorted(self._livros.values(), key=lambda livro: livro.isbn)
