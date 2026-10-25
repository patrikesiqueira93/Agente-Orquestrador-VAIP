# HANDOFF — Estado do Projeto VAIP

> Documento de transferência de contexto. Registra o que está pronto, o que
> está pendente e quais são os limites conhecidos da arquitetura atual.
> Última atualização: 25 de outubro de 2026.

---

## Estado atual

O repositório está em produção ativa no `PRJ-01` e em estruturação no `PRJ-02`.
A camada de governança transversal — auditoria de segurança, monitor de
políticas e varredura de segredos — está implementada e validada.

**Branch principal:** `main`, protegida contra force-push e exclusão.
**Execução agendada:** todo dia às 17:30 (America/Sao_Paulo) via GitHub Actions.
**Última auditoria de segurança:** `PASS`, 34 arquivos verificados, 0 ameaças,
0 erros de varredura.

---

## O que foi concluído

### Reorganização estrutural

- Specs movidas de `agents/` para `agents/specs/`, com nomes normalizados:
  `job_hunter.md` e `dark_channel.md`.
- Skills achatadas: pastas `skills/<nome>/SKILL.md` viraram arquivos únicos
  `skills/<nome>.md`, alinhando o caminho com o que o `INDEX.md` referencia.
- Criado `agents/INDEX.md` como ponto único de navegação entre agentes, specs
  e contratos.
- Criado `agents/contracts/_template.md` como modelo obrigatório para specs
  novas.

### Monitor de conformidade de plataformas

- Script `scripts/check_platform_policy.py` implementado.
- Cobre quatro políticas: monetização do YouTube, diretrizes da comunidade do
  YouTube, integridade e diretrizes do TikTok.
- Comparação por **similaridade de Jaccard** sobre *shingles* de cinco
  palavras, com limiar de 97%. Não usa hash exato.
- Filtragem prévia de ruído volátil: UUIDs, URLs, timestamps e sequências
  numéricas longas são removidos antes da comparação.
- Linha de base em `ledger/platform_policy_hashes.json`, relatório em
  `ledger/platform_policy_report.md`.
- Códigos de saída: `0` limpo, `1` falha de rede, `2` erro de configuração,
  `10` mudança detectada.
- Validado em execução real: quatro políticas, similaridade 100% estável em
  execuções consecutivas.

### Auditoria de segurança

- `scripts/secops_guard.py` corrigido. O problema não era só o `except: pass`:
  o `try` englobava `os.path.getsize` e a leitura, então arquivo ilegível era
  descartado em silêncio e a auditoria terminava reportando `PASS`.
- Novo comportamento: falha de leitura entra em `scan_errors` e o status cai
  para `PARTIAL`. Nunca mais conformidade falsa.
- Validação do `.gitignore` ampliada de um padrão (`.env`) para quatro:
  `.env`, `credentials/`, `*.pem`, `*.key`.
- Cada achado traz número de linha, permitindo localizar o vazamento sem
  varrer o arquivo manualmente.
- Detectores acrescentados: token de bot do Telegram e chave de LLM (`sk-`).
- Escrita do ledger passou a ser atômica (`.tmp` seguido de `os.replace`).
- Códigos de saída: `0` PASS, `1` WARN, `2` PARTIAL.

### Proteção de segredos

- `.gitignore` endurecido: `credentials/`, `.env.*` com exceção para
  `.env.example`, certificados `.p12`/`.pfx`/`.jks`, temporários `.tmp`/`.bak`.
- **Secret Protection** e **Push Protection** ativos no GitHub, cobrindo
  detecção por conteúdo, não por nome de arquivo.
- **Gitleaks** integrado ao workflow diário, com `fetch-depth: 0` para varrer
  o histórico completo.
- Histórico auditado: nenhum segredo versionado. O único arquivo sensível por
  nome é `.env.example`, que contém apenas placeholders vazios.

### Política de segurança e documentação

- `config/security_policy.md` enxugado para leitura em tela única, mantendo
  todas as regras. Headers numerados viraram rótulos em negrito e sub-bullets
  aninhados viraram frases corridas.
