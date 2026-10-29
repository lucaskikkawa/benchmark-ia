"""Regras de empréstimo e devolução."""

from datetime import date, timedelta

from .acervo import Acervo
from .modelos import (
    Emprestimo,
    EmprestimoNaoEncontrado,
    LimiteEmprestimos,
    LivroIndisponivel,
)


class ServicoEmprestimos:
    """Controla os empréstimos ativos sobre um Acervo."""

    def __init__(
        self,
        acervo: Acervo,
        limite_por_usuario: int = 3,
        prazo_dias: int = 14,
        multa_diaria: float = 1.0,
    ) -> None:
        self._acervo = acervo
        self.limite_por_usuario = limite_por_usuario
        self.prazo_dias = prazo_dias
        self.multa_diaria = multa_diaria
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

    def devolver(self, isbn: str, data: date) -> float:
        self._acervo.obter(isbn)
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data de devolução anterior à data do empréstimo")
        del self._ativos[isbn]
        dias_atraso = max(0, (data - emprestimo.data_prevista).days)
        return round(dias_atraso * self.multa_diaria, 2)

    def disponivel(self, isbn: str) -> bool:
        self._acervo.obter(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        do_usuario = (e for e in self._ativos.values() if e.usuario == usuario)
        return sorted(do_usuario, key=lambda e: (e.data_prevista, e.isbn))
