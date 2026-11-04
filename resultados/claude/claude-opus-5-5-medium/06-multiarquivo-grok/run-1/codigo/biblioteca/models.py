from dataclasses import dataclass

_DIGITOS = frozenset("0123456789")


class ErroBiblioteca(Exception):
    pass


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.isbn, str)
            or len(self.isbn) != 13
            or not all(c in _DIGITOS for c in self.isbn)
        ):
            raise ErroBiblioteca("ISBN inválido")
        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("título inválido")
        titulo = self.titulo.strip()
        if not titulo:
            raise ErroBiblioteca("título vazio")
        object.__setattr__(self, "titulo", titulo)
        if (
            not isinstance(self.exemplares, int)
            or isinstance(self.exemplares, bool)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("exemplares inválido")
