import pytest
from cliente import buscar_com_retry
from fake_api import ErroTemporario, ErroPermanente


class TemporarioFilho(ErroTemporario):
    pass


class TimeoutFilho(TimeoutError):
    pass


class PermanenteFilho(ErroPermanente):
    pass


class API:
    def __init__(self, eventos, registro):
        self.eventos = iter(eventos)
        self.registro = registro

    def get(self, chave, *, timeout):
        self.registro.append(('get', chave, timeout))
        evento = next(self.eventos)
        if isinstance(evento, BaseException):
            raise evento
        return evento


@pytest.mark.parametrize('chave', ['', '  ação\x00🧪\n ', 'e\u0301'])
def test_subclasses_ordem_dos_efeitos_e_objeto_original(chave):
    registro, objeto = [], {'interno': []}
    api = API([TemporarioFilho(), TimeoutFilho(), objeto], registro)
    def dormir(atraso):
        registro.append(('sleep', atraso))
    assert buscar_com_retry(api, chave, timeout=0.125, backoff=0.5, dormir=dormir) is objeto
    assert registro == [('get', chave, 0.125), ('sleep', 0.5),
                        ('get', chave, 0.125), ('sleep', 1.0), ('get', chave, 0.125)]


@pytest.mark.parametrize('erro', [TimeoutError('callback'), ErroTemporario('callback'),
                                 TemporarioFilho('callback'), TimeoutFilho('callback')])
def test_callback_transitorio_nao_e_falha_da_api(erro):
    registro = []
    api = API([TimeoutError(), {}], registro)
    def dormir(atraso):
        registro.append(('sleep', atraso))
        raise erro
    with pytest.raises(type(erro)) as captura:
        buscar_com_retry(api, 'id', tentativas=7, dormir=dormir)
    assert captura.value is erro
    assert registro == [('get', 'id', 1.0), ('sleep', 0.1)]


@pytest.mark.parametrize('erro', [PermanenteFilho('fim'), KeyError('fim'),
                                 KeyboardInterrupt(), SystemExit(5)])
def test_falha_nao_transitoria_apos_retry_propaga_mesma_instancia(erro):
    registro = []
    api = API([TimeoutError(), erro, {}], registro)
    def dormir(atraso):
        registro.append(('sleep', atraso))
    with pytest.raises(type(erro)) as captura:
        buscar_com_retry(api, 'x', tentativas=5, dormir=dormir)
    assert captura.value is erro
    assert registro == [('get', 'x', 1.0), ('sleep', 0.1), ('get', 'x', 1.0)]


def test_quarenta_tentativas_sem_teto_de_backoff():
    registro, pausas, objeto = [], [], {}
    falhas = [TimeoutFilho() if i % 2 else TemporarioFilho() for i in range(39)]
    api = API([*falhas, objeto], registro)
    assert buscar_com_retry(api, 'longa', tentativas=40, timeout=9.5,
                            backoff=0.125, dormir=pausas.append) is objeto
    assert registro == [('get', 'longa', 9.5)] * 40
    assert pausas == [0.125 * 2**i for i in range(39)]


def test_esgotamento_e_chamada_seguinte_reiniciam_backoff():
    registro, pausas = [], []
    ultimo = TemporarioFilho('último')
    api = API([TimeoutFilho(), ErroTemporario(), ultimo], registro)
    with pytest.raises(TemporarioFilho) as captura:
        buscar_com_retry(api, 'x', backoff=0.0625, dormir=pausas.append)
    assert captura.value is ultimo
    assert pausas == [0.0625, 0.125] and len(registro) == 3
    registro.clear()
    api = API([TimeoutError(), {}], registro)
    assert buscar_com_retry(api, 'x', backoff=0.0625, dormir=pausas.append) == {}
    assert pausas == [0.0625, 0.125, 0.0625] and len(registro) == 2


@pytest.mark.parametrize('parametro', ['timeout', 'backoff'])
def test_menos_infinito_validado_antes_do_sucesso(parametro):
    registro, pausas = [], []
    api = API([{}], registro)
    with pytest.raises(ValueError):
        buscar_com_retry(api, 'x', dormir=pausas.append, **{parametro: float('-inf')})
    assert registro == [] and pausas == []


def test_backoff_zero_em_todas_as_falhas():
    registro, pausas, vazio = [], [], {}
    api = API([ErroTemporario(), TimeoutError(), TemporarioFilho(), vazio], registro)
    assert buscar_com_retry(api, 'x', tentativas=4, timeout=1e-100,
                            backoff=0, dormir=pausas.append) is vazio
    assert len(registro) == 4 and pausas == [0, 0, 0]
