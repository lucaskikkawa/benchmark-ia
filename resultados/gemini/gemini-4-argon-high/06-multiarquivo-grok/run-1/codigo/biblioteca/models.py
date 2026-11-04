from dataclasses import dataclass


class ErroBiblioteca(Exception):
    """Exceção para erros de validação e regras de negócio da biblioteca."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.isbn, str)
            or len(self.isbn) != 13
            or not all("0" <= c <= "9" for c in self.isbn)
        ):
            raise ErroBiblioteca("ISBN deve ser uma string com exatamente 13 dígitos ASCII.")

        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("Título deve ser uma string.")
        titulo_limpo = self.titulo.strip()
        if not titulo_limpo:
            raise ErroBiblioteca("Título não pode ser vazio.")
        object.__setattr__(self, "titulo", titulo_limpo)

        if (
            isinstance(self.exemplares, bool)
            or not isinstance(self.exemplares, int)
            or self.exemplares < 1
        ):
            raise ErroBiblioteca("Exemplares deve ser um inteiro maior ou igual a 1.")
