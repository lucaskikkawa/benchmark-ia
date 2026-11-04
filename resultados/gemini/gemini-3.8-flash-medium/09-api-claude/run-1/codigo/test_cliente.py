import math
import pytest
from fake_api import FakeAPI, ErroConexao, TempoEsgotado, Resposta
from cliente import ClienteAPI, ErroAPI, NaoEncontrado, FalhaPermanente


class MockAPI:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def requisitar(self, metodo, caminho, timeout):
        self.calls.append((metodo, caminho, timeout))
        if not self.responses:
            return Resposta(200, {"id": 1, "nome": "Usuario 1"})
        resp = self.responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


def test_init_validations():
    api = FakeAPI()
    # max_tentativas
    with pytest.raises(ValueError):
        ClienteAPI(api, max_tentativas=0)
    with pytest.raises(ValueError):
        ClienteAPI(api, max_tentativas=-1)
    with pytest.raises(ValueError):
        ClienteAPI(api, max_tentativas=True)
    with pytest.raises(ValueError):
        ClienteAPI(api, max_tentativas=1.5)

    # timeout
    with pytest.raises(ValueError):
        ClienteAPI(api, timeout=0)
    with pytest.raises(ValueError):
        ClienteAPI(api, timeout=-1.0)
    with pytest.raises(ValueError):
        ClienteAPI(api, timeout=True)
    with pytest.raises(ValueError):
        ClienteAPI(api, timeout=float("nan"))

    # backoff_base
    with pytest.raises(ValueError):
        ClienteAPI(api, backoff_base=-0.1)
    with pytest.raises(ValueError):
        ClienteAPI(api, backoff_base=True)
    with pytest.raises(ValueError):
        ClienteAPI(api, backoff_base=float("nan"))
    # backoff_base == 0 is valid
    c = ClienteAPI(api, backoff_base=0)
    assert c.backoff_base == 0.0

    # backoff_max
    with pytest.raises(ValueError):
        ClienteAPI(api, backoff_max=-0.1)
    with pytest.raises(ValueError):
        ClienteAPI(api, backoff_max=True)
    with pytest.raises(ValueError):
        ClienteAPI(api, backoff_max=float("nan"))
    # backoff_max == 0 is valid
    c = ClienteAPI(api, backoff_max=0)
    assert c.backoff_max == 0.0

    # orcamento_espera
    with pytest.raises(ValueError):
        ClienteAPI(api, orcamento_espera=-0.1)
    with pytest.raises(ValueError):
        ClienteAPI(api, orcamento_espera=True)
    with pytest.raises(ValueError):
        ClienteAPI(api, orcamento_espera=float("nan"))
    # orcamento_espera == 0 and None are valid
    c = ClienteAPI(api, orcamento_espera=0)
    assert c.orcamento_espera == 0.0
    c = ClienteAPI(api, orcamento_espera=None)
    assert c.orcamento_espera is None

    # large max_tentativas
    c = ClienteAPI(api, max_tentativas=2000)
    assert c.max_tentativas == 2000


def test_obter_usuario_invalid_id():
    api = MockAPI([])
    cliente = ClienteAPI(api)
    for invalid in [0, -1, -100, True, False, "1", 1.0, None]:
        with pytest.raises(ValueError):
            cliente.obter_usuario(invalid)
    assert len(api.calls) == 0


def test_obter_usuario_sucesso():
    api = FakeAPI()
    cliente = ClienteAPI(api)
    res = cliente.obter_usuario(7)
    assert res == {"id": 7, "nome": "Usuario 7"}
    assert api.chamadas == [("GET", "/usuarios/7", 2.0)]


def test_obter_usuario_404_imediato():
    # 404 does not retry
    api = MockAPI([Resposta(404, {"erro": "não encontrado"})])
    dormidas = []
    cliente = ClienteAPI(api, dormir=dormidas.append)
    with pytest.raises(NaoEncontrado) as exc_info:
        cliente.obter_usuario(10)
    assert exc_info.value.status == 404
    assert len(api.calls) == 1
    assert len(dormidas) == 0


def test_obter_usuario_outros_status_imediatos():
    # 400, 403, 301, 501 do not retry
    for st in [400, 401, 403, 301, 501]:
        api = MockAPI([Resposta(st, {"erro": "qualquer"})])
        dormidas = []
        cliente = ClienteAPI(api, dormir=dormidas.append)
        with pytest.raises(ErroAPI) as exc_info:
            cliente.obter_usuario(1)
        assert exc_info.value.status == st
        assert not isinstance(exc_info.value, (NaoEncontrado, FalhaPermanente))
        assert len(api.calls) == 1
        assert len(dormidas) == 0


