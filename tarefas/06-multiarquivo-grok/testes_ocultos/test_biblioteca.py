from pathlib import Path

import pytest

from biblioteca import Catalogo, ErroBiblioteca, Livro, ServicoEmprestimos

ISBN_A = "9780000000001"
ISBN_B = "9780000000002"


def _catalogo():
    catalogo = Catalogo()
    catalogo.adicionar(Livro(ISBN_A, "  Dom Casmurro ", 1))
    catalogo.adicionar(Livro(ISBN_B, "Policarpo", 2))
    return catalogo


def test_livro_normaliza_titulo_e_rejeita_isbn():
    livro = Livro(ISBN_A, "  Dom Casmurro ", 1)
    assert livro.titulo == "Dom Casmurro"
    assert livro.exemplares == 1
    for isbn in ("978000000000", "97800000000011", "978-0000000001", "978000000000a", " 9780000000001"):
        with pytest.raises(ErroBiblioteca):
            Livro(isbn, "Titulo", 1)
    with pytest.raises(ErroBiblioteca):
        Livro(ISBN_A, "   ", 1)
    with pytest.raises(ErroBiblioteca):
        Livro(ISBN_A, "Titulo", 0)
    with pytest.raises(ErroBiblioteca):
        Livro(ISBN_A, "Titulo", True)
    with pytest.raises(ErroBiblioteca):
        Livro(ISBN_A, "Titulo", 1.5)


def test_catalogo_busca_lista_e_duplicata():
    catalogo = _catalogo()
    assert catalogo.buscar(ISBN_A).titulo == "Dom Casmurro"
    assert [livro.isbn for livro in catalogo.listar()] == [ISBN_A, ISBN_B]
    with pytest.raises(ErroBiblioteca):
        catalogo.adicionar(Livro(ISBN_A, "Outro", 1))
    with pytest.raises(ErroBiblioteca):
        catalogo.buscar("9780000000099")
    with pytest.raises(ErroBiblioteca):
        catalogo.adicionar({"isbn": ISBN_A})


def test_emprestar_reduz_disponiveis_e_bloqueia_repeticao():
    servico = ServicoEmprestimos(_catalogo())
    assert servico.disponiveis(ISBN_B) == 2
    servico.emprestar(ISBN_B, "Ana", "2024-01-01")
    assert servico.disponiveis(ISBN_B) == 1
    servico.emprestar(ISBN_B, "Bruno", "2024-01-02")
    assert servico.disponiveis(ISBN_B) == 0
    with pytest.raises(ErroBiblioteca):
        servico.emprestar(ISBN_B, "Carla", "2024-01-03")
    with pytest.raises(ErroBiblioteca):
        servico.emprestar(ISBN_B, " Ana ", "2024-01-04")


def test_dois_titulos_do_mesmo_usuario():
    servico = ServicoEmprestimos(_catalogo())
    servico.emprestar(ISBN_A, "Ana", "2024-03-01")
    servico.emprestar(ISBN_B, "Ana", "2024-03-01")
    assert servico.disponiveis(ISBN_A) == 0
    assert servico.disponiveis(ISBN_B) == 1


def test_atraso_no_prazo_e_depois():
    servico = ServicoEmprestimos(_catalogo())
    servico.emprestar(ISBN_A, "Ana", "2024-01-01")
    assert servico.devolver(ISBN_A, "Ana", "2024-01-01") == 0
    servico.emprestar(ISBN_A, "Ana", "2024-01-01")
    assert servico.devolver(ISBN_A, "Ana", "2024-01-15") == 0
    servico.emprestar(ISBN_A, "Ana", "2024-01-01")
    assert servico.devolver(ISBN_A, "Ana", "2024-01-16") == 1


def test_bissexto_e_data_anterior():
    servico = ServicoEmprestimos(_catalogo())
    servico.emprestar(ISBN_A, "Ana", "2024-02-29")
    assert servico.devolver(ISBN_A, "Ana", "2024-03-14") == 0
    servico.emprestar(ISBN_A, "Ana", "2024-02-29")
    assert servico.devolver(ISBN_A, "Ana", "2024-03-15") == 1
    servico.emprestar(ISBN_A, "Ana", "2024-02-29")
    with pytest.raises(ErroBiblioteca):
        servico.devolver(ISBN_A, "Ana", "2024-02-28")


def test_devolucao_libera_e_segunda_devolucao_falha():
    servico = ServicoEmprestimos(_catalogo())
    servico.emprestar(ISBN_A, "Ada Lovelace", "2024-04-01")
    with pytest.raises(ErroBiblioteca):
        servico.emprestar(ISBN_A, "Outra", "2024-04-02")
    assert servico.devolver(ISBN_A, "  Ada Lovelace ", "2024-04-10") == 0
    assert servico.disponiveis(ISBN_A) == 1
    servico.emprestar(ISBN_A, "Outra", "2024-04-11")
    with pytest.raises(ErroBiblioteca):
        servico.devolver(ISBN_A, "Ada Lovelace", "2024-04-12")
    with pytest.raises(ErroBiblioteca):
        servico.devolver(ISBN_B, "Ninguem", "2024-04-12")


def test_ativos_ordenados_e_sem_devolvidos():
    servico = ServicoEmprestimos(_catalogo())
    servico.emprestar(ISBN_B, "bruno", "2024-05-02")
    servico.emprestar(ISBN_A, "ana", "2024-05-02")
    servico.emprestar(ISBN_B, "ana", "2024-05-01")
    servico.devolver(ISBN_A, "ana", "2024-05-03")
    assert servico.ativos() == [
        (ISBN_B, "ana", "2024-05-01"),
        (ISBN_B, "bruno", "2024-05-02"),
    ]


def test_datas_e_usuarios_invalidos():
    servico = ServicoEmprestimos(_catalogo())
    with pytest.raises(ErroBiblioteca):
        servico.emprestar(ISBN_A, "   ", "2024-01-01")
    with pytest.raises(ErroBiblioteca):
        servico.emprestar(ISBN_A, "Ana", "2023-02-29")
    with pytest.raises(ErroBiblioteca):
        servico.emprestar(ISBN_A, "Ana", "2024-1-01")
    with pytest.raises(ErroBiblioteca):
        servico.emprestar("9780000000099", "Ana", "2024-01-01")
    with pytest.raises(ErroBiblioteca):
        servico.disponiveis("9780000000099")
    with pytest.raises(ErroBiblioteca):
        ServicoEmprestimos(object())


def test_api_publica_e_imports_relativos():
    import biblioteca

    assert biblioteca.Livro is Livro
    assert biblioteca.ErroBiblioteca is ErroBiblioteca
    assert issubclass(ErroBiblioteca, Exception)
    raiz = Path(__file__).resolve().parents[1] / "biblioteca"
    for nome in ("__init__.py", "catalogo.py", "emprestimos.py"):
        texto = (raiz / nome).read_text(encoding="utf-8")
        assert "from ." in texto
