# 08 - Elaboração de Suíte de Testes Unitários

Você recebeu o módulo correto `validador.py` contendo a implementação da classe `ValidadorSenha` e a constante `CARACTERES_ESPECIAIS_PERMITIDOS`.

Sua tarefa é escrever uma suíte de testes unitários abrangente utilizando `pytest` no diretório `tests/` (por exemplo, no arquivo `tests/test_validador.py`).

## Avaliação por Testes de Mutação (Mutation Testing)

A avaliação da sua suíte será realizada por um executor automatizado que:
1. Executará os seus testes contra a implementação correta de `validador.py` (seus testes **devem passar com 100% de sucesso**).
2. Executará os seus testes contra **12 mutantes** (versões de `validador.py` contendo bugs sutis, regras negligenciadas ou erros de off-by-one em limites e faixas de classificação).
3. Cada mutante é considerado **morto (eliminado)** se a sua suíte apresentar **falha de teste** ao rodar contra ele (código de saída 1 do pytest). Erros de coleta, ausência de testes, interrupções e timeouts não eliminam mutantes. Se a sua suíte passar em um mutante com bug, o mutante terá sobrevivido e o teste correspondente será reprovado.
4. Cada execução da suíte tem limite de **10 segundos**. A pasta `tests/` é copiada, com seus recursos e subpastas, para um diretório temporário junto com a versão avaliada de `validador.py`, tanto para o original quanto para os mutantes. Use a descoberta padrão do pytest; não é necessário que os arquivos estejam diretamente na raiz de `tests/`.

## Especificação do Módulo `validador.py`

### Constante
- `CARACTERES_ESPECIAIS_PERMITIDOS = set("!@#$%^&*()-_+=") `

### Classe `ValidadorSenha`
- `__init__(self, min_tam: int = 8, max_tam: int = 64) -> None`:
  Define os limites mínimo e máximo de caracteres (respeitando os parâmetros caso sejam fornecidos).

- `validar(self, senha: str) -> tuple[bool, list[str]]`:
  Valida a string fornecida contra as regras:
  1. Comprimento mínimo: `len(senha) >= self.min_tam`. Se violado: adiciona erro. Note que comprimentos exatamente iguais a `min_tam` são válidos.
  2. Comprimento máximo: `len(senha) <= self.max_tam`. Se violado: adiciona erro. Note que comprimentos exatamente iguais a `max_tam` são válidos.
  3. Deve conter ao menos uma letra maiúscula (`c.isupper()`).
  4. Deve conter ao menos uma letra minúscula (`c.islower()`).
  5. Deve conter ao menos um dígito numérico (`c.isdigit()`).
  6. Deve conter ao menos um caractere especial pertencente a `CARACTERES_ESPECIAIS_PERMITIDOS` (outros caracteres de pontuação não pertencentes ao conjunto não contam como caractere especial permitido).
  7. **Não pode** conter espaços em branco (`c.isspace()`, incluindo espaços comuns, tabulações e quebras de linha).
  8. **Não pode** conter 3 caracteres repetidos consecutivos em qualquer parte da senha, inclusive no final (ex.: `"aaa"`, `"111"`).
  - Retorna `(True, [])` se todas as regras forem cumpridas, ou `(False, lista_de_mensagens_de_erro)` caso haja violações (acumulando todos os erros identificados).
  - O texto e a ordem das mensagens de erro não fazem parte do contrato; os testes não devem depender deles.

- `calcular_forca(self, senha: str) -> str`:
  - Se a senha for inválida perante `validar(senha)`: retorna `"invalida"`.
  - Se for válida e `len(senha) < 10`: retorna `"fraca"`.
  - Se for válida e `10 <= len(senha) < 14`: retorna `"media"`.
  - Se for válida e `len(senha) >= 14`: retorna `"forte"`.

## Arquivos a Entregar

Crie seus arquivos de teste dentro da pasta `tests/` na raiz do seu projeto (ex.: `tests/test_validador.py`).
