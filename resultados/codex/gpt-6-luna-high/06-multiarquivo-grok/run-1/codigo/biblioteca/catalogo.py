from .models import ErroBiblioteca, Livro


class Catalogo:
    def __init__(self) -> None:
        self._livros: dict[str, Livro] = {}

    def adicionar(self, livro: Livro) -> None:
        if not isinstance(livro, Livro):
            raise ErroBiblioteca("É necessário adicionar uma instância de Livro")
        if livro.isbn in self._livros:
            raise ErroBiblioteca("ISBN já cadastrado")
        self._livros[livro.isbn] = livro

    def buscar(self, isbn: str) -> Livro:
        try:
            return self._livros[isbn]
        except (KeyError, TypeError):
            raise ErroBiblioteca("Livro não encontrado no catálogo") from None

    def listar(self) -> list[Livro]:
        return [self._livros[isbn] for isbn in sorted(self._livros)]
