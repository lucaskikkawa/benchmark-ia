import pytest
from fake_api import FakeApiServer
from cliente_resiliente import ApiError, ClienteResiliente


class MockSleeper:
    def __init__(self):
        self.delays: list[float] = []

    def __call__(self, delay: float) -> None:
        self.delays.append(delay)


def test_sucesso_imediato_get_e_post():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor=servidor, sleep_fn=sleeper)

    res_get = cliente.get("/itens")
    assert res_get["status"] == "ok"
    assert res_get["metodo"] == "GET"

    res_post = cliente.post("/itens", {"nome": "Novo Item"})
    assert res_post["status"] == "ok"
    assert res_post["metodo"] == "POST"
    assert res_post["payload"] == {"nome": "Novo Item"}
    assert len(sleeper.delays) == 0


def test_recuperacao_apos_falha_de_rede():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_falhas("/dados", qtd_falhas=2, tipo_falha="network")
    cliente = ClienteResiliente(
        servidor=servidor,
        max_tentativas=3,
        backoff_base=0.1,
        backoff_fator=2.0,
        sleep_fn=sleeper,
    )

    dados = cliente.get("/dados")
    assert dados["status"] == "ok"
    assert len(servidor.chamadas) == 3
    assert pytest.approx(sleeper.delays, 0.001) == [0.1, 0.2]


def test_recuperacao_apos_timeout():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_falhas("/processamento", qtd_falhas=1, tipo_falha="timeout")
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=3, sleep_fn=sleeper)

    res = cliente.get("/processamento")
    assert res["status"] == "ok"
    assert len(servidor.chamadas) == 2
    assert len(sleeper.delays) == 1


def test_recuperacao_apos_rate_limit_429():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_falhas("/limitada", qtd_falhas=1, tipo_falha="429")
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=2, sleep_fn=sleeper)

    res = cliente.get("/limitada")
    assert res["status"] == "ok"
    assert len(servidor.chamadas) == 2


def test_esgotamento_de_tentativas_rede_lanca_apierror_sem_status_code():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_falhas("/indisponivel", qtd_falhas=5, tipo_falha="network")
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=3, sleep_fn=sleeper)

    with pytest.raises(ApiError) as exc_info:
        cliente.get("/indisponivel")

    assert len(servidor.chamadas) == 3
    assert len(sleeper.delays) == 2
    assert exc_info.value.status_code is None


def test_esgotamento_de_tentativas_status_503_preserva_status_code():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_resposta("/indisponivel", status_code=503, data={"erro": "Serviço sobrecarregado"})
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=3, sleep_fn=sleeper)

    with pytest.raises(ApiError) as exc_info:
        cliente.get("/indisponivel")

    assert len(servidor.chamadas) == 3
    assert len(sleeper.delays) == 2
    assert exc_info.value.status_code == 503


def test_esgotamento_de_tentativas_status_429_preserva_status_code():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_resposta("/rate_limit", status_code=429, data={"erro": "Muitas requisições"})
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=2, sleep_fn=sleeper)

    with pytest.raises(ApiError) as exc_info:
        cliente.get("/rate_limit")

    assert len(servidor.chamadas) == 2
    assert exc_info.value.status_code == 429


def test_erro_404_sem_retry():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_resposta("/nao-existe", status_code=404, data={"erro": "Not Found"})
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=3, sleep_fn=sleeper)

    with pytest.raises(ApiError) as exc_info:
        cliente.get("/nao-existe")

    assert len(servidor.chamadas) == 1
    assert len(sleeper.delays) == 0
    assert exc_info.value.status_code == 404


def test_erro_400_sem_retry():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_resposta("/bad-request", status_code=400, data={"erro": "Bad Request"})
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=3, sleep_fn=sleeper)

    with pytest.raises(ApiError) as exc_info:
        cliente.post("/bad-request", {"invalido": True})

    assert len(servidor.chamadas) == 1
    assert len(sleeper.delays) == 0
    assert exc_info.value.status_code == 400


def test_status_301_sem_retry():
    servidor = FakeApiServer()
    sleeper = MockSleeper()
    servidor.configurar_resposta("/redirect", status_code=301, data={"location": "/novo"})
    cliente = ClienteResiliente(servidor=servidor, max_tentativas=3, sleep_fn=sleeper)

    with pytest.raises(ApiError) as exc_info:
        cliente.get("/redirect")

    assert len(servidor.chamadas) == 1
    assert len(sleeper.delays) == 0
    assert exc_info.value.status_code == 301


