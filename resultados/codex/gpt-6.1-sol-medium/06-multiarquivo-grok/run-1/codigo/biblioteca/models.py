from dataclasses import dataclass


class ErroBiblioteca(Exception):
    """Uma entrada ou operação viola as regras da biblioteca."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.isbn, str)
            or len(self.isbn) != 13
            or any(caractere not in "0123456789" for caractere in self.isbn)
        ):
            raise ErroBiblioteca("ISBN deve conter exatamente 13 dígitos ASCII.")
        if not isinstance(self.titulo, str) or not self.titulo.strip():
            raise ErroBiblioteca("Título deve ser uma string não vazia.")
        if (
            not isinstance(self.exemplares, int)
            or isinstance(self.exemplares, bool)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("Exemplares deve ser um inteiro positivo.")
        object.__setattr__(self, "titulo", self.titulo.strip())
