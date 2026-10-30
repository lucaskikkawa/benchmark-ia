"""Serviço de empréstimos sobre um Acervo."""

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
        self.acervo = acervo
        self.limite_por_usuario = limite_por_usuario
        self.prazo_dias = prazo_dias
        self.multa_diaria = multa_diaria
        self.max_renovacoes = max_renovacoes
        self._ativos: dict[str, Emprestimo] = {}

    def emprestar(self, isbn: str, usuario: str, data: datetime.date) -> Emprestimo:
        self.acervo.obter(isbn)
        if isbn in self._ativos:
            raise LivroIndisponivel(isbn)
        ativos = sum(1 for item in self._ativos.values() if item.usuario == usuario)
        if ativos >= self.limite_por_usuario:
            raise LimiteEmprestimos(usuario)
        emprestimo = Emprestimo(
            isbn=isbn,
            usuario=usuario,
            data_emprestimo=data,
            data_prevista=data + datetime.timedelta(days=self.prazo_dias),
        )
        self._ativos[isbn] = emprestimo
        return emprestimo

    def devolver(self, isbn: str, data: datetime.date) -> float:
        self.acervo.obter(isbn)
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data anterior à data do empréstimo")
        atraso = (data - emprestimo.data_prevista).days
        if atraso < 0:
            atraso = 0
        del self._ativos[isbn]
        return float(round(atraso * self.multa_diaria, 2))

    def disponivel(self, isbn: str) -> bool:
        self.acervo.obter(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        itens = [item for item in self._ativos.values() if item.usuario == usuario]
        itens.sort(key=lambda item: (item.data_prevista, item.isbn))
        return itens

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        self.acervo.obter(isbn)
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data anterior à data do empréstimo")
        if data > emprestimo.data_prevista or emprestimo.renovacoes >= self.max_renovacoes:
            raise RenovacaoNegada(isbn)
        novo = Emprestimo(
            isbn=emprestimo.isbn,
            usuario=emprestimo.usuario,
            data_emprestimo=emprestimo.data_emprestimo,
            data_prevista=max(
                emprestimo.data_prevista,
                data + datetime.timedelta(days=self.prazo_dias),
            ),
            renovacoes=emprestimo.renovacoes + 1,
        )
        self._ativos[isbn] = novo
        return novo

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        itens = [item for item in self._ativos.values() if item.data_prevista < data]
        itens.sort(key=lambda item: (item.data_prevista, item.isbn))
        return itens
