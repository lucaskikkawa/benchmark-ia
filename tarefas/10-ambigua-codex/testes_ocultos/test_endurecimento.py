from collections import Counter
from copy import deepcopy
from organizador import organizar_tarefas


def test_copia_rasa_preserva_extras_e_aliases():
    etiquetas = ['ação', {'metadado': 1}]
    marcador = object()
    original = dict(titulo='  e\u0301 🧪  ', prioridade=3, concluida=False,
                    etiquetas=etiquetas, marcador=marcador)
    resultado = organizar_tarefas([original, original, original])
    assert len(resultado) == 3
    assert len({id(tarefa) for tarefa in resultado}) == 3
    for tarefa in resultado:
        assert tarefa == original and tarefa is not original
        assert tarefa['etiquetas'] is etiquetas and tarefa['marcador'] is marcador
    resultado[0]['titulo'] = 'alterado'
    resultado[0]['extra'] = True
    assert resultado[1] == original and resultado[2] == original
    assert original['titulo'] == '  e\u0301 🧪  ' and 'extra' not in original


def test_volume_sem_deduplicar_nem_impor_desempate():
    entrada = [dict(titulo=['é', 'e\u0301', 'A', 'a', '🧪'][i % 5],
                    prioridade=(i * 7) % 6, concluida=i % 4 == 0,
                    identificador=i, etiquetas=[]) for i in range(30_000)]
    # Repete a mesma identidade além de repetir o conteúdo e o título.
    entrada.extend([entrada[1]] * 5)
    antes = deepcopy(entrada)
    saida = organizar_tarefas(entrada)
    assert entrada == antes and saida is not entrada
    pendentes = [t for t in entrada if not t['concluida']]
    assert len(saida) == len(pendentes)
    assert Counter(t['identificador'] for t in saida) == Counter(t['identificador'] for t in pendentes)
    prioridades = [t['prioridade'] for t in saida]
    assert prioridades == sorted(prioridades, reverse=True)
    originais = {t['identificador']: t for t in entrada}
    assert len({id(t) for t in saida}) == len(saida)
    for tarefa in saida:
        original = originais[tarefa['identificador']]
        assert tarefa == original and tarefa is not original
        assert tarefa['etiquetas'] is original['etiquetas']


def test_chamadas_independentes_com_mesma_entrada():
    entrada = [dict(titulo='mesma', prioridade=0, concluida=False, notas=[])]
    primeiro, segundo = organizar_tarefas(entrada), organizar_tarefas(entrada)
    assert primeiro == segundo == entrada
    assert primeiro is not segundo and primeiro[0] is not segundo[0]
    primeiro[0]['prioridade'] = 5
    assert segundo == entrada and entrada[0]['prioridade'] == 0
