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
        if (
            limite_por_usuario < 1
            or prazo_dias < 1
            or multa_diaria < 0
            or max_renovacoes < 0
        ):
            raise ValueError("Parâmetros de configuração inválidos")
        self._acervo = acervo
        self._limite_por_usuario = limite_por_usuario
        self._prazo_dias = prazo_dias
        self._multa_diaria = multa_diaria
        self._max_renovacoes = max_renovacoes
        self._emprestimos: dict[str, Emprestimo] = {}

    def emprestar(
        self, isbn: str, usuario: str, data: datetime.date
    ) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(isbn)
        if isbn in self._emprestimos:
            raise LivroIndisponivel(isbn)
        ativos_usuario = sum(
            1 for emp in self._emprestimos.values() if emp.usuario == usuario
        )
        if ativos_usuario >= self._limite_por_usuario:
            raise LimiteEmprestimos(usuario)

        data_prevista = data + datetime.timedelta(days=self._prazo_dias)
        emprestimo = Emprestimo(
            isbn=isbn,
            usuario=usuario,
            data_emprestimo=data,
            data_prevista=data_prevista,
            renovacoes=0,
        )
        self._emprestimos[isbn] = emprestimo
        return emprestimo

    def devolver(self, isbn: str, data: datetime.date) -> float:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(isbn)
        emprestimo = self._emprestimos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("Data de devolução anterior à data de empréstimo")

        del self._emprestimos[isbn]
        dias_atraso = (data - emprestimo.data_prevista).days
        if dias_atraso <= 0:
            return 0.0
        return round(dias_atraso * float(self._multa_diaria), 2)

    def disponivel(self, isbn: str) -> bool:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(isbn)
        return isbn not in self._emprestimos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        ativos = [
            emp for emp in self._emprestimos.values() if emp.usuario == usuario
        ]
        ativos.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return ativos

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(isbn)
        emprestimo = self._emprestimos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("Data de renovação anterior à data de empréstimo")
        if (
            data > emprestimo.data_prevista
            or emprestimo.renovacoes >= self._max_renovacoes
        ):
            raise RenovacaoNegada(isbn)

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
        self._emprestimos[isbn] = novo_emprestimo
        return novo_emprestimo

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        lista = [
            emp
            for emp in self._emprestimos.values()
            if emp.data_prevista < data
        ]
        lista.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return lista
