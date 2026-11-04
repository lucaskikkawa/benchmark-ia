"""Empréstimos, devoluções e renovações de livros do acervo."""

from dataclasses import replace
from datetime import date, timedelta

from .acervo import Acervo
from .modelos import (
    Emprestimo,
    EmprestimoNaoEncontrado,
    LimiteEmprestimos,
    LivroIndisponivel,
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
            raise ValueError("limite_por_usuario deve ser pelo menos 1")
        if prazo_dias < 1:
            raise ValueError("prazo_dias deve ser pelo menos 1")
        if multa_diaria < 0:
            raise ValueError("multa_diaria não pode ser negativa")
        if max_renovacoes < 0:
            raise ValueError("max_renovacoes não pode ser negativo")
        self._acervo = acervo
        self._limite_por_usuario = limite_por_usuario
        self._prazo = timedelta(days=prazo_dias)
        self._multa_diaria = multa_diaria
        self._max_renovacoes = max_renovacoes
        self._ativos: dict[str, Emprestimo] = {}

    def emprestar(self, isbn: str, usuario: str, data: date) -> Emprestimo:
        self._acervo.obter(isbn)
        if isbn in self._ativos:
            raise LivroIndisponivel(isbn)
        quantidade = sum(emp.usuario == usuario for emp in self._ativos.values())
        if quantidade >= self._limite_por_usuario:
            raise LimiteEmprestimos(usuario)
        emprestimo = Emprestimo(isbn, usuario, data, data + self._prazo)
        self._ativos[isbn] = emprestimo
        return emprestimo

    def _obter_emprestimo(self, isbn: str) -> Emprestimo:
        self._acervo.obter(isbn)
        try:
            return self._ativos[isbn]
        except KeyError:
            raise EmprestimoNaoEncontrado(isbn) from None

    def devolver(self, isbn: str, data: date) -> float:
        emprestimo = self._obter_emprestimo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("devolução anterior ao empréstimo")
        dias_de_atraso = max(0, (data - emprestimo.data_prevista).days)
        multa = round(float(dias_de_atraso * self._multa_diaria), 2)
        del self._ativos[isbn]
        return multa

    def disponivel(self, isbn: str) -> bool:
        self._acervo.obter(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        return sorted(
            (emp for emp in self._ativos.values() if emp.usuario == usuario),
            key=lambda emp: (emp.data_prevista, emp.isbn),
        )

    def renovar(self, isbn: str, data: date) -> Emprestimo:
        emprestimo = self._obter_emprestimo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("renovação anterior ao empréstimo")
        if (
            data > emprestimo.data_prevista
            or emprestimo.renovacoes >= self._max_renovacoes
        ):
            raise RenovacaoNegada(isbn)
        renovado = replace(
            emprestimo,
            renovacoes=emprestimo.renovacoes + 1,
            data_prevista=max(emprestimo.data_prevista, data + self._prazo),
        )
        self._ativos[isbn] = renovado
        return renovado

    def atrasados(self, data: date) -> list[Emprestimo]:
        return sorted(
            (emp for emp in self._ativos.values() if emp.data_prevista < data),
            key=lambda emp: (emp.data_prevista, emp.isbn),
        )
