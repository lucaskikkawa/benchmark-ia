from dataclasses import dataclass


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
            or not self.isbn.isascii()
            or not self.isbn.isdigit()
        ):
            raise ErroBiblioteca("ISBN deve ter exatamente 13 dígitos ASCII sem hífen nem espaços")

        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("Título deve ser string")

        titulo_limpo = self.titulo.strip()
        if not titulo_limpo:
            raise ErroBiblioteca("Título não pode ser vazio")

        object.__setattr__(self, "titulo", titulo_limpo)

        if (
            isinstance(self.exemplares, bool)
            or not isinstance(self.exemplares, int)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("Exemplares deve ser um inteiro maior ou igual a 1")
