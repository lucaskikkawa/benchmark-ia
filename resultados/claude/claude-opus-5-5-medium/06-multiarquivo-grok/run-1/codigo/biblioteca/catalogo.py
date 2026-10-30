from .models import ErroBiblioteca, Livro


class Catalogo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise ErroBiblioteca("esperado um Livro")
        if livro.isbn in self._livros:
            raise ErroBiblioteca("ISBN repetido")
        self._livros[livro.isbn] = livro

    def buscar(self, isbn: str) -> Livro:
        if not isinstance(isbn, str) or isbn not in self._livros:
            raise ErroBiblioteca("ISBN não encontrado")
        return self._livros[isbn]

    def listar(self) -> list[Livro]:
        return sorted(self._livros.values(), key=lambda livro: livro.isbn)
