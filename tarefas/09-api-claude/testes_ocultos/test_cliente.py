import pytest

from cliente import ClienteAPI, ErroAPI, FalhaPermanente, NaoEncontrado
from fake_api import ErroConexao, FakeAPI, Resposta, TempoEsgotado


class Dormir:
    """Substituto de time.sleep que só registra as esperas."""

    def __init__(self):
        self.esperas = []

    def __call__(self, segundos):
        self.esperas.append(segundos)


class APIScript:
    """API falsa que devolve/levanta itens de uma lista, em ordem."""

    def __init__(self, itens):
        self.itens = list(itens)
        self.chamadas = []

    def requisitar(self, metodo, caminho, timeout):
        self.chamadas.append((metodo, caminho, timeout))
        item = self.itens.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def cliente(api, **kwargs):
    dormir = Dormir()
    return ClienteAPI(api, dormir=dormir, **kwargs), dormir


def test_sucesso_primeira_tentativa():
    api = FakeAPI(roteiro=[])
    c, dormir = cliente(api)
    assert c.obter_usuario(7) == {"id": 7, "nome": "Usuario 7"}
    assert api.chamadas == [("GET", "/usuarios/7", 2.0)]
    assert dormir.esperas == []


def test_timeout_repassado_para_api():
    api = FakeAPI(roteiro=[])
    c, _ = cliente(api, timeout=0.75)
    c.obter_usuario(1)
    assert api.chamadas[0][2] == 0.75


def test_retry_com_backoff_exponencial():
    api = FakeAPI(roteiro=["500", "503", "conexao", "ok"])
    c, dormir = cliente(api, max_tentativas=4, backoff_base=0.5)
    assert c.obter_usuario(3)["id"] == 3
    assert len(api.chamadas) == 4
    assert dormir.esperas == [0.5, 1.0, 2.0]


def test_backoff_limitado_por_backoff_max():
    api = FakeAPI(roteiro=["500"] * 5)
    c, dormir = cliente(api, max_tentativas=6, backoff_base=1.0, backoff_max=3.0)
    c.obter_usuario(1)
    assert dormir.esperas == [1.0, 2.0, 3.0, 3.0, 3.0]


def test_lentidao_maior_que_timeout_e_retentada():
    api = FakeAPI(roteiro=["lento", "ok"], latencia_lenta=5.0)
    c, dormir = cliente(api, timeout=2.0)
    assert c.obter_usuario(2)["id"] == 2
    assert api.eventos == ["lento", "ok"]
    assert dormir.esperas == [0.5]


def test_lentidao_dentro_do_timeout_nao_retenta():
    api = FakeAPI(roteiro=["lento"], latencia_lenta=1.0)
    c, dormir = cliente(api, timeout=2.0)
    assert c.obter_usuario(2)["id"] == 2
    assert len(api.chamadas) == 1 and dormir.esperas == []


def test_429_usa_retry_after():
    api = FakeAPI(roteiro=["429", "ok"], retry_after="2")
    c, dormir = cliente(api, backoff_base=0.5)
    c.obter_usuario(1)
    assert dormir.esperas == [2.0]


def test_429_retry_after_decimal_limitado_e_invalido():
    api = FakeAPI(roteiro=["429", "ok"], retry_after="1.5")
    c, dormir = cliente(api)
    c.obter_usuario(1)
    assert dormir.esperas == [1.5]

    api = FakeAPI(roteiro=["429", "ok"], retry_after="60")
    c, dormir = cliente(api, backoff_max=8.0)
    c.obter_usuario(1)
    assert dormir.esperas == [8.0]

    api = FakeAPI(roteiro=["500", "429", "ok"], retry_after="abc")
    c, dormir = cliente(api, backoff_base=0.5)
    c.obter_usuario(1)
    assert dormir.esperas == [0.5, 1.0]


def test_429_sem_header():
    api = APIScript([Resposta(429, {}, {}), Resposta(200, {"id": 1})])
    c, dormir = cliente(api, backoff_base=0.25)
    assert c.obter_usuario(1) == {"id": 1}
    assert dormir.esperas == [0.25]


def test_502_e_504_retentaveis():
    api = APIScript([Resposta(502), Resposta(504), Resposta(200, {"id": 9})])
    c, dormir = cliente(api)
    assert c.obter_usuario(9) == {"id": 9}
    assert len(dormir.esperas) == 2


def test_falha_permanente_sem_dormir_apos_ultima():
    api = FakeAPI(roteiro=["500"] * 10)
    c, dormir = cliente(api, max_tentativas=3)
    with pytest.raises(FalhaPermanente) as info:
        c.obter_usuario(1)
    assert info.value.tentativas == 3
    assert isinstance(info.value, ErroAPI)
    assert len(api.chamadas) == 3
    assert dormir.esperas == [0.5, 1.0]


