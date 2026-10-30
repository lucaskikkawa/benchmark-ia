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
    def __init__(self, acervo: Acervo, limite_por_usuario: int = 3,
                 prazo_dias: int = 14, multa_diaria: float = 1.0,
                 max_renovacoes: int = 2):
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
        self._ativos = {}

    def emprestar(self, isbn: str, usuario: str, data: datetime.date) -> Emprestimo:
        self._acervo.obter(isbn)
        if isbn in self._ativos:
            raise LivroIndisponivel(f"Livro já emprestado: {isbn}")
        if sum(e.usuario == usuario for e in self._ativos.values()) >= self._limite_por_usuario:
            raise LimiteEmprestimos(f"Limite de empréstimos atingido para {usuario}")
        emprestimo = Emprestimo(isbn, usuario, data,
                               data + datetime.timedelta(days=self._prazo_dias))
        self._ativos[isbn] = emprestimo
        return emprestimo

    def devolver(self, isbn: str, data: datetime.date) -> float:
        self._acervo.obter(isbn)
        emprestimo = self._obter_ativo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data não pode ser anterior ao empréstimo")
        atraso = max(0, (data - emprestimo.data_prevista).days)
        del self._ativos[isbn]
        return round(atraso * self._multa_diaria, 2)

    def disponivel(self, isbn: str) -> bool:
        self._acervo.obter(isbn)
        return isbn not in self._ativos

    def emprestimos_de(self, usuario: str) -> list[Emprestimo]:
        return sorted((e for e in self._ativos.values() if e.usuario == usuario),
                      key=lambda e: (e.data_prevista, e.isbn))

    def renovar(self, isbn: str, data: datetime.date) -> Emprestimo:
        self._acervo.obter(isbn)
        emprestimo = self._obter_ativo(isbn)
        if data < emprestimo.data_emprestimo:
            raise ValueError("data não pode ser anterior ao empréstimo")
        if data > emprestimo.data_prevista or emprestimo.renovacoes >= self._max_renovacoes:
            raise RenovacaoNegada(f"Renovação negada para {isbn}")
        nova_previsao = max(emprestimo.data_prevista,
                            data + datetime.timedelta(days=self._prazo_dias))
        renovado = Emprestimo(emprestimo.isbn, emprestimo.usuario,
                              emprestimo.data_emprestimo, nova_previsao,
                              emprestimo.renovacoes + 1)
        self._ativos[isbn] = renovado
        return renovado

    def atrasados(self, data: datetime.date) -> list[Emprestimo]:
        return sorted((e for e in self._ativos.values() if e.data_prevista < data),
                      key=lambda e: (e.data_prevista, e.isbn))

    def _obter_ativo(self, isbn: str) -> Emprestimo:
        try:
            return self._ativos[isbn]
        except KeyError:
            raise EmprestimoNaoEncontrado(f"Empréstimo não encontrado: {isbn}") from None
