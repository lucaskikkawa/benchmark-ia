"""Regras de empréstimo e devolução."""

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
    """Controla os empréstimos ativos sobre um Acervo."""

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
        self._acervo = acervo  # mesmo objeto: livros adicionados depois ficam visíveis
        self.limite_por_usuario = limite_por_usuario
        self.prazo_dias = prazo_dias
        self.multa_diaria = multa_diaria
        self.max_renovacoes = max_renovacoes
        self._ativos: dict[str, Emprestimo] = {}  # isbn -> empréstimo ativo

    def emprestar(self, isbn: str, usuario: str, data: date) -> Emprestimo:
        self._acervo.obter(isbn)  # LivroNaoEncontrado se não existir
        if isbn in self._ativos:
            raise LivroIndisponivel(isbn)
        if len(self.emprestimos_de(usuario)) >= self.limite_por_usuario:
            raise LimiteEmprestimos(usuario)
        emprestimo = Emprestimo(isbn, usuario, data, data + timedelta(days=self.prazo_dias))
        self._ativos[isbn] = emprestimo
        return emprestimo

    def _ativo(self, isbn: str, data: date) -> Emprestimo:
        """Empréstimo ativo de ``isbn``, validando acervo, existência e data."""
        self._acervo.obter(isbn)
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data anterior à data do empréstimo")
        return emprestimo

    def devolver(self, isbn: str, data: date) -> float:
        emprestimo = self._ativo(isbn, data)
        del self._ativos[isbn]
        dias_atraso = max(0, (data - emprestimo.data_prevista).days)
        return round(dias_atraso * self.multa_diaria, 2)

    def renovar(self, isbn: str, data: date) -> Emprestimo:
        emprestimo = self._ativo(isbn, data)
        if data > emprestimo.data_prevista:
            raise RenovacaoNegada(f"{isbn}: empréstimo atrasado")
        if emprestimo.renovacoes >= self.max_renovacoes:
            raise RenovacaoNegada(f"{isbn}: limite de {self.max_renovacoes} renovação(ões)")
        renovado = replace(
            emprestimo,
            data_prevista=max(emprestimo.data_prevista, data + timedelta(days=self.prazo_dias)),
            renovacoes=emprestimo.renovacoes + 1,
        )
        self._ativos[isbn] = renovado
        return renovado

    def atrasados(self, data: date) -> list[Emprestimo]:
        vencidos = (e for e in self._ativos.values() if e.data_prevista < data)
        return sorted(vencidos, key=lambda e: (e.data_prevista, e.isbn))

    def disponivel(self, isbn: str) -> bool:
        self._acervo.obter(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        do_usuario = (e for e in self._ativos.values() if e.usuario == usuario)
        return sorted(do_usuario, key=lambda e: (e.data_prevista, e.isbn))
