from dataclasses import dataclass
import re


class ErroBiblioteca(Exception):
    """Erro de validação ou de regra da biblioteca."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if not isinstance(self.isbn, str) or re.fullmatch(r"[0-9]{13}", self.isbn) is None:
            raise ErroBiblioteca("ISBN deve conter exatamente 13 dígitos ASCII")
        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("Título deve ser uma string")
        titulo = self.titulo.strip()
        if not titulo:
            raise ErroBiblioteca("Título não pode ser vazio")
        object.__setattr__(self, "titulo", titulo)
        if isinstance(self.exemplares, bool) or not isinstance(self.exemplares, int) or self.exemplares < 1:
            raise ErroBiblioteca("Exemplares deve ser um inteiro maior ou igual a 1")
