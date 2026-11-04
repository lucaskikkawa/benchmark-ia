# 06 - Barramento de Eventos em Memória (Pacote Multi-arquivo)

Implemente o pacote Python `eventhub` estruturado exatamente nos seguintes 4 arquivos:
- `eventhub/__init__.py`
- `eventhub/models.py`
- `eventhub/handlers.py`
- `eventhub/bus.py`

## Especificação dos Módulos

### 1. `eventhub/models.py`
- `Priority(IntEnum)`:
  - `LOW = 1`
  - `NORMAL = 2`
  - `HIGH = 3`
- `Event` (dataclass):
  - `id: str`
  - `topic: str`
  - `payload: dict`
  - `priority: Priority = Priority.NORMAL`
  - `timestamp: float` (default gerado via `time.time`)
  - `retry_count: int = 0`

### 2. `eventhub/handlers.py`
- `EventHandler(ABC)`:
  - Método abstrato `@abstractmethod def handle(self, event: Event) -> None:`
- `DeadLetterQueue`:
  - `__init__(self) -> None`: inicializa lista de eventos com falha.
  - `add(self, event: Event, error: str) -> None`: armazena tupla `(event, str(error))`.
  - `get_failed_events(self) -> list[tuple[Event, str]]`: retorna cópia da lista de falhas.
  - `clear(self) -> None`: limpa a lista.

### 3. `eventhub/bus.py`
- `EventBus`:
  - `__init__(self, dlq: DeadLetterQueue | None = None) -> None`:
    - Aceita opcionalmente uma instância de `DeadLetterQueue`.
  - `subscribe(self, topic: str, handler: EventHandler | Callable[[Event], None]) -> None`:
    - Registra um handler (instância de `EventHandler` ou callable) para um tópico. Não deve duplicar inscrições idênticas.
  - `unsubscribe(self, topic: str, handler: EventHandler | Callable[[Event], None]) -> None`:
    - Remove o handler do tópico especificado, se registrado.
  - `publish(self, topic: str, payload: dict, priority: Priority = Priority.NORMAL) -> Event`:
    - Cria uma nova instância de `Event`, armazena na fila de pendências e no histórico, e retorna o `Event`.
  - `dispatch_next(self) -> bool`:
    - Retira e despacha o próximo evento pendente. Se nenhum handler estiver registrado para o tópico do evento retirado, o evento é consumido e o método retorna `True`.
    - Ordem de atendimento: maior prioridade primeiro (`HIGH > NORMAL > LOW`); para mesma prioridade, ordem cronológica (`timestamp` menor / FIFO).
    - Para o evento retirado, chama todos os handlers registrados no seu tópico. Se o handler for `EventHandler`, chama `handler.handle(event)`; caso contrário, chama `handler(event)`.
    - Se algum handler lançar exceção:
      - Caso haja `dlq` configurada no barramento, encaminha o evento e a mensagem de erro para `dlq.add(event, str(e))` sem interromper a execução dos demais handlers nem propagar a exceção.
      - Caso **não** haja `dlq` configurada (`dlq is None`), a exceção deve ser propagada para o chamador.
    - Se um handler publicar novos eventos no barramento durante seu processamento, esses novos eventos devem ingressar na fila e ser atendidos nos despachos subsequentes respeitando as prioridades.
    - Retorna `True` se um evento foi processado, ou `False` se a fila estava vazia.
  - `dispatch_all(self) -> int`:
    - Processa todos os eventos pendentes chamando `dispatch_next()` repetidamente e retorna o número total de eventos despachados.
  - `get_history(self, topic: str | None = None) -> list[Event]`:
    - Retorna uma nova lista (cópia) contendo os eventos em ordem de publicação. Se `topic` for fornecido, filtra apenas os eventos daquele tópico, preservando essa ordem. Modificações na lista retornada não devem impactar o histórico interno.

### 4. `eventhub/__init__.py`
Deve exportar os símbolos principais na raiz do pacote via imports relativos:
`Event`, `Priority`, `EventHandler`, `DeadLetterQueue`, `EventBus`.
