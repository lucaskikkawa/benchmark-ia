from .models import ErroBiblioteca, Livro


class Catalogo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise ErroBiblioteca("livro deve ser uma instância de Livro")
        if livro.isbn in self._livros:
            raise ErroBiblioteca(f"Livro com ISBN {livro.isbn} já existe no catálogo")
        self._livros[livro.isbn] = livro

    def buscar(self, isbn: str) -> Livro:
        if not isinstance(isbn, str):
            raise ErroBiblioteca("ISBN deve ser string")
        if isbn not in self._livros:
            raise ErroBiblioteca(f"Livro com ISBN {isbn} não encontrado")
        return self._livros[isbn]

    def listar(self) -> list[Livro]:
        return [self._livros[isbn] for isbn in sorted(self._livros.keys())]
