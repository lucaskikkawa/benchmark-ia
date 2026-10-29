import pytest
from cliente import buscar_com_retry
from fake_api import FakeAPI, ErroTemporario, ErroPermanente


class Roteiro:
    def __init__(self, eventos):
        self.eventos = iter(eventos)
        self.chamadas = []

    def get(self, chave, *, timeout):
        self.chamadas.append((chave, timeout))
        evento = next(self.eventos)
        if isinstance(evento, Exception):
            raise evento
        return evento


def test_sucesso_imediato_preserva_objeto():
    objeto = {'nome': 'ação'}
    api, pausas = Roteiro([objeto]), []
    assert buscar_com_retry(api, 'a', dormir=pausas.append) is objeto
    assert api.chamadas == [('a', 1.0)] and pausas == []


def test_dict_vazio_e_sucesso():
    vazio = {}
    assert buscar_com_retry(Roteiro([vazio]), 'x', dormir=lambda _: None) is vazio


def test_retry_e_backoff_exponencial():
    api = Roteiro([ErroTemporario('a'), TimeoutError('b'), ErroTemporario('c'), {'ok': True}])
    pausas = []
    assert buscar_com_retry(api, 'id', tentativas=4, timeout=0.5, backoff=0.25, dormir=pausas.append) == {'ok': True}
    assert api.chamadas == [('id', 0.5)] * 4
    assert pausas == [0.25, 0.5, 1.0]


def test_esgotamento_propaga_ultima_instancia():
    ultimo = TimeoutError('último')
    api, pausas = Roteiro([ErroTemporario('a'), ultimo]), []
    with pytest.raises(TimeoutError) as exc:
        buscar_com_retry(api, 'x', tentativas=2, backoff=0.2, dormir=pausas.append)
    assert exc.value is ultimo
    assert len(api.chamadas) == 2 and pausas == [0.2]


def test_uma_tentativa_nunca_dorme():
    erro = ErroTemporario('único')
    api, pausas = Roteiro([erro]), []
    with pytest.raises(ErroTemporario) as exc:
        buscar_com_retry(api, 'x', tentativas=1, dormir=pausas.append)
    assert exc.value is erro and len(api.chamadas) == 1 and pausas == []


@pytest.mark.parametrize('erro', [ErroPermanente('ausente'), ValueError('outro'), RuntimeError('outro')])
def test_outros_erros_nao_repetem(erro):
    api, pausas = Roteiro([erro, {}]), []
    with pytest.raises(type(erro)) as exc:
        buscar_com_retry(api, 'x', dormir=pausas.append)
    assert exc.value is erro and len(api.chamadas) == 1 and pausas == []


def test_backoff_zero_ainda_chama_callback():
    pausas = []
    api = Roteiro([TimeoutError(), {}])
    assert buscar_com_retry(api, 'x', backoff=0, dormir=pausas.append) == {}
    assert pausas == [0]


@pytest.mark.parametrize('kwargs', [
    {'tentativas': 0}, {'tentativas': -1}, {'timeout': 0}, {'timeout': -1},
    {'timeout': float('inf')}, {'timeout': float('nan')}, {'backoff': -0.1},
    {'backoff': float('inf')}, {'backoff': float('nan')},
])
def test_parametros_invalidos_sem_efeito(kwargs):
    api, pausas = Roteiro([{}]), []
    with pytest.raises(ValueError):
        buscar_com_retry(api, 'x', dormir=pausas.append, **kwargs)
    assert api.chamadas == [] and pausas == []


def test_erro_do_callback_propaga():
    erro = RuntimeError('relógio indisponível')
    api = Roteiro([TimeoutError(), {}])
    def dormir(_):
        raise erro
    with pytest.raises(RuntimeError) as exc:
        buscar_com_retry(api, 'x', dormir=dormir)
    assert exc.value is erro and len(api.chamadas) == 1


def test_fake_api_seed_deterministica_e_integração():
    eventos = set()
    for seed in range(12):
        dados = {'x': {'valor': seed}}
        api1, api2 = FakeAPI(dados, seed), FakeAPI(dados, seed)
        pausas1, pausas2 = [], []
        assert buscar_com_retry(api1, 'x', dormir=pausas1.append) == dados['x']
        assert buscar_com_retry(api2, 'x', dormir=pausas2.append) == dados['x']
        assert api1.chamadas == api2.chamadas
        assert pausas1 == pausas2
        assert len(pausas1) == len(api1.chamadas) - 1
        eventos.update(c[2] for c in api1.chamadas)
    assert {'ok', 'lento', 'temporario'} <= eventos


def test_fake_api_timeout_pequeno_em_todas_tentativas():
    api, pausas = FakeAPI({'x': {}}, seed=1), []
    with pytest.raises(TimeoutError):
        buscar_com_retry(api, 'x', tentativas=3, timeout=0.001, dormir=pausas.append)
    assert len(api.chamadas) == 3 and pausas == [0.1, 0.2]


def test_fake_api_chave_ausente():
    api, pausas = FakeAPI({}, seed=3), []
    with pytest.raises(ErroPermanente):
        buscar_com_retry(api, 'nada', dormir=pausas.append)
    assert len(api.chamadas) == 1 and pausas == []
