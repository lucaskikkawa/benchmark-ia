import dataclasses
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from biblioteca import (
    Acervo,
    BibliotecaErro,
    Emprestimo,
    EmprestimoNaoEncontrado,
    LimiteEmprestimos,
    Livro,
    LivroIndisponivel,
    LivroNaoEncontrado,
    RenovacaoNegada,
    ServicoEmprestimos,
)

PACOTE = Path(__file__).resolve().parent.parent / "biblioteca"
D0 = date(2024, 3, 1)


@pytest.fixture
def acervo():
    a = Acervo()
    a.adicionar(Livro("1", "Dom Casmurro", "Machado de Assis"))
    a.adicionar(Livro("2", "Memórias Póstumas", "Machado de Assis"))
    a.adicionar(Livro("3", "Vidas Secas", "Graciliano Ramos"))
    a.adicionar(Livro("4", "A Hora da Estrela", "Clarice Lispector"))
    a.adicionar(Livro("5", "Angústia", "Graciliano Ramos"))
    return a


@pytest.fixture
def servico(acervo):
    return ServicoEmprestimos(acervo)


def test_estrutura_do_pacote():
    nomes = sorted(
        p.name for p in PACOTE.iterdir() if p.name != "__pycache__" and not p.name.endswith(".pyc")
    )
    assert nomes == ["__init__.py", "acervo.py", "emprestimos.py", "modelos.py"]


def test_submodulos_e_imports_relativos():
    from biblioteca import acervo, emprestimos, modelos

    assert acervo.Acervo is Acervo
    assert emprestimos.ServicoEmprestimos is ServicoEmprestimos
    assert modelos.Livro is Livro and modelos.Emprestimo is Emprestimo
    for nome in ("__init__.py", "acervo.py", "emprestimos.py"):
        fonte = (PACOTE / nome).read_text(encoding="utf-8")
        assert "from ." in fonte, f"{nome} deve usar import relativo"
        assert "from biblioteca" not in fonte and "import biblioteca" not in fonte


