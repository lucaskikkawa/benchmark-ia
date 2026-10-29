from copy import deepcopy
from pathlib import Path
from organizador import organizar_tarefas


def tarefa(titulo, prioridade, concluida=False):
    return {'titulo': titulo, 'prioridade': prioridade, 'concluida': concluida}


def test_vazio_nova_lista():
    entrada = []
    saida = organizar_tarefas(entrada)
    assert saida == [] and saida is not entrada


def test_so_concluidas():
    assert organizar_tarefas([tarefa('a', 5, True), tarefa('b', 0, True)]) == []


def test_filtra_e_ordena():
    entrada = [tarefa('baixa', 1), tarefa('feita', 5, True), tarefa('alta', 4), tarefa('media', 2)]
    assert organizar_tarefas(entrada) == [entrada[2], entrada[3], entrada[0]]


def test_prioridades_extremas():
    entrada = [tarefa('zero', 0), tarefa('cinco', 5)]
    assert organizar_tarefas(entrada) == [entrada[1], entrada[0]]


def test_unicode_preserva_titulo():
    entrada = [tarefa('  ação Ç  ', 3)]
    assert organizar_tarefas(entrada) == entrada


def test_nao_altera_entrada():
    entrada = [tarefa('b', 1), tarefa('a', 4), tarefa('c', 5, True)]
    antes = deepcopy(entrada)
    organizar_tarefas(entrada)
    assert entrada == antes


def test_copia_dicionario():
    entrada = [tarefa('a', 2)]
    saida = organizar_tarefas(entrada)
    assert saida == entrada and saida is not entrada and saida[0] is not entrada[0]
    saida[0]['titulo'] = 'outro'
    assert entrada[0]['titulo'] == 'a'


def test_empates_sem_impor_desempate():
    entrada = [tarefa('c', 2), tarefa('a', 2), tarefa('b', 3), tarefa('d', 2)]
    saida = organizar_tarefas(entrada)
    assert [t['prioridade'] for t in saida] == [3, 2, 2, 2]
    assert sorted(t['titulo'] for t in saida) == ['a', 'b', 'c', 'd']


def test_repeticoes_sao_ocorrencias():
    entrada = [tarefa('igual', 2), tarefa('igual', 2)]
    saida = organizar_tarefas(entrada)
    assert len(saida) == 2 and saida == entrada
    assert saida[0] is not saida[1]


def test_chamadas_independentes():
    a = organizar_tarefas([tarefa('a', 1)])
    assert organizar_tarefas([]) == []
    assert a == [tarefa('a', 1)]


def test_documento_obrigatorio():
    p = Path(__file__).resolve().parents[1] / 'SUPOSICOES.md'
    assert p.is_file(), 'Entregue SUPOSICOES.md'
    assert p.read_text(encoding='utf-8').strip(), 'Registre suas suposições em texto'
