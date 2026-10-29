# Plano do Benchmark IA — v2

Documento de planejamento e especificações finais para o benchmark de agentes e modelos de inteligência artificial em tarefas de programação.

---

## 1. Visão Geral e Objetivos

- **Natureza do Projeto:** Projeto hobby focado em comparar a capacidade prática de geração e resolução de código entre modelos de IA contemporâneos.
- **Escopo e Duração:** Meta de execução de aproximadamente ~2 horas no total.
- **Métricas Observadas:** Qualidade e corretude da solução (testes unitários e rubrica qualitativa) e tempo de execução. **Não medimos tokens nem custo.**

---

## 2. Modelos e Matriz de Combinações

Serão avaliados **8 modelos** distribuídos por 4 empresas/ecossistemas, combinados com **2 níveis de esforço de raciocínio** (`medium` e `high`), totalizando **16 combinações**:

| Empresa / Ecossistema | Modelos Avaliados | Esforços de Raciocínio | Combinações |
| :--- | :--- | :--- | :--- |
| **Codex (OpenAI)** | `gpt-6.1-sol`, `gpt-6-luna` | `medium`, `high` | 4 combinações |
| **Claude (Anthropic)** | `Opus 5.5`, `Haiku 5.5` | `medium`, `high` | 4 combinações |
| **Gemini (Google)** | `gemini-4-argon`, `gemini-3.8-flash` | `medium`, `high` | 4 combinações |
| **Grok (xAI)** | `grok-4.7`, `grok-4.7-build-fast` | `medium`, `high` | 4 combinações |

### Regra Específica de Execução (Cotas do Gemini)
Para mitigar restrições de cota no ecossistema Gemini:
- Executar integralmente todas as rodadas do modelo **`gemini-3.8-flash`** primeiro.
- Apenas após a conclusão do Flash, iniciar as execuções do **`gemini-4-argon`**.

---

## 3. Tipos de Tarefa e Dificuldade

Todas as tarefas são em **Python**, com nível de dificuldade **simples** e escopo autocontido. Há **10 tipos de tarefa**, com ajustes específicos de design:

1. **Tipo 1 — Função do zero:** Implementação de uma função com assinatura, tipos e comportamento definidos em especificação.
2. **Tipo 2 — Correção de bug:** Código existente com falha lógica, corner case não tratado ou exceção.
3. **Tipo 3 — Refatoração:** Código funcional, porém com débito técnico, má legibilidade ou arquitetura deficiente, mantendo comportamento idêntico.
4. **Tipo 4 — Manipulação de dados (CSV/JSON):** Leitura, filtragem, transformação, agregação e escrita de dados estruturados.
5. **Tipo 5 — CLI completa:** Interface de linha de comando com argumentos, flags, tratamento de entrada inválida e saída padronizada.
6. **Tipo 6 — Projeto multi-arquivo:** Estrutura modular contendo no **máximo 3 a 4 arquivos**, avaliando imports relativos e coesão entre módulos.
7. **Tipo 7 — Algoritmo com desempenho:** Resolução que exige complexidade de tempo/espaço adequada; o teste inclui **limite estrito de tempo de execução** contra entradas volumosas.
8. **Tipo 8 — Escrever testes unitários:** O modelo deve implementar uma suíte de testes; a avaliação é realizada via **mutation testing com ~10 bugs plantados**, medindo a taxa de mutantes eliminados.
9. **Tipo 9 — Integração com API simulada:** Consumo de serviços HTTP usando **API mock local**, executado em **Docker sem rede**, com falhas de rede, lentidão e retries **determinísticos controlados por seed**.
10. **Tipo 10 — Tarefa ambígua:** Enunciado com pontos propositalmente abertos. Os testes automáticos validam exclusivamente o **núcleo explícito e inequívoco** da especificação; a rubrica avaliadora confere se o modelo documentou suas decisões em um arquivo `SUPOSICOES.md`.

---

## 4. Geração de Tarefas e Matriz de Execuções

