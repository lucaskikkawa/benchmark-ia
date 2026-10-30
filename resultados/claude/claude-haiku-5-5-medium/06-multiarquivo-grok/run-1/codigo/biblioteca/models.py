from dataclasses import dataclass


class ErroBiblioteca(Exception):
    ...


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if not isinstance(self.isbn, str) or len(self.isbn) != 13 or any(
            c not in "0123456789" for c in self.isbn
        ):
            raise ErroBiblioteca("ISBN deve ter exatamente 13 dígitos ASCII")
        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("título deve ser string")
        titulo = self.titulo.strip()
        if not titulo:
            raise ErroBiblioteca("título não pode ser vazio")
        object.__setattr__(self, "titulo", titulo)
        if isinstance(self.exemplares, bool) or not isinstance(self.exemplares, int):
            raise ErroBiblioteca("exemplares deve ser int")
        if self.exemplares < 1:
            raise ErroBiblioteca("exemplares deve ser >= 1")
