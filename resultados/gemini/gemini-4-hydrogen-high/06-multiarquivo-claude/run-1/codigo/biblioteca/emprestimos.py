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
    """Gerencia empréstimos, devoluções, renovações e consultas de disponibilidade."""

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

    def _garantir_livro_no_acervo(self, isbn: str) -> None:
        if isbn not in self._acervo:
            raise LivroNaoEncontrado(f"livro {isbn!r} não encontrado no acervo")

    def _obter_emprestimo_ativo(self, isbn: str) -> Emprestimo:
        self._garantir_livro_no_acervo(isbn)
        emprestimo = self._ativos.get(isbn)
        if emprestimo is None:
            raise EmprestimoNaoEncontrado(
                f"não há empréstimo ativo para o livro {isbn!r}"
            )
        return emprestimo

    def emprestar(self, isbn: str, usuario: str, data: datetime.date) -> Emprestimo:
        """Registra um novo empréstimo para o usuário na data informada."""
        self._garantir_livro_no_acervo(isbn)
        if isbn in self._ativos:
            raise LivroIndisponivel(f"livro {isbn!r} já está emprestado")

        ativos_usuario = sum(
            1 for emp in self._ativos.values() if emp.usuario == usuario
        )
        if ativos_usuario >= self._limite_por_usuario:
            raise LimiteEmprestimos(
                f"usuário {usuario!r} atingiu o limite de empréstimos"
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
        """Encerra o empréstimo ativo do livro e retorna a multa calculada."""
        emprestimo = self._obter_emprestimo_ativo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data de devolução anterior à data do empréstimo")

        dias_atraso = max(0, (data - emprestimo.data_prevista).days)
        multa = round(dias_atraso * self._multa_diaria, 2)
        del self._ativos[isbn]
        return multa

    def disponivel(self, isbn: str) -> bool:
        """Informa se o livro do acervo está disponível para empréstimo."""
        self._garantir_livro_no_acervo(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        """Lista os empréstimos ativos do usuário ordenados por data_prevista e isbn."""
        ativos = [emp for emp in self._ativos.values() if emp.usuario == usuario]
        ativos.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return ativos

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        """Renova o empréstimo ativo do livro, atualizando renovacoes e data_prevista."""
        emprestimo = self._obter_emprestimo_ativo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data de renovação anterior à data do empréstimo")
        if (
            data > emprestimo.data_prevista
            or emprestimo.renovacoes >= self._max_renovacoes
        ):
            raise RenovacaoNegada("renovação não permitida")

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
        """Lista todos os empréstimos ativos com data_prevista < data."""
        atrasados = [
            emp for emp in self._ativos.values() if emp.data_prevista < data
        ]
        atrasados.sort(key=lambda emp: (emp.data_prevista, emp.isbn))
        return atrasados
