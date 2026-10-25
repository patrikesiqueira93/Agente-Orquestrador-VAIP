# Template de Especificação — VAIP

Copie este arquivo para `agents/specs/<id>.md` ou `skills/<id>.md` e preencha.
Todo campo do front-matter é obrigatório. Spec sem campo obrigatório é rejeitada.

---

```yaml
---
id: nome_curto_sem_espaco
tipo: subagente | skill | politica
carrega_quando: frase objetiva, uma linha, descrevendo a tarefa que precisa desta spec
nao_carrega_quando: frase objetiva, uma linha, descrevendo tarefas que NÃO devem abrir esta spec
depende_de: [outra_spec, security_policy]
tokens_aprox: 1200
versao: 1.0
responsavel: patrik | vinicius
---
