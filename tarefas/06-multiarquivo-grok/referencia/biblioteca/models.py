"""Modelos da biblioteca."""

from dataclasses import dataclass


class ErroBiblioteca(Exception):
    """Erro de regra: ISBN, estoque, data ou empréstimo inválido."""


@dataclass(frozen=True)
class Livro:
    """Um título do catálogo, com ISBN de 13 dígitos e exemplares >= 1."""

    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.isbn, str)
            or len(self.isbn) != 13
            or any(caractere not in "0123456789" for caractere in self.isbn)
        ):
            raise ErroBiblioteca("isbn invalido")
        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("titulo invalido")
        titulo = self.titulo.strip()
        if not titulo:
            raise ErroBiblioteca("titulo invalido")
        object.__setattr__(self, "titulo", titulo)
        if (
            isinstance(self.exemplares, bool)
            or not isinstance(self.exemplares, int)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("exemplares invalido")
