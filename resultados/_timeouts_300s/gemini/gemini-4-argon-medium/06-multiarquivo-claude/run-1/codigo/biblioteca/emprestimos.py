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
            raise ValueError("limite_por_usuario deve ser pelo menos 1.")
        if prazo_dias < 1:
            raise ValueError("prazo_dias deve ser pelo menos 1.")
        if multa_diaria < 0:
            raise ValueError("multa_diaria não pode ser negativa.")
        if max_renovacoes < 0:
            raise ValueError("max_renovacoes não pode ser negativo.")

        self._acervo = acervo
        self._limite_por_usuario = limite_por_usuario
        self._prazo_dias = prazo_dias
        self._multa_diaria = multa_diaria
        self._max_renovacoes = max_renovacoes
        self._ativos: dict[str, Emprestimo] = {}

    def emprestar(self, isbn: str, usuario: str, data: datetime.date) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado.")
        if isbn in self._ativos:
            raise LivroIndisponivel(f"Livro com ISBN '{isbn}' já está emprestado.")
        ativos_usuario = sum(1 for emp in self._ativos.values() if emp.usuario == usuario)
        if ativos_usuario >= self._limite_por_usuario:
            raise LimiteEmprestimos(
                f"Usuário '{usuario}' atingiu o limite de {self._limite_por_usuario} empréstimos."
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
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado.")
        if isbn not in self._ativos:
            raise EmprestimoNaoEncontrado(f"Não há empréstimo ativo para o ISBN '{isbn}'.")

        emp = self._ativos[isbn]
        if data < emp.data_emprestimo:
            raise ValueError("A data de devolução não pode ser anterior à data do empréstimo.")

        del self._ativos[isbn]
        dias_atraso = max(0, (data - emp.data_prevista).days)
        if dias_atraso == 0:
            return 0.0
        return round(float(dias_atraso * self._multa_diaria), 2)

    def disponivel(self, isbn: str) -> bool:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado.")
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        ativos = (emp for emp in self._ativos.values() if emp.usuario == usuario)
        return sorted(ativos, key=lambda e: (e.data_prevista, e.isbn))

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado.")
        if isbn not in self._ativos:
            raise EmprestimoNaoEncontrado(f"Não há empréstimo ativo para o ISBN '{isbn}'.")

        emp = self._ativos[isbn]
        if data < emp.data_emprestimo:
            raise ValueError("A data de renovação não pode ser anterior à data do empréstimo.")
        if data > emp.data_prevista or emp.renovacoes >= self._max_renovacoes:
            raise RenovacaoNegada(f"Renovação negada para o ISBN '{isbn}'.")

        nova_prevista = max(
            emp.data_prevista,
            data + datetime.timedelta(days=self._prazo_dias),
        )
        novo_emp = Emprestimo(
            isbn=emp.isbn,
            usuario=emp.usuario,
            data_emprestimo=emp.data_emprestimo,
            data_prevista=nova_prevista,
            renovacoes=emp.renovacoes + 1,
        )
        self._ativos[isbn] = novo_emp
        return novo_emp

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        vencidos = (emp for emp in self._ativos.values() if emp.data_prevista < data)
        return sorted(vencidos, key=lambda e: (e.data_prevista, e.isbn))
