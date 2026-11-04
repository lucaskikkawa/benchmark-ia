"""Modelos e erros de domínio da biblioteca."""

from dataclasses import dataclass


class ErroBiblioteca(Exception):
    """Indica uma violação das regras da biblioteca."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.isbn, str)
            or len(self.isbn) != 13
            or any(digito not in "0123456789" for digito in self.isbn)
        ):
            raise ErroBiblioteca("O ISBN deve conter exatamente 13 dígitos ASCII.")
        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("O título deve ser uma string.")
        titulo = str.strip(self.titulo)
        if not titulo:
            raise ErroBiblioteca("O título não pode ser vazio.")
        if (
            not isinstance(self.exemplares, int)
            or isinstance(self.exemplares, bool)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("A quantidade de exemplares deve ser um inteiro positivo.")
        object.__setattr__(self, "titulo", titulo)
