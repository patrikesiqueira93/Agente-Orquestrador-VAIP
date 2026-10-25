# Índice de Especificações — VAIP

Este é o único arquivo, junto com `vaip_master.md` e `config/security_policy.md`,
que deve estar sempre carregado. Todo o resto entra sob demanda.

## Regra de carregamento

1. Leia apenas a linha deste índice que corresponde à tarefa atual.
2. Abra no máximo 2 arquivos de especificação por tarefa.
3. Se a tarefa exigir 3 ou mais specs, divida em subtarefas antes de continuar.
4. Se o front-matter da spec disser que não se aplica, não abra o arquivo.
5. Nunca explore a estrutura do repositório para descobrir onde está algo.
   Use esta tabela. Exploração é o gasto mais caro e menos produtivo.

## Tabela de roteamento

| Tarefa | Spec a carregar | Tokens aprox. |
|---|---|---|
| Buscar, filtrar e ranquear vagas | `agents/specs/job_hunter.md` | 1400 |
| Produzir, agendar ou publicar vídeo curto | `agents/specs/dark_channel.md` | 1800 |
| Proteger o host ou varrer segredos | `skills/vaip-host-defense.md` | 900 |
| Verificar defesa contra prompt injection | `skills/vaip-agent-shield.md` | 800 |
| Rotina diária de auditoria e mitigação | `skills/vaip-secops-updater.md` | 700 |
| Revisar política de segurança global | `config/security_policy.md` | 400 |

## Orçamento de contexto por sessão

| Componente | Tokens |
|---|---|
| Este índice | ~350 |
| `vaip_master.md` | ~600 |
| `config/security_policy.md` | ~400 |
| 2 specs sob demanda | ~3000 |
| **Total por turno** | **~4350** |

Se o contexto de um turno passar de 8.000 tokens antes de qualquer código,
algo foi carregado sem necessidade. Pare e reduza.

## Quando falta informação

Se nenhuma linha da tabela cobre a tarefa:

1. Não abra arquivos por tentativa.
2. Trate como spec inexistente.
3. Registre a lacuna em `ledger/state.json` no campo `specs_faltantes`.
4. Peça a criação da spec antes de executar a tarefa.

## Contrato das specs

Toda spec nova segue `agents/contracts/_template.md`. Spec sem front-matter
completo é rejeitada: sem `carrega_quando` e `nao_carrega_quando` o agente
não tem como decidir o que abrir, e volta a explorar o repositório.

## Versionamento

Ao alterar uma spec, incremente `versao` no front-matter e registre
a mudança em uma linha no fim do arquivo, no bloco `## Histórico`.
