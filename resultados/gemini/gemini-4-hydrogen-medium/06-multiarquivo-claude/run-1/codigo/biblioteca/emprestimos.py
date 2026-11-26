from __future__ import annotations

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
    """Gerencia empréstimos, devoluções, renovações e atrasos sobre um Acervo."""

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
        self._multa_diaria = float(multa_diaria)
        self._max_renovacoes = max_renovacoes
        self._ativos: dict[str, Emprestimo] = {}

    def _exigir_no_acervo(self, isbn: str) -> None:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado no acervo")

    def _obter_emprestimo_ativo(self, isbn: str) -> Emprestimo:
        self._exigir_no_acervo(isbn)
        try:
            return self._ativos[isbn]
        except KeyError as exc:
            raise EmprestimoNaoEncontrado(f"Não há empréstimo ativo para o ISBN {isbn!r}") from exc

    def emprestar(self, isbn: str, usuario: str, data: datetime.date) -> Emprestimo:
        self._exigir_no_acervo(isbn)
        if isbn in self._ativos:
            raise LivroIndisponivel(f"Livro com ISBN {isbn!r} já está emprestado")
        ativos_usuario = sum(1 for emp in self._ativos.values() if emp.usuario == usuario)
        if ativos_usuario >= self._limite_por_usuario:
            raise LimiteEmprestimos(
                f"Usuário {usuario!r} atingiu o limite de {self._limite_por_usuario} empréstimos"
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
        emprestimo = self._obter_emprestimo_ativo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("Data de devolução não pode ser anterior à data do empréstimo")

        del self._ativos[isbn]
        dias_atraso = max(0, (data - emprestimo.data_prevista).days)
        return round(dias_atraso * self._multa_diaria, 2)

    def disponivel(self, isbn: str) -> bool:
        self._exigir_no_acervo(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        resultado = [emp for emp in self._ativos.values() if emp.usuario == usuario]
        resultado.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return resultado

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        emprestimo = self._obter_emprestimo_ativo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("Data de renovação não pode ser anterior à data do empréstimo")
        if data > emprestimo.data_prevista:
            raise RenovacaoNegada("Empréstimo em atraso não pode ser renovado")
        if emprestimo.renovacoes >= self._max_renovacoes:
            raise RenovacaoNegada("Limite máximo de renovações atingido")

        nova_data_prevista = max(
            emprestimo.data_prevista,
            data + datetime.timedelta(days=self._prazo_dias),
        )
        renovado = Emprestimo(
            isbn=emprestimo.isbn,
            usuario=emprestimo.usuario,
            data_emprestimo=emprestimo.data_emprestimo,
            data_prevista=nova_data_prevista,
            renovacoes=emprestimo.renovacoes + 1,
        )
        self._ativos[isbn] = renovado
        return renovado

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        resultado = [emp for emp in self._ativos.values() if emp.data_prevista < data]
        resultado.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return resultado
