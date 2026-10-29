# Benchmark IA

Projeto hobby de avaliação e benchmark comparativo de modelos de inteligência artificial aplicados à engenharia de software e programação em Python.

---

## 📌 Status Atual

> **Planejamento — nenhuma tarefa criada ainda**

O projeto encontra-se na fase de estruturação e alinhamento de diretrizes. Nenhuma tarefa ou bateria de testes foi instanciada até o momento. Para todos os detalhes metodológicos e regras de execução, consulte o documento oficial [PLANO.md](PLANO.md).

---

## 🎯 Sobre o Projeto

O objetivo deste benchmark é mensurar a eficácia de diferentes modelos de linguagem de ponta na resolução de problemas de programação cotidianos, com foco em simplicidade, consistência e precisão. 

O projeto prioriza:
- Avaliação prática de corretude de código via testes automatizados e rubrica qualitativa;
- Avaliação antiviés com criação e resolução cruzadas entre diferentes provedores;
- Isolamento estrito de ambiente via contêineres Docker descartáveis sem acesso à rede externa;
- Análise de tempo de resposta sem foco em consumo de tokens ou custos financeiros.

---

## 🤖 Modelos e Combinações Testadas

O benchmark avalia **8 modelos** distribuídos em 4 ecossistemas/provedores, combinados com **2 níveis de esforço de raciocínio** (`medium` e `high`), resultando em **16 combinações**:

- **Codex (OpenAI):** `gpt-6.1-sol`, `gpt-6-luna` (esforço `medium` e `high`)
- **Claude (Anthropic):** `Opus 5.5`, `Haiku 5.5` (esforço `medium` e `high`)
- **Gemini (Google):** `gemini-4-argon`, `gemini-3.8-flash` (esforço `medium` e `high`)
- **Grok (xAI):** `grok-4.7`, `grok-4.7-build-fast` (esforço `medium` e `high`)

> *Nota operacional:* Para gerenciar limites de cota no Gemini, todas as baterias do `gemini-3.8-flash` são executadas antes de iniciar as do `gemini-4-argon`.

---

## 🔬 Metodologia

Um resumo da abordagem definida na versão 2 do plano de benchmark:

1. **Tipos de Tarefa (Dificuldade Simples):**
   - 10 tipos de problemas (função do zero, correção de bug, refatoração, manipulação de CSV/JSON, CLI, projeto multi-arquivo de até 3-4 arquivos, algoritmo com limite estrito de tempo de execução, escrita de testes avaliada por mutation testing com ~10 bugs plantados, integração com API mock local determinística e tarefa com requisitos ambíguos exigindo registro em `SUPOSICOES.md`).
2. **Criação Cruzada Antiviés:**
   - Cada empresa cria 1 versão de cada tipo (totalizando 40 tarefas).
   - Cada modelo resolve apenas as 30 tarefas criadas pelos outros 3 provedores (nunca tarefas de sua própria criadora).
3. **Consistência:**
   - 1 tarefa fixa executada 3 vezes por combinação (16 combinações × 33 tarefas = 528 execuções totais).
4. **Ambiente e Isolamento:**
   - Containers Docker descartáveis, sem acesso à internet e com teto de 5 minutos por execução (ajustável para menos por tarefa).
5. **Critério de Pontuação:**
   - $\text{Nota} = 0{,}7 \times (\% \text{ de testes passados}) + 0{,}3 \times (\text{rubrica}/10)$.
   - A rubrica contém 5 itens objetivos de 0 a 2 pontos avaliados de forma cega por um modelo de empresa neutra.

---

## 📂 Estrutura de Pastas Prevista

```
benchmark-ia/
├── PLANO.md                  # Especificações completas do benchmark (v2)
├── README.md                 # Visão geral, status e documentação de entrada
└── tarefas/                  # Diretório das tarefas (a ser gerado)
    └── <tipo>-<autor>/
        ├── enunciado.md      # Instruções da tarefa fornecidas ao modelo
        ├── inicial/          # Código-base inicial
        ├── testes_ocultos/   # Suíte de validação em pytest (>=8 testes)
        ├── rubrica.yaml      # Critérios objetivos de pontuação da rubrica
        └── meta.yaml         # Metadados e configurações de timeout
```
