import datetime
from .modelos import (
    Emprestimo,
    LivroNaoEncontrado,
    LivroIndisponivel,
    LimiteEmprestimos,
    EmprestimoNaoEncontrado,
    RenovacaoNegada,
)
from .acervo import Acervo


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
        self.multa_diaria = float(multa_diaria)
        self.max_renovacoes = max_renovacoes
        self._emprestimos: dict[str, Emprestimo] = {}

    def emprestar(self, isbn: str, usuario: str, data: datetime.date) -> Emprestimo:
        if isbn not in self.acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado no acervo")
        if isbn in self._emprestimos:
            raise LivroIndisponivel(f"Livro com ISBN '{isbn}' já está emprestado")

        ativos_usuario = sum(1 for emp in self._emprestimos.values() if emp.usuario == usuario)
        if ativos_usuario >= self.limite_por_usuario:
            raise LimiteEmprestimos(f"Usuário '{usuario}' já atingiu o limite de {self.limite_por_usuario} empréstimos ativos")

        data_prevista = data + datetime.timedelta(days=self.prazo_dias)
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
        if isbn not in self.acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado no acervo")
        if isbn not in self._emprestimos:
            raise EmprestimoNaoEncontrado(f"Empréstimo para o ISBN '{isbn}' não encontrado")

        emp = self._emprestimos[isbn]
        if data < emp.data_emprestimo:
            raise ValueError("Data de devolução não pode ser anterior à data de empréstimo")

        if data > emp.data_prevista:
            dias_atraso = (data - emp.data_prevista).days
            multa = round(dias_atraso * self.multa_diaria, 2)
        else:
            multa = 0.0

        del self._emprestimos[isbn]
        return float(multa)

    def disponivel(self, isbn: str) -> bool:
        if isbn not in self.acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado no acervo")
        return isbn not in self._emprestimos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        ativos = [emp for emp in self._emprestimos.values() if emp.usuario == usuario]
        return sorted(ativos, key=lambda emp: (emp.data_prevista, emp.isbn))

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        if isbn not in self.acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN '{isbn}' não encontrado no acervo")
        if isbn not in self._emprestimos:
            raise EmprestimoNaoEncontrado(f"Empréstimo para o ISBN '{isbn}' não encontrado")

        emp = self._emprestimos[isbn]
        if data < emp.data_emprestimo:
            raise ValueError("Data de renovação não pode ser anterior à data de empréstimo")
        if data > emp.data_prevista or emp.renovacoes >= self.max_renovacoes:
            raise RenovacaoNegada("Empréstimo em atraso ou limite de renovações atingido")

        nova_data_prevista = max(emp.data_prevista, data + datetime.timedelta(days=self.prazo_dias))
        novo_emp = Emprestimo(
            isbn=emp.isbn,
            usuario=emp.usuario,
            data_emprestimo=emp.data_emprestimo,
            data_prevista=nova_data_prevista,
            renovacoes=emp.renovacoes + 1,
        )
        self._emprestimos[isbn] = novo_emp
        return novo_emp

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        ativos_atrasados = [
            emp for emp in self._emprestimos.values()
            if emp.data_prevista < data
        ]
        return sorted(ativos_atrasados, key=lambda emp: (emp.data_prevista, emp.isbn))
