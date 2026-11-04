"""Empréstimos ativos sobre um acervo compartilhado."""

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

    def emprestar(self, isbn: str, usuario: str, data: datetime.date) -> Emprestimo:
        self._acervo.obter(isbn)
        if isbn in self._ativos:
            raise LivroIndisponivel(f"livro já emprestado: {isbn}")
        ativos_do_usuario = sum(
            1 for emp in self._ativos.values() if emp.usuario == usuario
        )
        if ativos_do_usuario >= self._limite_por_usuario:
            raise LimiteEmprestimos(
                f"usuário {usuario} atingiu o limite de empréstimos"
            )
        emprestimo = Emprestimo(
            isbn=isbn,
            usuario=usuario,
            data_emprestimo=data,
            data_prevista=data + datetime.timedelta(days=self._prazo_dias),
        )
        self._ativos[isbn] = emprestimo
        return emprestimo

    def devolver(self, isbn: str, data: datetime.date) -> float:
        self._acervo.obter(isbn)
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(f"sem empréstimo ativo: {isbn}")
        if data < emprestimo.data_emprestimo:
            raise ValueError("data de devolução anterior ao empréstimo")
        dias_atraso = (data - emprestimo.data_prevista).days
        if dias_atraso < 0:
            dias_atraso = 0
        del self._ativos[isbn]
        return float(round(dias_atraso * self._multa_diaria, 2))

    def disponivel(self, isbn: str) -> bool:
        self._acervo.obter(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        itens = [emp for emp in self._ativos.values() if emp.usuario == usuario]
        itens.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return itens

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        self._acervo.obter(isbn)
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(f"sem empréstimo ativo: {isbn}")
        if data < emprestimo.data_emprestimo:
            raise ValueError("data de renovação anterior ao empréstimo")
        if data > emprestimo.data_prevista or emprestimo.renovacoes >= self._max_renovacoes:
            raise RenovacaoNegada(f"renovação negada: {isbn}")
        nova_prevista = max(
            emprestimo.data_prevista,
            data + datetime.timedelta(days=self._prazo_dias),
        )
        novo = Emprestimo(
            isbn=emprestimo.isbn,
            usuario=emprestimo.usuario,
            data_emprestimo=emprestimo.data_emprestimo,
            data_prevista=nova_prevista,
            renovacoes=emprestimo.renovacoes + 1,
        )
        self._ativos[isbn] = novo
        return novo

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        itens = [emp for emp in self._ativos.values() if emp.data_prevista < data]
        itens.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return itens
