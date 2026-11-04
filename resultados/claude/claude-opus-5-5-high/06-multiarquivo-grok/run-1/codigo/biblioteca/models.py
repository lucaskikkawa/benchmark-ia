import re
from dataclasses import dataclass

_ISBN_RE = re.compile(r"[0-9]{13}")


class ErroBiblioteca(Exception):
    """Erro de regra da biblioteca."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if not isinstance(self.isbn, str) or not _ISBN_RE.fullmatch(self.isbn):
            raise ErroBiblioteca("ISBN deve ter exatamente 13 dígitos")
        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("título deve ser string")
        titulo = self.titulo.strip()
        if not titulo:
            raise ErroBiblioteca("título vazio")
        object.__setattr__(self, "titulo", titulo)
        if (
            not isinstance(self.exemplares, int)
            or isinstance(self.exemplares, bool)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("exemplares deve ser inteiro >= 1")
