import datetime

from .acervo import Acervo
from .modelos import (
    Emprestimo,
    EmprestimoNaoEncontrado,
    LimiteEmprestimos,
    LivroIndisponivel,
    LivroNaoEncontrado,
    RenovacaoNegada,
)


class ServicoEmprestimos:
    def __init__(
        self,
        acervo: Acervo,
        limite_por_usuario: int = 3,
        prazo_dias: int = 14,
        multa_diaria: float = 1.0,
        max_renovacoes: int = 2,
    ) -> None:
        if limite_por_usuario < 1:
            raise ValueError("limite_por_usuario deve ser >= 1")
        if prazo_dias < 1:
            raise ValueError("prazo_dias deve ser >= 1")
        if multa_diaria < 0:
            raise ValueError("multa_diaria deve ser >= 0")
        if max_renovacoes < 0:
            raise ValueError("max_renovacoes deve ser >= 0")

        self._acervo = acervo
        self._limite_por_usuario = limite_por_usuario
        self._prazo_dias = prazo_dias
        self._multa_diaria = multa_diaria
        self._max_renovacoes = max_renovacoes
        self._ativos: dict[str, Emprestimo] = {}

    def emprestar(
        self, isbn: str, usuario: str, data: datetime.date
    ) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro {isbn!r} não encontrado no acervo")
        if isbn in self._ativos:
            raise LivroIndisponivel(f"Livro {isbn!r} já está emprestado")
        ativos_usuario = sum(
            1 for emp in self._ativos.values() if emp.usuario == usuario
        )
        if ativos_usuario >= self._limite_por_usuario:
            raise LimiteEmprestimos(
                f"Usuário {usuario!r} atingiu o limite de empréstimos"
            )

        data_prevista = data + datetime.timedelta(days=self._prazo_dias)
        emprestimo = Emprestimo(
            isbn=isbn,
            usuario=usuario,
            data_emprestimo=data,
            data_prevista=data_prevista,
            renovacoes=0,
        )
        self._ativos[isbn] = emprestimo
        return emprestimo

    def devolver(self, isbn: str, data: datetime.date) -> float:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro {isbn!r} não encontrado no acervo")
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(f"Livro {isbn!r} não está emprestado")
        if data < emprestimo.data_emprestimo:
            raise ValueError("Data de devolução anterior à data de empréstimo")

        del self._ativos[isbn]
        dias_atraso = (data - emprestimo.data_prevista).days
        if dias_atraso <= 0:
            return 0.0
        return round(float(dias_atraso * self._multa_diaria), 2)

    def disponivel(self, isbn: str) -> bool:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro {isbn!r} não encontrado no acervo")
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        lista = [
            emp for emp in self._ativos.values() if emp.usuario == usuario
        ]
        lista.sort(key=lambda e: (e.data_prevista, e.isbn))
        return lista

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro {isbn!r} não encontrado no acervo")
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(f"Livro {isbn!r} não está emprestado")
        if data < emprestimo.data_emprestimo:
            raise ValueError("Data de renovação anterior à data de empréstimo")
        if (
            data > emprestimo.data_prevista
            or emprestimo.renovacoes >= self._max_renovacoes
        ):
            raise RenovacaoNegada("Renovação não permitida")

        nova_prevista = max(
            emprestimo.data_prevista,
            data + datetime.timedelta(days=self._prazo_dias),
        )
        novo_emprestimo = Emprestimo(
            isbn=emprestimo.isbn,
            usuario=emprestimo.usuario,
            data_emprestimo=emprestimo.data_emprestimo,
            data_prevista=nova_prevista,
            renovacoes=emprestimo.renovacoes + 1,
        )
        self._ativos[isbn] = novo_emprestimo
        return novo_emprestimo

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        lista = [
            emp for emp in self._ativos.values() if emp.data_prevista < data
        ]
        lista.sort(key=lambda e: (e.data_prevista, e.isbn))
        return lista