def test_importavel_de_outro_diretorio(tmp_path):
    codigo = f"import sys; sys.path.insert(0, {str(PACOTE.parent)!r}); import biblioteca; print(biblioteca.Acervo.__name__)"
    r = subprocess.run([sys.executable, "-c", codigo], cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "Acervo"


def test_modelos_sao_dataclasses_imutaveis():
    livro = Livro("9", "T", "A")
    assert dataclasses.is_dataclass(livro)
    with pytest.raises(dataclasses.FrozenInstanceError):
        livro.titulo = "Outro"
    assert Livro("9", "T", "A") == livro
    emprestimo = Emprestimo("9", "ana", D0, D0)
    assert dataclasses.is_dataclass(emprestimo)
    with pytest.raises(dataclasses.FrozenInstanceError):
        emprestimo.usuario = "bia"


def test_hierarquia_de_excecoes():
    for exc in (LivroNaoEncontrado, LivroIndisponivel, LimiteEmprestimos, EmprestimoNaoEncontrado, RenovacaoNegada):
        assert issubclass(exc, BibliotecaErro)
    assert issubclass(BibliotecaErro, Exception)


def test_acervo_basico(acervo):
    assert len(acervo) == 5
    assert "3" in acervo and "99" not in acervo
    assert acervo.obter("3").titulo == "Vidas Secas"
    with pytest.raises(LivroNaoEncontrado):
        acervo.obter("99")


def test_acervo_isbn_duplicado(acervo):
    with pytest.raises(ValueError):
        acervo.adicionar(Livro("1", "Outro", "Outro"))
    assert len(acervo) == 5


def test_buscar_por_autor(acervo):
    assert [l.titulo for l in acervo.buscar_por_autor("graciliano")] == ["Angústia", "Vidas Secas"]
    assert [l.isbn for l in acervo.buscar_por_autor("ASSIS")] == ["1", "2"]
    assert acervo.buscar_por_autor("Tolstói") == []


def test_buscar_por_autor_desempata_por_isbn():
    a = Acervo()
    a.adicionar(Livro("b", "Mesmo", "X"))
    a.adicionar(Livro("a", "Mesmo", "X"))
    assert [l.isbn for l in a.buscar_por_autor("x")] == ["a", "b"]


def test_emprestar(servico):
    e = servico.emprestar("1", "ana", D0)
    assert e == Emprestimo("1", "ana", D0, D0 + timedelta(days=14))
    assert servico.disponivel("1") is False
    assert servico.disponivel("2") is True


def test_emprestar_erros(servico):
    with pytest.raises(LivroNaoEncontrado):
        servico.emprestar("99", "ana", D0)
    servico.emprestar("1", "ana", D0)
    with pytest.raises(LivroIndisponivel):
        servico.emprestar("1", "bia", D0)


def test_limite_por_usuario(acervo):
    s = ServicoEmprestimos(acervo, limite_por_usuario=2)
    s.emprestar("1", "ana", D0)
    s.emprestar("2", "ana", D0)
    with pytest.raises(LimiteEmprestimos):
        s.emprestar("3", "ana", D0)
    assert s.disponivel("3")
    s.emprestar("3", "bia", D0)  # limite é por usuário
    s.devolver("1", D0)
    s.emprestar("4", "ana", D0)  # liberou vaga


def test_ordem_das_verificacoes(acervo):
    s = ServicoEmprestimos(acervo, limite_por_usuario=1)
    s.emprestar("1", "ana", D0)
    with pytest.raises(LivroIndisponivel):
        s.emprestar("1", "ana", D0)  # indisponível vem antes do limite
    with pytest.raises(LivroNaoEncontrado):
        s.emprestar("99", "ana", D0)  # inexistente vem antes do limite


def test_limite_e_multa_padrao(acervo):
    s = ServicoEmprestimos(acervo)
    for isbn in ("1", "2", "3"):
        s.emprestar(isbn, "ana", D0)
    with pytest.raises(LimiteEmprestimos):
        s.emprestar("4", "ana", D0)
    assert s.disponivel("4") is True
    # prazo padrão 14 dias; 2 dias de atraso * multa padrão 1.0
    assert s.devolver("1", D0 + timedelta(days=16)) == 2.0


def test_devolver_no_prazo_e_com_atraso(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=7, multa_diaria=2.5)
    s.emprestar("1", "ana", D0)
    assert s.devolver("1", D0 + timedelta(days=7)) == 0.0
    s.emprestar("1", "ana", D0)
    assert s.devolver("1", D0 + timedelta(days=10)) == 7.5
    assert s.disponivel("1")


def test_devolver_multa_arredondada(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=1, multa_diaria=0.1)
    s.emprestar("1", "ana", D0)
    assert s.devolver("1", D0 + timedelta(days=4)) == 0.3


def test_devolver_erros(servico):
    with pytest.raises(LivroNaoEncontrado):
        servico.devolver("99", D0)
    with pytest.raises(EmprestimoNaoEncontrado):
        servico.devolver("1", D0)
    servico.emprestar("1", "ana", D0)
    with pytest.raises(ValueError):
        servico.devolver("1", D0 - timedelta(days=1))
    assert servico.disponivel("1") is False  # continua emprestado
    assert servico.devolver("1", D0) == 0.0


def test_disponivel_isbn_inexistente(servico):
    with pytest.raises(LivroNaoEncontrado):
        servico.disponivel("99")


def test_emprestimos_de_ordenado(servico):
    servico.emprestar("3", "ana", D0 + timedelta(days=2))
    servico.emprestar("2", "ana", D0)
    servico.emprestar("1", "ana", D0)
    servico.emprestar("4", "bia", D0)
    assert [e.isbn for e in servico.emprestimos_de("ana")] == ["1", "2", "3"]
    assert servico.emprestimos_de("ninguem") == []


# ---- requisitos adicionais ----

def test_all_exato():
    import biblioteca

    assert sorted(biblioteca.__all__) == sorted([
        "Livro", "Emprestimo", "Acervo", "ServicoEmprestimos", "BibliotecaErro", "LivroNaoEncontrado",
        "LivroIndisponivel", "LimiteEmprestimos", "EmprestimoNaoEncontrado", "RenovacaoNegada",
    ])
    assert len(biblioteca.__all__) == 10


def test_emprestimo_campo_renovacoes():
    e = Emprestimo("9", "ana", D0, D0)
    assert e.renovacoes == 0
    assert [f.name for f in dataclasses.fields(Emprestimo)] == [
        "isbn", "usuario", "data_emprestimo", "data_prevista", "renovacoes"
    ]


def test_livro_valida_campos():
    for args in [("", "T", "A"), ("1", "   ", "A"), ("1", "T", "\t\n")]:
        with pytest.raises(ValueError):
            Livro(*args)
    for args in [(1, "T", "A"), ("1", None, "A"), ("1", "T", b"A")]:
        with pytest.raises(TypeError):
            Livro(*args)


def test_adicionar_nao_livro(acervo):
    with pytest.raises(TypeError):
        acervo.adicionar(("6", "T", "A"))
    assert len(acervo) == 5


def test_buscar_por_autor_casefold_e_trecho_vazio():
    a = Acervo()
    a.adicionar(Livro("1", "Valsas", "Johann Strauß"))
    a.adicionar(Livro("2", "Óperas", "ÉMILE ZOLA"))
    a.adicionar(Livro("3", "Contos", "Ana"))
    assert [l.isbn for l in a.buscar_por_autor("STRAUSS")] == ["1"]
    assert [l.isbn for l in a.buscar_por_autor("émile")] == ["2"]
    assert [l.isbn for l in a.buscar_por_autor("")] == ["3", "1", "2"]  # "Óperas" > "Valsas" (str)


@pytest.mark.parametrize(
    "kwargs",
    [{"limite_por_usuario": 0}, {"prazo_dias": 0}, {"prazo_dias": -3}, {"multa_diaria": -0.5}, {"max_renovacoes": -1}],
)
def test_construtor_valida_parametros(acervo, kwargs):
    with pytest.raises(ValueError):
        ServicoEmprestimos(acervo, **kwargs)


def test_construtor_aceita_limites(acervo):
    ServicoEmprestimos(acervo, limite_por_usuario=1, prazo_dias=1, multa_diaria=0, max_renovacoes=0)


def test_servico_usa_o_mesmo_acervo(acervo):
    s = ServicoEmprestimos(acervo)
    acervo.adicionar(Livro("10", "Novo", "Autor"))
    assert s.disponivel("10") is True
    assert s.emprestar("10", "ana", D0).isbn == "10"


def test_renovar_basico(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=10)
    s.emprestar("1", "ana", D0)
    r = s.renovar("1", D0 + timedelta(days=4))
    assert r == Emprestimo("1", "ana", D0, D0 + timedelta(days=14), 1)
    assert s.emprestimos_de("ana") == [r]
    assert s.disponivel("1") is False


def test_renovar_nunca_encurta_o_prazo(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=10)
    s.emprestar("1", "ana", D0)
    s.renovar("1", D0 + timedelta(days=8))            # prevista: D0+18
    r = s.renovar("1", D0 + timedelta(days=1))        # D0+11 < D0+18 -> mantém
    assert r.data_prevista == D0 + timedelta(days=18)
    assert r.renovacoes == 2


def test_renovar_no_dia_previsto_e_permitido(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=7)
    s.emprestar("1", "ana", D0)
    r = s.renovar("1", D0 + timedelta(days=7))
    assert r.data_prevista == D0 + timedelta(days=14)


def test_renovar_atrasado_e_negado_sem_alterar(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=7)
    original = s.emprestar("1", "ana", D0)
    with pytest.raises(RenovacaoNegada):
        s.renovar("1", D0 + timedelta(days=8))
    assert s.emprestimos_de("ana") == [original]


def test_renovar_limite_de_renovacoes(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=7)  # max_renovacoes padrão = 2
    s.emprestar("1", "ana", D0)
    s.renovar("1", D0 + timedelta(days=1))
    antes = s.renovar("1", D0 + timedelta(days=2))
    with pytest.raises(RenovacaoNegada):
        s.renovar("1", D0 + timedelta(days=3))
    assert s.emprestimos_de("ana") == [antes]

    a = Acervo()
    a.adicionar(Livro("x", "T", "A"))
    s0 = ServicoEmprestimos(a, max_renovacoes=0)
    s0.emprestar("x", "bia", D0)
    with pytest.raises(RenovacaoNegada):
        s0.renovar("x", D0)


def test_renovar_erros_na_ordem(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=7)
    with pytest.raises(LivroNaoEncontrado):
        s.renovar("99", D0)
    with pytest.raises(EmprestimoNaoEncontrado):
        s.renovar("1", D0)
    s.emprestar("1", "ana", D0 + timedelta(days=5))
    with pytest.raises(ValueError):
        s.renovar("1", D0)
    assert s.emprestimos_de("ana")[0].renovacoes == 0


def test_devolver_usa_prazo_renovado(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=10, multa_diaria=2.0)
    s.emprestar("1", "ana", D0)
    s.renovar("1", D0 + timedelta(days=10))           # prevista: D0+20
    assert s.devolver("1", D0 + timedelta(days=20)) == 0.0
    s.emprestar("1", "ana", D0)
    s.renovar("1", D0 + timedelta(days=5))            # prevista: D0+15
    assert s.devolver("1", D0 + timedelta(days=18)) == 6.0


def test_emprestimos_de_reordena_apos_renovar(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=10)
    s.emprestar("1", "ana", D0)
    s.emprestar("2", "ana", D0 + timedelta(days=3))
    s.renovar("1", D0 + timedelta(days=9))            # "1" vence em D0+19, depois de "2" (D0+13)
    assert [e.isbn for e in s.emprestimos_de("ana")] == ["2", "1"]


def test_atrasados(acervo):
    s = ServicoEmprestimos(acervo, prazo_dias=5)
    s.emprestar("3", "ana", D0)                       # vence D0+5
    s.emprestar("1", "bia", D0)                       # vence D0+5
    s.emprestar("2", "caio", D0 + timedelta(days=2))  # vence D0+7
    s.emprestar("4", "ana", D0 + timedelta(days=10))  # vence D0+15
    assert s.atrasados(D0 + timedelta(days=5)) == []
    assert [e.isbn for e in s.atrasados(D0 + timedelta(days=6))] == ["1", "3"]
    assert [e.isbn for e in s.atrasados(D0 + timedelta(days=30))] == ["1", "3", "2", "4"]
    s.devolver("1", D0 + timedelta(days=6))
    s.renovar("2", D0 + timedelta(days=7))            # vence D0+12
    assert [e.isbn for e in s.atrasados(D0 + timedelta(days=8))] == ["3"]