def test_obter_usuario_excecao_nao_retentavel():
    class ErroInesperado(Exception):
        pass

    api = MockAPI([ErroInesperado("falha desconhecida")])
    dormidas = []
    cliente = ClienteAPI(api, dormir=dormidas.append)
    with pytest.raises(ErroInesperado):
        cliente.obter_usuario(1)
    assert len(api.calls) == 1
    assert len(dormidas) == 0


def test_retry_e_backoff():
    # 3 failures, then success
    api = MockAPI([
        Resposta(500),
        ErroConexao("recusada"),
        TempoEsgotado("timeout"),
        Resposta(200, {"id": 1, "nome": "Usuario 1"}),
    ])
    dormidas = []
    cliente = ClienteAPI(api, max_tentativas=4, backoff_base=0.5, backoff_max=8.0, dormir=dormidas.append)
    res = cliente.obter_usuario(1)
    assert res == {"id": 1, "nome": "Usuario 1"}
    assert len(api.calls) == 4
    # Failures:
    # 1: n=1, espera = min(8.0, 0.5 * 2^0) = 0.5
    # 2: n=2, espera = min(8.0, 0.5 * 2^1) = 1.0
    # 3: n=3, espera = min(8.0, 0.5 * 2^2) = 2.0
    assert dormidas == [0.5, 1.0, 2.0]


def test_falha_permanente_esgotou_tentativas_status():
    api = MockAPI([Resposta(500), Resposta(502), Resposta(503)])
    dormidas = []
    cliente = ClienteAPI(api, max_tentativas=3, backoff_base=1.0, backoff_max=10.0, dormir=dormidas.append)
    with pytest.raises(FalhaPermanente) as exc_info:
        cliente.obter_usuario(1)
    err = exc_info.value
    assert err.tentativas == 3
    assert err.status == 503
    assert err.__cause__ is None
    assert len(api.calls) == 3
    # Slept twice: after n=1 and n=2. Not after n=3!
    assert dormidas == [1.0, 2.0]


def test_falha_permanente_alternando_erros():
    # 1: ErroConexao, 2: 500 -> last failure is HTTP status, __cause__ must be None
    api = MockAPI([ErroConexao("falhou"), Resposta(500)])
    cliente = ClienteAPI(api, max_tentativas=2, dormir=lambda s: None)
    with pytest.raises(FalhaPermanente) as exc_info:
        cliente.obter_usuario(1)
    assert exc_info.value.tentativas == 2
    assert exc_info.value.__cause__ is None
    assert exc_info.value.status == 500

    # 1: 500, 2: TempoEsgotado -> last failure is exception, __cause__ must be TempoEsgotado
    api = MockAPI([Resposta(500), TempoEsgotado("timeout")])
    cliente = ClienteAPI(api, max_tentativas=2, dormir=lambda s: None)
    with pytest.raises(FalhaPermanente) as exc_info:
        cliente.obter_usuario(1)
    assert exc_info.value.tentativas == 2
    assert isinstance(exc_info.value.__cause__, TempoEsgotado)
    assert exc_info.value.status is None


def test_falha_permanente_max_tentativas_1():
    api = MockAPI([Resposta(500)])
    dormidas = []
    cliente = ClienteAPI(api, max_tentativas=1, dormir=dormidas.append)
    with pytest.raises(FalhaPermanente) as exc_info:
        cliente.obter_usuario(1)
    assert exc_info.value.tentativas == 1
    assert exc_info.value.__cause__ is None
    assert dormidas == []


def test_retry_after_header():
    # 429 with Retry-After "2"
    api = MockAPI([
        Resposta(429, headers={"Retry-After": "2"}),
        Resposta(429, headers={"retry-after": "1.5"}),
        Resposta(429, headers={"Retry-After": "20"}),  # backoff_max caps it
        Resposta(429, headers={"Retry-After": "-1"}),  # invalid -> fallback to backoff
        Resposta(429, headers={"Retry-After": "nan"}), # invalid -> fallback to backoff
        Resposta(200, {"id": 1, "ok": True}),
    ])
    dormidas = []
    cliente = ClienteAPI(api, max_tentativas=6, backoff_base=0.5, backoff_max=8.0, dormir=dormidas.append)
    cliente.obter_usuario(1)
    assert dormidas[0] == 2.0
    assert dormidas[1] == 1.5
    assert dormidas[2] == 8.0  # capped at backoff_max
    # n=4: backoff_base * 2^(4-1) = 0.5 * 8 = 4.0
    assert dormidas[3] == 4.0
    # n=5: backoff_base * 2^(5-1) = 0.5 * 16 = 8.0 (capped at backoff_max 8.0)
    assert dormidas[4] == 8.0


