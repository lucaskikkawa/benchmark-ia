# Suposições adotadas

- Empates de prioridade mantêm a ordem original (ordenação estável).
- Títulos repetidos representam tarefas distintas, e não são deduplicados.
- Campos extras são preservados na cópia rasa, sem interpretar seu conteúdo.
- Não normalizo títulos nem altero espaços ou maiúsculas.
- Entradas fora do domínio explícito não recebem validação adicional; podem
  produzir exceções nativas. Uma versão de produção poderia definir essa política
  com quem consome a API.
- Não há acesso a arquivos, data corrente ou estado persistente entre chamadas.