def test_falha_permanente_encadeia_excecao():
    api = FakeAPI(roteiro=["500", "conexao"])
    c, _ = cliente(api, max_tentativas=2)
    with pytest.raises(FalhaPermanente) as info:
        c.obter_usuario(1)
    assert isinstance(info.value.__cause__, ErroConexao)

    api = FakeAPI(roteiro=["lento"])
    c, dormir = cliente(api, max_tentativas=1)
    with pytest.raises(FalhaPermanente) as info:
        c.obter_usuario(1)
    assert isinstance(info.value.__cause__, TempoEsgotado)
    assert dormir.esperas == []


def test_404_sem_retry():
    api = FakeAPI(roteiro=[])
    c, dormir = cliente(api)
    with pytest.raises(NaoEncontrado):
        c.obter_usuario(5000)
    assert len(api.chamadas) == 1 and dormir.esperas == []


def test_outro_4xx_sem_retry():
    api = APIScript([Resposta(400, {"erro": "x"}), Resposta(200, {"id": 1})])
    c, dormir = cliente(api)
    with pytest.raises(ErroAPI) as info:
        c.obter_usuario(1)
    assert not isinstance(info.value, (NaoEncontrado, FalhaPermanente))
    assert len(api.chamadas) == 1 and dormir.esperas == []


def test_excecao_desconhecida_propaga_sem_retry():
    api = APIScript([RuntimeError("bug"), Resposta(200, {"id": 1})])
    c, dormir = cliente(api)
    with pytest.raises(RuntimeError):
        c.obter_usuario(1)
    assert len(api.chamadas) == 1 and dormir.esperas == []


@pytest.mark.parametrize("id_invalido", [0, -1, "1", 1.0, None, True])
def test_id_invalido_sem_requisicao(id_invalido):
    api = FakeAPI(roteiro=[])
    c, _ = cliente(api)
    with pytest.raises(ValueError):
        c.obter_usuario(id_invalido)
    assert api.chamadas == []


@pytest.mark.parametrize(
    "kwargs",
    [{"max_tentativas": 0}, {"timeout": 0}, {"timeout": -1}, {"backoff_base": -0.1}, {"backoff_max": -1}],
)
def test_parametros_invalidos(kwargs):
    with pytest.raises(ValueError):
        ClienteAPI(FakeAPI(), **kwargs)


def test_obter_varios():
    api = FakeAPI(roteiro=["500"])
    c, _ = cliente(api)
    resultado = c.obter_varios([3, 2000, 1, 3])
    assert list(resultado) == [3, 2000, 1]
    assert resultado == {3: {"id": 3, "nome": "Usuario 3"}, 2000: None, 1: {"id": 1, "nome": "Usuario 1"}}
    assert [ch[1] for ch in api.chamadas] == ["/usuarios/3", "/usuarios/3", "/usuarios/2000", "/usuarios/1"]


def test_obter_varios_propaga_falha_permanente():
    api = FakeAPI(roteiro=["ok", "500", "500"])
    c, _ = cliente(api, max_tentativas=2)
    with pytest.raises(FalhaPermanente):
        c.obter_varios([1, 2, 3])


def test_obter_varios_propaga_value_error():
    api = FakeAPI(roteiro=[])
    c, _ = cliente(api)
    with pytest.raises(ValueError):
        c.obter_varios([1, 0])


def test_hierarquia_de_excecoes():
    assert issubclass(NaoEncontrado, ErroAPI)
    assert issubclass(FalhaPermanente, ErroAPI)


def test_4xx_no_meio_do_retry_nao_e_falha_permanente():
    api = APIScript([Resposta(503), Resposta(400, {"erro": "x"}), Resposta(200, {"id": 1})])
    c, dormir = cliente(api, backoff_base=0.5)
    with pytest.raises(ErroAPI) as info:
        c.obter_usuario(1)
    assert not isinstance(info.value, (NaoEncontrado, FalhaPermanente))
    assert len(api.chamadas) == 2
    assert dormir.esperas == [0.5]


def test_deterministico_por_seed():
    def rodar():
        api = FakeAPI(seed=3, taxa_falha=0.5)
        c, dormir = cliente(api, max_tentativas=8)
        return c.obter_varios(range(1, 31)), api, dormir

    resultado, api, dormir = rodar()
    assert resultado == {i: {"id": i, "nome": f"Usuario {i}"} for i in range(1, 31)}
    # Com seed 3 um cliente correto faz exatamente 58 requisições (28 falhas retentadas).
    assert len(api.chamadas) == 58
    assert len(dormir.esperas) == 58 - 30
    assert all(0 <= e <= 8.0 for e in dormir.esperas)
    _, api2, dormir2 = rodar()
    assert api2.eventos == api.eventos and dormir2.esperas == dormir.esperas


def test_seed_com_falhas_consecutivas_esgota_tentativas():
    api = FakeAPI(seed=7, taxa_falha=0.5)
    c, _ = cliente(api, max_tentativas=8)
    with pytest.raises(FalhaPermanente) as info:
        c.obter_varios(range(1, 31))
    assert info.value.tentativas == 8
