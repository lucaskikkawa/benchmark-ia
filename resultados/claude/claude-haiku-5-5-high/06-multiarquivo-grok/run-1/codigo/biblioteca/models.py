from dataclasses import dataclass

DIGITOS = "0123456789"


class ErroBiblioteca(Exception):
    ...


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if not isinstance(self.isbn, str) or len(self.isbn) != 13 or any(c not in DIGITOS for c in self.isbn):
            raise ErroBiblioteca(f"ISBN inválido: {self.isbn!r}")
        if not isinstance(self.titulo, str) or not self.titulo.strip():
            raise ErroBiblioteca("título vazio ou inválido")
        if isinstance(self.exemplares, bool) or not isinstance(self.exemplares, int) or self.exemplares < 1:
            raise ErroBiblioteca(f"número de exemplares inválido: {self.exemplares!r}")
        object.__setattr__(self, "titulo", self.titulo.strip())