### Criação e Regra Antiviés
- Cada empresa cria 1 versão para cada um dos 10 tipos = **40 tarefas no total** (10 criadas por Codex, 10 por Claude, 10 por Gemini, 10 por Grok).
- **Isolamento de viés:** Cada modelo/empresa resolve unicamente as **30 tarefas criadas pelas outras 3 empresas** (nenhum modelo resolve tarefas formuladas por sua própria família/empresa).

### Amostra de Consistência
- Além das 30 tarefas principais, seleciona-se **1 tarefa fixa** para ser repetida **3 vezes** por combinação, avaliando determinismo e variabilidade.

### Contagem Total de Execuções
- Cada combinação executa:
  $$\text{30 tarefas normais} + (1 \text{ tarefa de consistência} \times 3 \text{ repetições}) = 33 \text{ execuções}$$
- Total geral com as 16 combinações:
  $$16 \text{ combinações} \times 33 \text{ execuções} = 528 \text{ execuções}$$

---

## 5. Ambiente de Execução e Isolamento

- **Contêineres descartáveis:** Toda execução ocorre em um container Docker isolado, recriado a partir do zero para cada execução e destruído logo após o término.
- **Rede desativada:** Containers operam com rede desabilitada (`--network none`), exceto se houver mock interno via loopback local.
- **Teto de tempo (Timeout):** Teto padrão de **5 minutos por execução**. O papel *Cria Testes* pode definir um timeout menor específico na configuração da tarefa (`meta.yaml`).

---

## 6. Sistema de Avaliação e Pontuação

A nota final de cada execução varia de **0 a 10** e é calculada pela fórmula ponderada:

$$\text{Nota Final} = 0{,}7 \times (\% \text{ de testes passados}) + 0{,}3 \times \left(\frac{\text{Rubrica}}{10}\right)$$

### Estrutura da Rubrica Qualitativa
A rubrica avalia 5 critérios objetivos com pontuações de 0 a 2 cada (total de 0 a 10 pontos):
1. **Legibilidade e Organização** (0 a 2)
2. **Tratamento de Erros e Casos de Borda** (0 a 2)
3. **Aderência às Boas Práticas e Padrões Idiomáticos de Python** (0 a 2)
4. **Manutenibilidade e Modularidade** (0 a 2)
5. **Documentação / Atendimento às Instruções Adicionais** (ex.: `SUPOSICOES.md` no tipo 10) (0 a 2)

### Juiz Neutro e Anonimização
- A avaliação da rubrica é feita de forma cega.
- O código submetido tem nomes de modelos, prompts internos e metadados de procedência removidos.
- O **juiz da rubrica** é sempre uma IA de uma **empresa neutra**: não pode ser a empresa autora da tarefa nem a empresa criadora do modelo sob avaliação.

---

## 7. Formato e Estrutura dos Arquivos de Tarefa

Cada tarefa reside no diretório `tarefas/<tipo>-<autor>/` estruturada com:

```
tarefas/<tipo>-<autor>/
├── enunciado.md          # Especificação detalhada da tarefa para o agente
├── inicial/              # Código base inicial fornecido ao modelo
├── testes_ocultos/       # Suíte de testes em pytest (mínimo de 8 testes rigorosos)
├── rubrica.yaml          # Critérios detalhados de avaliação para os 5 itens (0 a 2 cada)
└── meta.yaml             # Metadados: tipo, autor, revisor, timeout_segundos, comando_teste
```

---

## 8. Fluxo de Trabalho do Benchmark

1. **Criação das Tarefas:** Geração das 40 tarefas distribuídas igualmente entre as 4 empresas de acordo com os 10 tipos.
2. **Aprovação:** Revisão e aprovação formal de todas as tarefas e rubricas pelo Lucas.
3. **Rodada Piloto:** Execução de 1 tarefa de teste em todas as 16 combinações para validar orquestração, scripts de automação, isolamento Docker e tempos reais de resposta.
4. **Ajustes:** Calibração de timeouts e refinamento do pipeline a partir das métricas do piloto.
5. **Rodada Completa:** Execução das 528 instâncias, cálculo das notas e consolidação dos relatórios finais.
