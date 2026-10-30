from .models import ErroBiblioteca, Livro


class Catalogo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise ErroBiblioteca("O catálogo aceita apenas instâncias de Livro.")
        if livro.isbn in self._livros:
            raise ErroBiblioteca("ISBN já cadastrado.")
        self._livros[livro.isbn] = livro

    def buscar(self, isbn: str) -> Livro:
        if not isinstance(isbn, str) or isbn not in self._livros:
            raise ErroBiblioteca("ISBN não encontrado no catálogo.")
        return self._livros[isbn]

    def listar(self) -> list[Livro]:
        return [self._livros[isbn] for isbn in sorted(self._livros)]
