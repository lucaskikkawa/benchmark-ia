from dataclasses import dataclass


class ErroBiblioteca(Exception):
    pass


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if not isinstance(self.isbn, str) or len(self.isbn) != 13 or not (
            self.isbn.isascii() and self.isbn.isdigit()
        ):
            raise ErroBiblioteca("ISBN inválido: deve conter exatamente 13 dígitos ASCII.")

        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("Título inválido: deve ser uma string.")
        titulo_limpo = self.titulo.strip()
        if not titulo_limpo:
            raise ErroBiblioteca("Título inválido: não pode ser vazio.")
        object.__setattr__(self, "titulo", titulo_limpo)

        if (
            not isinstance(self.exemplares, int)
            or isinstance(self.exemplares, bool)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("Exemplares inválidos: deve ser int >= 1.")
