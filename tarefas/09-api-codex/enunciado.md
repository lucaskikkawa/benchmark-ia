# Cliente resiliente para API local

Crie `cliente.py` e preserve `fake_api.py`, já fornecido. Implemente:

```python
def buscar_com_retry(api, chave: str, *, tentativas: int = 3, timeout: float = 1.0,
                     backoff: float = 0.1, dormir=time.sleep) -> dict:
    ...
```

Importe `time` para o valor padrão. `api` oferece `get(chave, *, timeout)` e
retorna um dict ou lança exceção. Passe a mesma chave e o mesmo timeout em toda
chamada. Devolva o objeto retornado sem transformá-lo (inclusive dict vazio).
`tentativas` é o número MÁXIMO de chamadas, incluindo a primeira. Ele é um inteiro
>= 1; timeout é número real finito > 0, backoff é número real finito >= 0.
Parâmetros numéricos fora dessas faixas devem gerar `ValueError` ANTES de chamar
a API ou dormir. Outros tipos ficam fora do escopo.

Repita somente para `fake_api.ErroTemporario` e `TimeoutError`. Após a falha da
chamada de índice 0, 1, ... espere `backoff * 2**indice`, chamando `dormir(segundos)`
antes da próxima tentativa, inclusive quando o atraso for zero. Nunca durma após
sucesso ou a última falha. Ao esgotar tentativas, propague a última exceção
original. `ErroPermanente` e outras exceções propagam imediatamente. Erro lançado
por `dormir` também deve propagar. Não capture exceções de maneira genérica.
O timeout é POR tentativa, não um orçamento global; a API é responsável por
interromper a operação ao excedê-lo. Não são necessárias threads ou sinais.

`FakeAPI(dados, seed=0)` roda inteiramente em processo. A seed gera, para cada
chave, zero a duas falhas temporárias/lentas antes de sucesso; roteiros e chamadas
são reproduzíveis. Eventos normais têm latência virtual 0.01s e lentos 2s; a API
compara isso ao timeout e lança `TimeoutError`, sem esperar de verdade. Chave
ausente lança `ErroPermanente`. `.chamadas` registra `(chave, timeout, evento)`.
Para testar sem espera real, injete `dormir=lista.append`. O avaliador também usa
outros objetos com a mesma interface `get`, sem acessar rede.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
