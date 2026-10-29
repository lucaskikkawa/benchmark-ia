# Seleção de tarefas especiais

## Piloto (simples e rápida)
- **Principal:** `01-funcao-codex` (unir intervalos fechados; 1 arquivo, timeout 3 min).
- **Para combinações Codex** (regra antiviés): `01-funcao-claude` (parse de duração), mesmo tipo e porte.

## Consistência (3 repetições por combinação)
- **Principal:** `04-dados-claude` (resumir vendas CSV → JSON): saída verificável, varia em tratamento de bordas.
- **Para combinações Claude:** `04-dados-grok` (consolidar chamados e SLA).