def test_timeout_passado_ao_servidor():
    servidor = FakeApiServer()
    cliente = ClienteResiliente(servidor=servidor, timeout=4.5)
    cliente.get("/ping")
    assert servidor.chamadas[0]["timeout"] == 4.5


def test_validacao_parametros_construtor():
    servidor = FakeApiServer()
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, max_tentativas=0)
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, max_tentativas=-1)
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, max_tentativas=True)  # type: ignore
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, backoff_base=0.0)
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, backoff_base=-0.5)
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, backoff_fator=0.0)
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, backoff_fator=-2.0)
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, timeout=0.0)
    with pytest.raises(ValueError):
        ClienteResiliente(servidor=servidor, timeout=-1.0)


@pytest.mark.parametrize("status", [200, 201, 204, 206, 299])
def test_sucesso_qualquer_2xx(status):
    servidor = FakeApiServer()
    servidor.configurar_resposta("/sucesso", status, {"valor": 42})
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor, sleep_fn=sleeper)
    assert cliente.get("/sucesso") == {"valor": 42}
    assert len(servidor.chamadas) == 1
    assert sleeper.delays == []


def test_recuperacao_apos_503():
    servidor = FakeApiServer()
    servidor.configurar_falhas("/ocupado", 1, "503")
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor, sleep_fn=sleeper)
    assert cliente.get("/ocupado")["status"] == "ok"
    assert len(servidor.chamadas) == 2
    assert sleeper.delays == [0.05]


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_status_transitorios_esgotam_tentativas_com_backoff_configurado(status):
    servidor = FakeApiServer()
    servidor.configurar_resposta("/falha", status, {"erro": "temporário"})
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor, max_tentativas=4, backoff_base=0.2,
                                backoff_fator=3.0, sleep_fn=sleeper)
    with pytest.raises(ApiError) as exc_info:
        cliente.get("/falha")
    assert len(servidor.chamadas) == 4
    assert sleeper.delays == pytest.approx([0.2, 0.6, 1.8])
    assert exc_info.value.status_code == status


@pytest.mark.parametrize("status", [401, 403])
def test_outros_4xx_sem_retry(status):
    servidor = FakeApiServer()
    servidor.configurar_resposta("/protegido", status, {"erro": "negado"})
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor, sleep_fn=sleeper)
    with pytest.raises(ApiError) as exc:
        cliente.get("/protegido")
    assert exc.value.status_code == status
    assert len(servidor.chamadas) == 1
    assert sleeper.delays == []


@pytest.mark.parametrize("tipo", ["network", "timeout", "503", "429"])
def test_uma_tentativa_nao_espera_apos_falha(tipo):
    servidor = FakeApiServer()
    servidor.configurar_falhas("/falha", 2, tipo)
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor, max_tentativas=1, sleep_fn=sleeper)
    with pytest.raises(ApiError):
        cliente.get("/falha")
    assert len(servidor.chamadas) == 1
    assert sleeper.delays == []


def test_executar_preserva_metodo_payload_rota_e_timeout_nos_retries():
    servidor = FakeApiServer()
    servidor.configurar_falhas("/alterar", 1, "network")
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor, timeout=0.75, sleep_fn=sleeper)
    payload = {"nome": "ação"}
    res = cliente.executar("PATCH", "/alterar", payload)
    assert res == {"status": "ok", "metodo": "PATCH", "rota": "/alterar", "payload": payload}
    assert servidor.chamadas == [
        {"metodo": "PATCH", "rota": "/alterar", "payload": payload, "timeout": 0.75},
        {"metodo": "PATCH", "rota": "/alterar", "payload": payload, "timeout": 0.75},
    ]


def test_alternancia_de_erros_antes_do_sucesso():
    servidor = FakeApiServer()
    servidor.configurar_falhas("/complexo", 2, "network")
    sleeper = MockSleeper()
    cliente = ClienteResiliente(servidor, max_tentativas=3, backoff_base=0.1, backoff_fator=2.0, sleep_fn=sleeper)
    res = cliente.get("/complexo")
    assert res["status"] == "ok"
    assert len(sleeper.delays) == 2
    assert sleeper.delays == pytest.approx([0.1, 0.2])
