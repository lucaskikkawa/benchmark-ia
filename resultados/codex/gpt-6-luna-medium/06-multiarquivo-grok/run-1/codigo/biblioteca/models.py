from dataclasses import dataclass


class ErroBiblioteca(Exception):
    """Erro de validação ou operação no sistema da biblioteca."""


@dataclass(frozen=True)
class Livro:
    isbn: str
    titulo: str
    exemplares: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.isbn, str)
            or len(self.isbn) != 13
            or any(caractere < "0" or caractere > "9" for caractere in self.isbn)
        ):
            raise ErroBiblioteca("ISBN deve conter exatamente 13 dígitos ASCII.")

        if not isinstance(self.titulo, str):
            raise ErroBiblioteca("Título deve ser uma string.")
        titulo = self.titulo.strip()
        if not titulo:
            raise ErroBiblioteca("Título não pode ficar vazio.")
        object.__setattr__(self, "titulo", titulo)

        if isinstance(self.exemplares, bool) or not isinstance(self.exemplares, int) or self.exemplares < 1:
            raise ErroBiblioteca("Exemplares deve ser um inteiro maior ou igual a 1.")
