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
        self._emprestimos: dict[str, Emprestimo] = {}

    def emprestar(
        self, isbn: str, usuario: str, data: datetime.date
    ) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado")
        if isbn in self._emprestimos:
            raise LivroIndisponivel(f"Livro com ISBN {isbn!r} já está emprestado")
        ativos_usuario = sum(
            1 for emp in self._emprestimos.values() if emp.usuario == usuario
        )
        if ativos_usuario >= self._limite_por_usuario:
            raise LimiteEmprestimos(
                f"Usuário {usuario!r} atingiu o limite de empréstimos"
            )

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
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado")
        emprestimo = self._emprestimos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(
                f"Livro com ISBN {isbn!r} não está emprestado"
            )
        if data < emprestimo.data_emprestimo:
            raise ValueError(
                "Data de devolução não pode ser anterior à data de empréstimo"
            )

        del self._emprestimos[isbn]
        dias_atraso = max(0, (data - emprestimo.data_prevista).days)
        return round(float(dias_atraso * self._multa_diaria), 2)

    def disponivel(self, isbn: str) -> bool:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado")
        return isbn not in self._emprestimos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        emprestimos = [
            emp for emp in self._emprestimos.values() if emp.usuario == usuario
        ]
        emprestimos.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return emprestimos

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"Livro com ISBN {isbn!r} não encontrado")
        emprestimo = self._emprestimos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(
                f"Livro com ISBN {isbn!r} não está emprestado"
            )
        if data < emprestimo.data_emprestimo:
            raise ValueError(
                "Data de renovação não pode ser anterior à data de empréstimo"
            )
        if data > emprestimo.data_prevista:
            raise RenovacaoNegada("Não é possível renovar empréstimo atrasado")
        if emprestimo.renovacoes >= self._max_renovacoes:
            raise RenovacaoNegada("Limite máximo de renovações atingido")

        nova_data_prevista = max(
            emprestimo.data_prevista,
            data + datetime.timedelta(days=self._prazo_dias),
        )
        novo = Emprestimo(
            isbn=emprestimo.isbn,
            usuario=emprestimo.usuario,
            data_emprestimo=emprestimo.data_emprestimo,
            data_prevista=nova_data_prevista,
            renovacoes=emprestimo.renovacoes + 1,
        )
        self._emprestimos[isbn] = novo
        return novo

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        lista = [
            emp for emp in self._emprestimos.values() if emp.data_prevista < data
        ]
        lista.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return lista