- Acrescentadas duas proibições: `git push --force` e
  `git commit --no-verify` exigem confirmação expressa. Bloqueio da proteção
  de segredos nunca deve ser contornado.
- Removida a referência a `python-dotenv`, dependência que o projeto não usa:
  os scripts leem de `os.environ`, da biblioteca padrão.
- `README.md` atualizado com stack, requisitos, monitor de conformidade,
  pipeline e árvore de diretórios real.

### Pipeline

- `daily_jobs.yml` reescrito com sete etapas em ordem de segurança: checkout
  completo, Python, dependências, geração do `.env`, Gitleaks, monitor de
  políticas e execução do runner.
- Etapas de Gitleaks e do monitor usam `continue-on-error`: alerta é
  informação, não falha de execução.
- Commit automático restrito a `data/` e `ledger/`, nunca `git add .`.

---

## Pendências

### Bloqueantes

- Commitar e enviar `secops_guard.py`, `daily_jobs.yml`, `.gitignore`,
  `README.md`, `HANDOFF.md` e os arquivos do `ledger`, que estão alterados
  localmente.
- Disparar o workflow manualmente em **Actions → VAIP Daily Jobs → Run
  workflow** para validar a primeira execução em nuvem.

### Melhorias

- Investigar a pasta `.agents/` (com ponto), que contém um `agent.md` paralelo
  ao `agents/vaip_master.md`. Duplicidade de instrução confunde o carregamento
  de contexto.
- Adicionar `secops_guard.py` como etapa do `daily_jobs.yml`, para a auditoria
  rodar também na nuvem a cada execução.
- Criar testes automatizados para `search_jobs.py` e
  `check_platform_policy.py`.
- Relatório semanal consolidado a partir dos snapshots diários de `data/`.

---

## Limites conhecidos

Registrados de forma explícita para que não sejam redescobertos como surpresa.

**Histórico do Git.** O `.gitignore` impede que arquivo novo entre no
repositório, mas não remove nada que já esteja no histórico. Arquivo commitado
no passado permanece exposto indefinidamente. Por isso o Gitleaks é
obrigatório e não substituível.

**Cofres em texto puro.** `.env` e `credentials/` são tratados como cofres
legítimos e ignorados pela varredura, por design. Isso significa que as chaves
vivem em texto puro no disco local. Se a máquina for comprometida, o
`secops_guard` reporta `PASS` enquanto as chaves estão acessíveis. É um risco
aceito conscientemente, não um bug.

**Página do TikTok sobre IA.** A URL de conteúdo gerado por IA foi removida do
monitor porque é renderizada por JavaScript e o Python recebe apenas a casca
do HTML. O guard recusou gravar hash de página vazia, comportamento correto. As
diretrizes de IA seguem cobertas pelas outras duas políticas do TikTok.

**Caminho com espaço.** A raiz do projeto é `Projetos IA`, com espaço no nome.
Funciona, mas exige aspas em comandos futuros que recebam o caminho completo.

**Dependência de conta pessoal.** O Gitleaks roda sem licença apenas em
repositório de conta pessoal. Se o projeto migrar para uma organização, será
necessário obter `GITLEAKS_LICENSE`.

---

## Convenções

- Commits em português, imperativo, com escopo: `fix: corrige leitura de estado`.
- Sem emojis em código.
- `snake_case` para Python, `kebab-case` para skills.
- Toda decisão relevante entra no `ledger/PROJECTS_LEDGER.md`.
- Spec nova segue `agents/contracts/_template.md`.
- Segredo nunca entra no repositório, em nenhuma hipótese.

---

## Como retomar

```powershell
git pull
python scripts/secops_guard.py
python scripts/check_platform_policy.py --dry-run
```

Se os três passarem sem erro, o ambiente está consistente e qualquer trabalho
pode começar a partir do estado descrito aqui.
engole erro de leitura de arquivo. Se metade do repositório falhar na leitura,
o audit ainda conclui "100% Seguro". Correção esperada: contar as falhas,
registrar cada uma em `findings` com severidade MEDIUM e devolver status
`INCONCLUSIVO` quando houver falha de leitura sem ameaça encontrada.
