# Tarefa: escrever testes para `senhas.py`

O diretório de trabalho contém `senhas.py`, um módulo **correto** com três funções públicas e uma
constante, cujo comportamento está especificado nas docstrings:

```python
ESPECIAIS: frozenset[str]
def validar_senha(senha: str, tamanho_minimo: int = 8) -> list[str]: ...
def pontuar_senha(senha: str) -> int: ...
def classificar(senha: str) -> str: ...
```

**Não altere `senhas.py`.** Sua tarefa é escrever uma suíte pytest em `tests/test_senhas.py`
(pode criar outros `tests/test_*.py` e um `tests/conftest.py` se quiser) que verifique a
especificação das docstrings da forma mais completa possível, incluindo casos de borda.

Como será avaliado:

- A suíte será executada com `python -m pytest -q tests` a partir do diretório de trabalho; importe
  o módulo com `from senhas import ...`. Use só pytest e a biblioteca padrão; não use rede nem arquivos externos.
- Ela **precisa passar** contra o `senhas.py` fornecido.
- Depois, será executada contra várias versões de `senhas.py` com pequenos bugs plantados; quanto
  mais versões com bug a sua suíte detectar (fazendo algum teste falhar), maior a nota.
- Os testes devem ser determinísticos e rápidos (a suíte inteira em poucos segundos).
