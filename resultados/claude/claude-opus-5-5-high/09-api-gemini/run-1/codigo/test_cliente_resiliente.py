import pytest

from cliente_resiliente import ApiError, ClienteResiliente
from fake_api import FakeApiServer


def make(srv=None, **kw):
    sleeps = []
    c = ClienteResiliente(srv or FakeApiServer(), sleep_fn=sleeps.append, **kw)
    return c, sleeps


def test_sucesso_sem_retry():
    srv = FakeApiServer()
    c, sleeps = make(srv)
    assert c.get("/a")["status"] == "ok"
    assert len(srv.chamadas) == 1 and sleeps == []
    assert srv.chamadas[0]["timeout"] == 2.0


def test_post_envia_payload():
    srv = FakeApiServer()
    c, _ = make(srv)
    assert c.post("/p", {"x": 1})["payload"] == {"x": 1}
    assert srv.chamadas[0]["metodo"] == "POST"


@pytest.mark.parametrize("tipo", ["network", "timeout", "503", "429"])
def test_recupera_apos_falhas(tipo):
    srv = FakeApiServer()
    srv.configurar_falhas("/r", 2, tipo)
    c, sleeps = make(srv, backoff_base=0.1, backoff_fator=3.0)
    assert c.get("/r")["status"] == "ok"
    assert len(srv.chamadas) == 3
    assert sleeps == pytest.approx([0.1, 0.3])


@pytest.mark.parametrize("tipo,code", [("network", None), ("timeout", None), ("503", 503), ("429", 429)])
def test_esgota_tentativas(tipo, code):
    srv = FakeApiServer()
    srv.configurar_falhas("/r", 10, tipo)
    c, sleeps = make(srv, max_tentativas=4)
    with pytest.raises(ApiError) as ei:
        c.get("/r")
    assert ei.value.status_code == code
    assert len(srv.chamadas) == 4 and len(sleeps) == 3


@pytest.mark.parametrize("code", [500, 502, 504])
def test_5xx_configurado_retenta(code):
    srv = FakeApiServer()
    srv.configurar_resposta("/x", code, {})
    c, sleeps = make(srv)
    with pytest.raises(ApiError) as ei:
        c.get("/x")
    assert ei.value.status_code == code and len(srv.chamadas) == 3


@pytest.mark.parametrize("code", [301, 400, 401, 403, 404, 422])
def test_nao_retentavel(code):
    srv = FakeApiServer()
    srv.configurar_resposta("/x", code, {"erro": "x"})
    c, sleeps = make(srv)
    with pytest.raises(ApiError) as ei:
        c.get("/x")
    assert ei.value.status_code == code
    assert len(srv.chamadas) == 1 and sleeps == []


def test_max_tentativas_um_sem_sleep():
    srv = FakeApiServer()
    srv.configurar_falhas("/r", 1, "network")
    c, sleeps = make(srv, max_tentativas=1)
    with pytest.raises(ApiError):
        c.get("/r")
    assert sleeps == []


@pytest.mark.parametrize("kw", [
    {"max_tentativas": 0}, {"max_tentativas": 2.0}, {"max_tentativas": True}, {"max_tentativas": "3"},
    {"backoff_base": 0}, {"backoff_base": -1}, {"backoff_base": True}, {"backoff_base": "0.1"},
    {"backoff_fator": 0}, {"backoff_fator": None}, {"timeout": 0}, {"timeout": False},
    {"timeout": float("nan")},
])
def test_validacao(kw):
    with pytest.raises(ValueError):
        ClienteResiliente(FakeApiServer(), **kw)


def test_api_error_padrao():
    e = ApiError("msg")
    assert isinstance(e, Exception) and e.status_code is None and "msg" in str(e)
