from pathlib import Path

import pytest

from solucao import classificar_mensagem

RAIZ = Path(__file__).resolve().parents[1]


def _nucleo(texto):
    resultado = classificar_mensagem(texto)
    assert isinstance(resultado, dict)
    assert {"categoria", "urgente", "tamanho"} <= set(resultado)
    assert isinstance(resultado["categoria"], str) and resultado["categoria"] != ""
    assert isinstance(resultado["urgente"], bool)
    assert resultado["tamanho"] == len(texto)
    assert resultado["urgente"] is ("URGENTE" in texto)
    return resultado


def test_string_vazia():
    resultado = classificar_mensagem("")
    assert resultado["categoria"] == "vazia"
    assert resultado["urgente"] is False
    assert resultado["tamanho"] == 0


def test_somente_vazio_usa_categoria_vazia():
    for texto in (" ", "   ", "\n", "?", "olá", "URGENTE"):
        assert _nucleo(texto)["categoria"] != "vazia"


def test_urgente_e_substring_sensivel_a_maiusculas():
    assert _nucleo("URGENTE")["urgente"] is True
    assert _nucleo("URGENTE")["tamanho"] == 7
    assert _nucleo("algo URGENTE aqui")["urgente"] is True
    assert _nucleo("XURGENTEY")["urgente"] is True
    assert _nucleo(" URGENTE")["urgente"] is True
    assert _nucleo("urgente")["urgente"] is False
    assert _nucleo("Urgente")["urgente"] is False
    assert _nucleo("URGEN")["urgente"] is False


def test_tamanho_e_len_sem_strip():
    assert _nucleo("ação")["tamanho"] == 4
    assert _nucleo("🙂")["tamanho"] == 1
    assert _nucleo("a\nb")["tamanho"] == 3
    assert _nucleo("  ")["tamanho"] == 2
    assert _nucleo("Olá")["tamanho"] == 3


def test_tipos_invalidos():
    for valor in (None, b"URGENTE", 10, ["URGENTE"], 1.5):
        with pytest.raises(TypeError):
            classificar_mensagem(valor)


def test_deterministico():
    texto = "Preciso de ajuda URGENTE com o pedido"
    assert classificar_mensagem(texto) == classificar_mensagem(texto)
    primeiro = classificar_mensagem("só espaços não são vazio   ")
    segundo = classificar_mensagem("só espaços não são vazio   ")
    assert primeiro == segundo
    assert primeiro["tamanho"] == len("só espaços não são vazio   ")


def test_urgente_false_em_texto_comum():
    resultado = _nucleo("bom dia, tudo bem")
    assert resultado["urgente"] is False
    assert isinstance(resultado["categoria"], str)


def test_unicode_sem_normalizar_nem_medir_bytes():
    assert _nucleo("a\u0301")["tamanho"] == 2
    assert _nucleo("\u00a0")["tamanho"] == 1
    assert _nucleo("\u00a0")["categoria"] != "vazia"
    assert _nucleo("\u200b")["tamanho"] == 1
    assert _nucleo("\u200b")["urgente"] is False
    assert _nucleo("\ud800")["tamanho"] == 1
    assert _nucleo("\ud800")["urgente"] is False
    assert _nucleo("ação")["tamanho"] == 4
    assert len("ação".encode("utf-8")) != 4
    assert _nucleo("こんにちは")["tamanho"] == 5
    assert _nucleo("vazia")["categoria"] != "vazia"
    assert _nucleo("vazia")["tamanho"] == 5
    assert _nucleo("\n\n")["categoria"] != "vazia"


def test_lookalike_e_texto_longo():
    assert _nucleo("URGENT\u0415")["urgente"] is False
    assert _nucleo("URGENT\u0415")["tamanho"] == 7
    cauda = "a" * 100_000 + "URGENTE"
    resultado = _nucleo(cauda)
    assert resultado["urgente"] is True
    assert resultado["tamanho"] == 100_007
    assert resultado["categoria"] != "vazia"
    meio = "x" * 50_000 + "URGENTE" + "y" * 50_000
    assert _nucleo(meio)["urgente"] is True
    assert _nucleo(meio)["tamanho"] == 100_007
    assert _nucleo("UR\u200bGENTE")["urgente"] is False
    assert _nucleo("UR\u200bGENTE")["tamanho"] == 8


def test_tipos_de_bytes_e_determinismo_em_texto_grande():
    for valor in (bytearray(b"URGENTE"), memoryview(b"URGENTE")):
        with pytest.raises(TypeError):
            classificar_mensagem(valor)
    texto = "\ud800" + " " * 1000 + "urgente"
    assert classificar_mensagem(texto) == classificar_mensagem(texto)


def test_suposicoes_existe_e_tem_substancia():
    caminho = RAIZ / "SUPOSICOES.md"
    assert caminho.is_file(), "Arquivo SUPOSICOES.md não encontrado"
    texto = caminho.read_text(encoding="utf-8")
    linhas = [linha for linha in texto.splitlines() if linha.strip()]
    assert len(linhas) >= 2
    assert len(texto.strip()) >= 80
