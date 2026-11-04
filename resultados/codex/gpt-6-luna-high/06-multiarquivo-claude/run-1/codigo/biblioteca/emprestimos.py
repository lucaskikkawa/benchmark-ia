"""Regras para empréstimo, devolução e renovação de livros."""

from datetime import date, timedelta

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
            raise ValueError("limite_por_usuario deve ser pelo menos 1")
        if prazo_dias < 1:
            raise ValueError("prazo_dias deve ser pelo menos 1")
        if multa_diaria < 0:
            raise ValueError("multa_diaria não pode ser negativa")
        if max_renovacoes < 0:
            raise ValueError("max_renovacoes não pode ser negativa")
        self._acervo = acervo
        self._limite_por_usuario = limite_por_usuario
        self._prazo_dias = prazo_dias
        self._multa_diaria = multa_diaria
        self._max_renovacoes = max_renovacoes
        self._ativos: dict[str, Emprestimo] = {}

    def emprestar(self, isbn: str, usuario: str, data: date) -> Emprestimo:
        self._acervo.obter(isbn)
        if isbn in self._ativos:
            raise LivroIndisponivel(f"Livro {isbn!r} já está emprestado")
        if sum(1 for item in self._ativos.values() if item.usuario == usuario) >= self._limite_por_usuario:
            raise LimiteEmprestimos(f"Usuário {usuario!r} atingiu o limite de empréstimos")
        emprestimo = Emprestimo(
            isbn=isbn,
            usuario=usuario,
            data_emprestimo=data,
            data_prevista=data + timedelta(days=self._prazo_dias),
        )
        self._ativos[isbn] = emprestimo
        return emprestimo

    def devolver(self, isbn: str, data: date) -> float:
        self._acervo.obter(isbn)
        try:
            emprestimo = self._ativos[isbn]
        except KeyError:
            raise EmprestimoNaoEncontrado(f"Não há empréstimo ativo para {isbn!r}") from None
        if data < emprestimo.data_emprestimo:
            raise ValueError("data não pode ser anterior à data do empréstimo")
        dias_de_atraso = max(0, (data - emprestimo.data_prevista).days)
        del self._ativos[isbn]
        return round(dias_de_atraso * self._multa_diaria, 2)

    def disponivel(self, isbn: str) -> bool:
        self._acervo.obter(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        emprestimos = [item for item in self._ativos.values() if item.usuario == usuario]
        return sorted(emprestimos, key=lambda item: (item.data_prevista, item.isbn))

    def renovar(self, isbn: str, data: date) -> Emprestimo:
        self._acervo.obter(isbn)
        try:
            emprestimo = self._ativos[isbn]
        except KeyError:
            raise EmprestimoNaoEncontrado(f"Não há empréstimo ativo para {isbn!r}") from None
        if data < emprestimo.data_emprestimo:
            raise ValueError("data não pode ser anterior à data do empréstimo")
        if data > emprestimo.data_prevista or emprestimo.renovacoes >= self._max_renovacoes:
            raise RenovacaoNegada(f"Empréstimo de {isbn!r} não pode ser renovado")
        nova_data_prevista = max(
            emprestimo.data_prevista,
            data + timedelta(days=self._prazo_dias),
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

    def atrasados(self, data: date) -> list[Emprestimo]:
        atrasados = [item for item in self._ativos.values() if item.data_prevista < data]
        return sorted(atrasados, key=lambda item: (item.data_prevista, item.isbn))
