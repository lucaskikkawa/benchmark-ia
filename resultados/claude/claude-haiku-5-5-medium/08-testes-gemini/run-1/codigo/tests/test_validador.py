import sys
from pathlib import Path

import pytest

# Garante que validador.py seja importável tanto na raiz do projeto quanto ao lado de tests/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validador import CARACTERES_ESPECIAIS_PERMITIDOS, ValidadorSenha  # noqa: E402


ESPECIAIS = "!@#$%^&*()-_+="


def senha_valida(tamanho: int) -> str:
    """Gera uma senha válida (sem triplicações e com todas as classes) do tamanho pedido."""
    prefixo = "Aa1!"
    corpo = "bcdefgh"
    resto = tamanho - len(prefixo)
    senha = prefixo + (corpo * (resto // len(corpo) + 1))[:resto]
    assert len(senha) == tamanho
    return senha


BASE_VALIDA = "Senha@123"  # 9 caracteres, válida


@pytest.fixture
def validador():
    return ValidadorSenha()


# ---------------------------------------------------------------------------
# Constante e construtor
# ---------------------------------------------------------------------------

def test_constante_caracteres_especiais_permitidos():
    assert CARACTERES_ESPECIAIS_PERMITIDOS == set("!@#$%^&*()-_+=")


def test_construtor_padrao_define_limites_8_e_64():
    v = ValidadorSenha()
    assert v.min_tam == 8
    assert v.max_tam == 64


def test_construtor_respeita_parametros_customizados():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert v.min_tam == 4
    assert v.max_tam == 6


def test_construtor_customizado_nao_troca_limites():
    # Valores distintos para detectar troca de min/max no __init__.
    v = ValidadorSenha(min_tam=3, max_tam=20)
    assert v.validar("Aa1!bcd")[0] is True  # 7 caracteres, dentro de [3, 20]
    assert v.validar("Aa1!bcdefghijklmnopqrs")[0] is False  # 21 caracteres > 20


# ---------------------------------------------------------------------------
# Retorno de validar
# ---------------------------------------------------------------------------

def test_validar_senha_valida_retorna_true_e_lista_vazia(validador):
    assert validador.validar(BASE_VALIDA) == (True, [])


def test_validar_retorna_tupla_bool_e_lista(validador):
    resultado = validador.validar("abc")
    assert isinstance(resultado, tuple)
    assert len(resultado) == 2
    assert isinstance(resultado[0], bool)
    assert isinstance(resultado[1], list)


def test_validar_senha_invalida_retorna_false_com_erros(validador):
    valida, erros = validador.validar("abc")
    assert valida is False
    assert len(erros) > 0


def test_validar_acumula_todos_os_erros(validador):
    # "a": curta (1 < 8), sem maiúscula, sem dígito, sem especial; tem minúscula e não tem espaço/triplicação.
    valida, erros = validador.validar("a")
    assert valida is False
    assert len(erros) == 4


def test_validar_acumula_erros_incluindo_triplicacao(validador):
    # "aaa": curta, sem maiúscula, sem dígito, sem especial e com triplicação => 5 erros.
    valida, erros = validador.validar("aaa")
    assert valida is False
    assert len(erros) == 5


def test_validar_nao_muta_senha_nem_estado(validador):
    antes = (validador.min_tam, validador.max_tam)
    validador.validar("abc")
    assert (validador.min_tam, validador.max_tam) == antes


# ---------------------------------------------------------------------------
# Regra 1: comprimento mínimo
# ---------------------------------------------------------------------------

def test_minimo_um_abaixo_do_limite_e_invalido(validador):
    senha = senha_valida(7)
    valida, erros = validador.validar(senha)
    assert valida is False
    assert len(erros) == 1


def test_minimo_exatamente_no_limite_e_valido(validador):
    senha = senha_valida(8)
    assert validador.validar(senha) == (True, [])


def test_minimo_customizado_no_limite_e_valido():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert v.validar("Aa1!") == (True, [])


def test_minimo_customizado_um_abaixo_e_invalido():
    v = ValidadorSenha(min_tam=5, max_tam=6)
    valida, erros = v.validar("Aa1!")  # 4 caracteres, todas as outras classes presentes
    assert valida is False
    assert len(erros) == 1


def test_minimo_erro_nao_depende_de_outras_regras_faltando():
    # Senha curta mas com todas as classes: deve gerar exatamente 1 erro (comprimento).
    v = ValidadorSenha(min_tam=10)
    valida, erros = v.validar("Aa1!bcdef")  # 9 caracteres
    assert valida is False
    assert len(erros) == 1


# ---------------------------------------------------------------------------
# Regra 2: comprimento máximo
# ---------------------------------------------------------------------------

def test_maximo_exatamente_no_limite_e_valido(validador):
    senha = senha_valida(64)
    assert validador.validar(senha) == (True, [])


def test_maximo_um_acima_do_limite_e_invalido(validador):
    senha = senha_valida(65)
    valida, erros = validador.validar(senha)
    assert valida is False
    assert len(erros) == 1


def test_maximo_customizado_no_limite_e_valido():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    assert v.validar("Aa1!bc") == (True, [])


def test_maximo_customizado_um_acima_e_invalido():
    v = ValidadorSenha(min_tam=4, max_tam=6)
    valida, erros = v.validar("Aa1!bcd")
    assert valida is False
    assert len(erros) == 1


def test_maximo_nao_afeta_senha_dentro_do_limite_default(validador):
    # Com max=64 padrão, uma senha de 63 caracteres é válida.
    assert validador.validar(senha_valida(63)) == (True, [])


# ---------------------------------------------------------------------------
# Regra 3: letra maiúscula
# ---------------------------------------------------------------------------

def test_sem_maiuscula_e_invalido(validador):
    valida, erros = validador.validar("senha@123")
    assert valida is False
    assert len(erros) == 1


def test_uma_maiuscula_basta(validador):
    assert validador.validar("senha@12A") == (True, [])


def test_maiuscula_no_fim_basta(validador):
    assert validador.validar("abcdefg1!Z") == (True, [])


# ---------------------------------------------------------------------------
# Regra 4: letra minúscula
# ---------------------------------------------------------------------------

def test_sem_minuscula_e_invalido(validador):
    valida, erros = validador.validar("SENHA@123")
    assert valida is False
    assert len(erros) == 1


def test_uma_minuscula_basta(validador):
    assert validador.validar("SENHA@12a") == (True, [])


# ---------------------------------------------------------------------------
# Regra 5: dígito
# ---------------------------------------------------------------------------

def test_sem_digito_e_invalido(validador):
    valida, erros = validador.validar("Senha@abc")
    assert valida is False
    assert len(erros) == 1


@pytest.mark.parametrize("digito", list("0123456789"))
def test_cada_digito_satisfaz_regra(validador, digito):
    senha = f"Senha@ab{digito}"
    assert validador.validar(senha) == (True, [])


def test_digito_nao_e_confundido_com_especial(validador):
    # Dígitos não são caracteres especiais permitidos.
    valida, erros = validador.validar("Senha123x")
    assert valida is False
    assert len(erros) == 1


# ---------------------------------------------------------------------------
# Regra 6: caractere especial permitido
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("especial", list(ESPECIAIS))
def test_cada_caractere_especial_permitido_satisfaz_regra(validador, especial):
    senha = f"Aa1{especial}bcdefg"
    assert validador.validar(senha) == (True, [])


@pytest.mark.parametrize("pontuacao", list("~.,/?;:'\"[]{}\\|<>`"))
def test_pontuacao_fora_do_conjunto_nao_conta(validador, pontuacao):
    senha = f"Aa1{pontuacao}bcdefg"
    valida, erros = validador.validar(senha)
    assert valida is False
    assert len(erros) == 1


def test_sem_especial_e_invalido(validador):
    valida, erros = validador.validar("Senha1234")
    assert valida is False
    assert len(erros) == 1


def test_especial_fora_do_conjunto_com_demais_regras_validas(validador):
    # Apenas "~" como especial: não basta.
    valida, erros = validador.validar("Senha~123")
    assert valida is False
    assert len(erros) == 1


def test_caractere_especial_nao_permitido_ainda_conta_se_houver_permitido(validador):
    assert validador.validar("Senha~123!") == (True, [])


def test_conjunto_especiais_tem_exatamente_14_caracteres():
    assert len(CARACTERES_ESPECIAIS_PERMITIDOS) == 14


# ---------------------------------------------------------------------------
# Regra 7: espaços em branco
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("branco", [" ", "\t", "\n", "\r", "\v", "\f"])
def test_espaco_em_branco_e_invalido(validador, branco):
    senha = f"Senha@12{branco}3"
    valida, erros = validador.validar(senha)
    assert valida is False
    assert len(erros) == 1


def test_espaco_no_inicio_e_invalido(validador):
    valida, erros = validador.validar(" Senha@123")
    assert valida is False
    assert len(erros) == 1


def test_espaco_no_fim_e_invalido(validador):
    valida, erros = validador.validar("Senha@123 ")
    assert valida is False
    assert len(erros) == 1


def test_senha_sem_espacos_e_valida(validador):
    assert validador.validar("Senha@123") == (True, [])


# ---------------------------------------------------------------------------
# Regra 8: triplicação de caracteres consecutivos
# ---------------------------------------------------------------------------

def test_duas_repeticoes_consecutivas_sao_validas(validador):
    assert validador.validar("Aa1!aabbcc") == (True, [])


def test_repeticoes_nao_consecutivas_sao_validas(validador):
    assert validador.validar("Aa1!aXaYa") == (True, [])


def test_sequencia_crescente_nao_e_repeticao(validador):
    assert validador.validar("Aa1!abcdef") == (True, [])


@pytest.mark.parametrize(
    "senha",
    [
        "zzzAa1!bcdef",      # no início
        "Aa1!zzzbcdef",      # no meio
        "Aa1!bcdefzzz",      # no fim
        "AAAa1!bcdef",       # maiúsculas repetidas
        "Aa1!!!bcdef",       # especiais repetidos
        "Aa!bcdef111",       # dígitos repetidos no fim
        "Aa1!bcdef1111",     # quatro repetidos (contém triplicação)
    ],
)
def test_triplicacao_em_qualquer_posicao_e_invalida(validador, senha):
    valida, erros = validador.validar(senha)
    assert valida is False
    assert len(erros) == 1


def test_triplicacao_no_fim_exatamente_detectada():
    # Garante detecção no último trio (índice len-3), não apenas até len-4.
    v = ValidadorSenha()
    valida, _ = v.validar("Aa1!bcdeff")  # sem triplicação
    assert valida is True
    valida, erros = v.validar("Aa1!bcdefff")
    assert valida is False
    assert len(erros) == 1


def test_triplicacao_no_inicio_exatamente_detectada():
    v = ValidadorSenha()
    valida, erros = v.validar("aaaA1!bcdef")
    assert valida is False
    assert len(erros) == 1


def test_triplicacao_sem_outros_erros_gera_um_erro(validador):
    # Todas as outras regras satisfeitas; só a triplicação viola.
    valida, erros = validador.validar("Aa1!bcdeeef")
    assert valida is False
    assert len(erros) == 1


# ---------------------------------------------------------------------------
# calcular_forca
# ---------------------------------------------------------------------------

def test_forca_invalida_quando_senha_invalida(validador):
    assert validador.calcular_forca("abc") == "invalida"


def test_forca_invalida_mesmo_com_tamanho_forte(validador):
    # Senha longa, mas com espaço: deve ser "invalida", não "forte".
    assert validador.calcular_forca("Aa1! bcdefghijklmnopq") == "invalida"


def test_forca_invalida_por_triplicacao_mesmo_longa(validador):
    assert validador.calcular_forca("Aa1!bcdefghijklmnzzz") == "invalida"


def test_forca_invalida_quando_excede_maximo(validador):
    assert validador.calcular_forca(senha_valida(65)) == "invalida"


def test_forca_invalida_quando_abaixo_do_minimo(validador):
    assert validador.calcular_forca(senha_valida(7)) == "invalida"


def test_forca_fraca_no_minimo_valido(validador):
    assert validador.calcular_forca(senha_valida(8)) == "fraca"


def test_forca_fraca_um_abaixo_de_10(validador):
    assert validador.calcular_forca(senha_valida(9)) == "fraca"


def test_forca_media_no_limite_inferior_10(validador):
    assert validador.calcular_forca(senha_valida(10)) == "media"


def test_forca_media_um_abaixo_de_14(validador):
    assert validador.calcular_forca(senha_valida(13)) == "media"


def test_forca_forte_no_limite_14(validador):
    assert validador.calcular_forca(senha_valida(14)) == "forte"


def test_forca_forte_no_maximo_64(validador):
    assert validador.calcular_forca(senha_valida(64)) == "forte"


def test_forca_retorna_string(validador):
    assert isinstance(validador.calcular_forca(BASE_VALIDA), str)


def test_forca_usa_comprimento_da_senha_e_nao_min_customizado():
    # Limites de força são fixos (10 e 14), independentes de min_tam.
    v = ValidadorSenha(min_tam=1, max_tam=64)
    assert v.calcular_forca("Aa1!bcdefg") == "media"  # 10 caracteres
    assert v.calcular_forca("Aa1!bcdef") == "fraca"   # 9 caracteres


def test_forca_respeita_max_customizado():
    v = ValidadorSenha(min_tam=4, max_tam=12)
    assert v.calcular_forca(senha_valida(12)) == "media"
    assert v.calcular_forca(senha_valida(13)) == "invalida"