def test_retry_after_ignorado_em_nao_429():
    # If 500 has Retry-After header, it should not use it
    api = MockAPI([
        Resposta(500, headers={"Retry-After": "100"}),
        Resposta(200, {"id": 1}),
    ])
    dormidas = []
    cliente = ClienteAPI(api, max_tentativas=2, backoff_base=0.5, backoff_max=10.0, dormir=dormidas.append)
    cliente.obter_usuario(1)
    # n=1: backoff is 0.5, not 10.0
    assert dormidas == [0.5]


def test_orcamento_espera():
    # orcamento_espera = 1.5
    # n=1: espera = 0.5 -> soma = 0.5 <= 1.5 -> sleeps 0.5
    # n=2: espera = 1.0 -> soma = 1.5 <= 1.5 -> sleeps 1.0 (soma becomes 1.5)
    # n=3: espera = 2.0 -> soma = 3.5 > 1.5 -> desiste na hora!
    api = MockAPI([Resposta(500), Resposta(500), Resposta(500)])
    dormidas = []
    cliente = ClienteAPI(
        api,
        max_tentativas=5,
        backoff_base=0.5,
        backoff_max=8.0,
        orcamento_espera=1.5,
        dormir=dormidas.append,
    )
    with pytest.raises(FalhaPermanente) as exc_info:
        cliente.obter_usuario(1)
    assert exc_info.value.tentativas == 3
    assert dormidas == [0.5, 1.0]


def test_orcamento_espera_zero():
    api = MockAPI([Resposta(500)])
    dormidas = []
    cliente = ClienteAPI(api, max_tentativas=4, backoff_base=0.5, orcamento_espera=0.0, dormir=dormidas.append)
    with pytest.raises(FalhaPermanente) as exc_info:
        cliente.obter_usuario(1)
    assert exc_info.value.tentativas == 1
    assert dormidas == []


def test_sem_overflow_com_muitas_tentativas():
    # max_tentativas = 2000
    class Always500API:
        def __init__(self):
            self.calls = 0

        def requisitar(self, metodo, caminho, timeout):
            self.calls += 1
            return Resposta(500)

    api = Always500API()
    dormidas = []
    cliente = ClienteAPI(api, max_tentativas=2000, backoff_base=0.5, backoff_max=10.0, dormir=dormidas.append)
    with pytest.raises(FalhaPermanente) as exc_info:
        cliente.obter_usuario(1)
    assert exc_info.value.tentativas == 2000
    assert len(dormidas) == 1999
    assert dormidas[-1] == 10.0


def test_obter_varios():
    api = MockAPI([
        Resposta(200, {"id": 1, "nome": "U1"}),
        Resposta(404),
        Resposta(200, {"id": 3, "nome": "U3"}),
    ])
    cliente = ClienteAPI(api)
    # Duplicate 1 should only be requested once
    # 404 should map to None
    resultado = cliente.obter_varios([1, 2, 1, 3])
    assert resultado == {
        1: {"id": 1, "nome": "U1"},
        2: None,
        3: {"id": 3, "nome": "U3"},
    }
    # Check order of keys: 1, 2, 3
    assert list(resultado.keys()) == [1, 2, 3]
    assert len(api.calls) == 3


def test_obter_varios_gerador():
    api = MockAPI([Resposta(200, {"id": 5, "nome": "U5"})])
    cliente = ClienteAPI(api)
    gen = (x for x in [5])
    resultado = cliente.obter_varios(gen)
    assert resultado == {5: {"id": 5, "nome": "U5"}}


def test_obter_varios_validacao_previa():
    api = MockAPI([])
    cliente = ClienteAPI(api)
    # Generator with invalid id at the end
    gen = (x for x in [1, 2, "invalido"])
    with pytest.raises(ValueError):
        cliente.obter_varios(gen)
    assert len(api.calls) == 0

    with pytest.raises(ValueError):
        cliente.obter_varios([1, 2, False])
    assert len(api.calls) == 0


def test_obter_varios_falha_propaga():
    api = MockAPI([
        Resposta(200, {"id": 1, "nome": "U1"}),
        Resposta(500),
    ])
    cliente = ClienteAPI(api, max_tentativas=1)
    with pytest.raises(FalhaPermanente):
        cliente.obter_varios([1, 2])
