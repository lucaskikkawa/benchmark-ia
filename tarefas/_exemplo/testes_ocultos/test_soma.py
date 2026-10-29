from soma import soma_pares
def test_basico(): assert soma_pares([1,2,3,4]) == 6
def test_vazio(): assert soma_pares([]) == 0
def test_negativos(): assert soma_pares([-2,-3]) == -2
def test_sem_pares(): assert soma_pares([1,3,5]) == 0
