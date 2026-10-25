<div align="center">

# 🧠 VAIP - Agente Orquestrador Mestre
**Vinicius + AI + Patrik • Arquitetura de Orquestração Autônoma, Gestão Multi-Projetos e Segurança Digital**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![CI/CD GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Discord Integration](https://img.shields.io/badge/Alerts-Discord_Webhook-5865F2.svg?logo=discord&logoColor=white)](https://discord.com/)
[![Gitleaks](https://img.shields.io/badge/Secret_Scan-Gitleaks-critical.svg?logo=git&logoColor=white)](https://gitleaks.io/)
[![Zero-Leak Security](https://img.shields.io/badge/Security-Zero--Leak%20Policy-success.svg?logo=shield&logoColor=white)](#-segurança-governança-e-skills-ativas)
[![Status](https://img.shields.io/badge/Status-Produção%20Ativa-brightgreen.svg)](#-projetos-orquestrados)

<p align="center">
  <i>Um ecossistema robusto de agentes especialistas e automações inteligentes projetado para coordenar fluxos analíticos, monitoramento de oportunidades de mercado, conformidade de plataformas e esteiras digitais de alta performance.</i>
</p>

---

</div>

## 📌 Visão Geral do Ecossistema

O **VAIP** é o agente supervisor mestre concebido pelos fundadores **Patrik Ernandes Siqueira** e **Vinicius**. O sistema opera desacoplado: o núcleo orquestrador gerencia múltiplos projetos independentes, coordenando subagentes descartáveis, rotinas em nuvem e políticas rígidas de cibersegurança e eficiência de tokens.

```text
                                 ┌─────────────────────────┐
                                 │   VAIP MASTER AGENT     │
                                 │ (Governança & Despacho) │
                                 └───────────┬─────────────┘
                                             │
               ┌─────────────────────────────┴─────────────────────────────┐
               ▼                                                           ▼
┌──────────────────────────────┐                           ┌──────────────────────────────┐
│  PRJ-01: Vagas-dados-Mogi    │                           │  PRJ-02: Canais-Dark-Engine  │
│  - Scraping & Match Semântico│                           │  - Roteirização via LLM      │
│  - Discord Webhook / Forum   │                           │  - TTS + Render Local FFmpeg │
│  - Copiloto de Candidatura   │                           │  - Multi-Upload Automático   │
│  - Nuvem (GitHub Actions)    │                           │  - TikTok, Kwai & YouTube    │
└──────────────────────────────┘                           └──────────────────────────────┘
               │                                                           │
               └─────────────────────────────┬─────────────────────────────┘
                                             ▼
                          ┌────────────────────────────────────────┐
                          │  CAMADA DE GOVERNANÇA TRANSVERSAL      │
                          │  - SecOps Guard (auditoria diária)     │
                          │  - Monitor de Políticas (Jaccard)      │
                          │  - Gitleaks (histórico de segredos)    │
                          │  - Secret Scanning + Push Protection   │
                          └────────────────────────────────────────┘
```

---

## 🚀 Projetos Orquestrados

### 🟢 `PRJ-01`: Vagas-dados-Mogi-e-regiao (Ativo em Produção)
Esteira autônoma de inteligência de mercado focada em oportunidades de **Dados & Business Intelligence** no polo do **Alto Tietê (Mogi das Cruzes, Suzano, Guararema, Salesópolis, Poá), Guarulhos e posições 100% Remoto**.

* **Monitoramento Contínuo:** Varredura diária automatizada via APIs públicas e portais de carreiras (Gupy, LinkedIn Jobs, Catho, InfoJobs).
* **Filtro de Frescor:** Rastreamento com priorização de vagas publicadas nas últimas 24h a 7 dias.
* **Alertas Inteligentes no Discord:** Publicação diária às **17:30** no canal `#vagas-dados` com criação automática de tópicos (*threads*) por data e links diretos parametrizados.
* **Copiloto de Candidatura (`copilot_apply.py`):** Preenchimento assistido de formulários com base no histórico curricular estruturado (`data/profile.json`), gerando cartas de apresentação hiperpersonalizadas alinhadas aos requisitos de cada vaga.
* **Histórico Versionado:** Cada execução gera um snapshot próprio em `data/vagas_AAAA-MM-DD.md`, permitindo comparar dias e auditar exatamente o que foi publicado.
* **Execução Híbrida (Local + Nuvem):**
  * *Local:* Agendador de Tarefas do Windows (`VAIP_Job_Hunter_Daily`).
  * *Nuvem:* GitHub Actions Workflow (`daily_jobs.yml`) programado via Cron para execução diária gratuita e pontual mesmo com o computador desligado.

---

### 🟡 `PRJ-02`: Canais-Dark-Engine (Em Estruturação)
Pipeline automatizado de criação, composição e distribuição de mídia vertical (9:16) para plataformas de vídeo curto: **YouTube Shorts, TikTok e Kwai**.

* **Geração Rápida de Roteiros:** Estrutura de ganchos de alta retenção (3s) e storytelling dinâmico (30-50s) com baixo custo de tokens.
* **Renderização Eficiente:** Composição visual, legendas sincronizadas e mixagem de áudio automatizadas localmente com **FFmpeg** e engines leves de síntese de voz (TTS).
* **Agendamento Inteligente:** Otimização de metadados, títulos com SEO orientado a tendências e tags estratégicas.
* **Conformidade Antecipada:** Operação subordinada ao monitor de políticas, que avisa diariamente sobre qualquer mudança nas regras das plataformas antes da publicação.

---

## 🧬 Stack, Linguagens & Requisitos

| Camada | Tecnologia | Onde aparece |
|---|---|---|
| Lógica e automação | **Python 3.11+** (biblioteca padrão) | `scripts/` |
| Orquestração e CI/CD | **YAML** (GitHub Actions) | `.github/workflows/` |
| Estado e configuração | **JSON**, `.env` | `ledger/`, `data/` |
| Documentação e specs | **Markdown** | `agents/`, `skills/`, `README.md` |
| Renderização de mídia | **FFmpeg** + TTS | `PRJ-02` |
| Varredura de segredos | **Gitleaks** | CI/CD |
| Ambiente local | **VS Code** + PowerShell (Windows) | desenvolvimento |
| Shell do runner | **Bash** (ubuntu-latest) | `daily_jobs.yml` |

**Requisitos mínimos:** Python 3.11 ou superior, Git e conta no GitHub com acesso ao repositório. O núcleo roda sem dependências externas obrigatórias — quando alguma biblioteca extra for necessária, ela vai em `requirements.txt` e o workflow instala automaticamente.

---

## 📊 Monitor de Conformidade de Plataformas

O script `check_platform_policy.py` acompanha as páginas oficiais de política do **YouTube** e do **TikTok**, para que a operação do `PRJ-02` nunca dependa de uma regra que mudou sem aviso.

A comparação **não** usa hash exato. Páginas de suporte injetam trechos voláteis a cada acesso (IDs de sessão, datas relativas, artigos rotativos), e hash exato transformaria isso em alarme falso diário. Em vez disso:

1. O HTML é reduzido a texto limpo, sem markup, scripts ou comentários.
2. UUIDs, URLs, timestamps e sequências numéricas longas são removidos.
3. O texto restante vira *shingles* (blocos de cinco palavras) e é comparado pelo índice de **Jaccard**.
4. Similaridade acima de **97%** é considerada estável.

| Código de saída | Significado |
|---|---|
| `0` | Nenhuma mudança relevante |
| `1` | Falha de rede em pelo menos uma página |
| `2` | Erro de configuração |
| `10` | Mudança de política detectada |

Status possíveis: `IGUAL`, `NOVA`, `MUDOU`, `ERRO_DE_REDE`. A linha de base fica em `ledger/platform_policy_hashes.json` e o último relatório em `ledger/platform_policy_report.md`.

---

## 🛡️ Segurança, Governança e Skills Ativas

Projetado sob rigorosos padrões de segurança da informação, integridade corporativa e proteção ativa da máquina local:

1. **Trava de Proprietário (Branch Protection na `main`):** A branch principal é blindada no GitHub contra force-pushes (`non_fast_forward`) e exclusões não autorizadas, com controle exclusivo do proprietário **Patrik Ernandes Siqueira**.
2. **Defesa Ativa da Máquina Host (`vaip-host-defense.md`):** Bloqueio estrito de operações destrutivas no sistema operacional, isolamento de processos e blindagem contra acesso a chaves mestras e credenciais do Windows.
3. **Escudo Cognitivo dos Agentes (`vaip-agent-shield.md`):** Defesa ativa contra *Prompt Injection* (Web Shield para dados raspados na Catho/LinkedIn/Gupy), princípio do menor privilégio para subagentes e mascaramento automático de credenciais em logs e saídas.
4. **Auditoria Contínua & Inteligência Diária (`vaip-secops-updater.md`):** Módulo autônomo (`scripts/secops_guard.py`) executado a cada ciclo para escanear segredos expostos, validar a integridade do `.gitignore` e registrar conformidade em `ledger/security_audit.json`. A auditoria nunca falha em silêncio: arquivo ilegível entra em `scan_errors` e o status cai para `PARTIAL`, em vez de reportar conformidade falsa.
5. **Proteção de Segredos em Três Camadas:** o `.gitignore` bloqueia arquivos sensíveis na origem, o **Secret Scanning + Push Protection** do GitHub barra o envio pelo conteúdo e o **Gitleaks** varre o histórico completo a cada execução diária.
6. **Monitor de Conformidade de Plataformas:** vigia diariamente as políticas do YouTube e do TikTok e sinaliza mudança antes que afete a operação do `PRJ-02`.
7. **Cofres Locais Declarados:** `.env` e `credentials/` são reconhecidos como cofres legítimos e não são varridos por design, evitando alerta falso sem esconder o risco assumido.
8. **Eficiência Extrema de Tokens:** Tarefas pesadas de computação, parsing e renderização rodam em scripts locais e workers em nuvem, garantindo respostas rápidas e custo de inferência próximo de zero.

> ⚠️ **Limite conhecido:** o `.gitignore` impede que um arquivo novo entre no repositório, mas **não remove** nada que já esteja no histórico. Por isso a varredura com Gitleaks é obrigatória e não substituível.

---

## 📂 Arquitetura do Repositório

```text
Agente-Orquestrador-VAIP/
├── .github/
│   └── workflows/
│       └── daily_jobs.yml        # CI/CD & Automação Cron diária às 17:30
├── agents/
│   ├── INDEX.md                  # Índice dos agentes, specs e contratos
│   ├── vaip_master.md            # Blueprint e diretrizes do Orquestrador Mestre
│   ├── contracts/
│   │   └── _template.md          # Template obrigatório para novas specs
│   └── specs/
│       ├── job_hunter.md         # Especificação técnica do subagente de vagas
│       └── dark_channel.md       # Especificação técnica do subagente de canais dark
├── skills/
│   ├── vaip-host-defense.md      # Proteção do PC e do Sistema Operacional
│   ├── vaip-agent-shield.md      # Defesa contra Prompt Injection e Jailbreak
│   └── vaip-secops-updater.md    # Auditoria diária e mitigação contínua
├── config/
│   └── security_policy.md        # Diretrizes formais de segurança e economia de tokens
├── ledger/
│   ├── PROJECTS_LEDGER.md        # Painel visual do status de cada projeto
│   ├── state.json                # Estado persistente legível por máquina
│   ├── security_audit.json       # Registro diário da auditoria SecOps
│   ├── platform_policy_hashes.json   # Linha de base das políticas monitoradas
│   └── platform_policy_report.md     # Último relatório de conformidade
├── scripts/
│   ├── secops_guard.py           # Auditoria ativa e varredura diária de segredos
│   ├── check_platform_policy.py  # Monitor de políticas por similaridade (Jaccard)
│   ├── search_jobs.py            # Motor de busca e parametrização de links por região
│   ├── notify.py                 # Integração e disparo de Embeds + Arquivos para Discord
│   ├── daily_runner.py           # Runner unificado com auditoria prévia
│   ├── copilot_apply.py          # Copiloto de candidatura e respostas contextuais
│   └── test_gupy.py              # Teste de conectividade com a fonte de vagas
├── data/
│   ├── profile.json              # Perfil curricular estruturado para auto-fill
│   └── vagas_AAAA-MM-DD.md       # Histórico diário de vagas coletadas
├── .env.example                  # Modelo seguro de configuração de ambiente
├── .gitignore                    # Blindagem de dados sensíveis e binários
├── HANDOFF.md                    # Estado atual do projeto e próximos passos
└── README.md                     # Documentação técnica executiva
```

---

## ⚙️ Configuração de Ambiente

Copie o template seguro e preencha com suas credenciais reais:

```bash
cp .env.example .env
```

Variáveis esperadas:

| Variável | Função |
|---|---|
| `GEMINI_API_KEY` | Chave dos modelos de linguagem |
| `DISCORD_WEBHOOK_URL` | Webhook para alertas no Discord |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Canal alternativo de notificação |
| `GUPY_USER_EMAIL` | Identificação na coleta de vagas |
| `YOUTUBE_CLIENT_SECRETS_FILE` | Caminho do segredo OAuth do YouTube (`credentials/`) |
| `TIKTOK_ACCESS_TOKEN` / `KWAI_ACCESS_TOKEN` | Publicação nos canais dark |
| `TARGET_CITY` / `TARGET_STATE` / `TARGET_ROLES` | Parâmetros regionais da busca |

> 🔐 O arquivo `.env` nunca é versionado. Em produção, cada variável é cadastrada como **Secret** em `Settings → Secrets and variables → Actions`.

---

## ⚡ Como Executar Localmente

### 1. Clonar o Repositório
```bash
git clone https://github.com/patrikesiqueira93/Agente-Orquestrador-VAIP.git
cd Agente-Orquestrador-VAIP
```

### 2. Criar o Ambiente Virtual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Configurar as Variáveis
```bash
cp .env.example .env
```

### 4. Rodar a Auditoria de Segurança
```bash
python scripts/secops_guard.py
```
Saída esperada: `Status: PASS`, com o total de arquivos verificados e nenhum achado.

### 5. Rodar a Varredura de Vagas Manualmente
```bash
python scripts/daily_runner.py
```

### 6. Verificar as Políticas das Plataformas
```bash
python scripts/check_platform_policy.py
```

Para apenas checar, sem gravar nova linha de base:
```bash
python scripts/check_platform_policy.py --dry-run
```

### 7. Disparar o Pipeline na Nuvem
Em **Actions → VAIP Daily Jobs → Run workflow**, sem precisar esperar o horário agendado.

---

## 🔄 Pipeline Diário

O workflow `daily_jobs.yml` executa às **17:30 (America/Sao_Paulo)** e pode ser disparado manualmente. A ordem de execução garante que nada é publicado sem passar pelas verificações:

1. Checkout com histórico completo (`fetch-depth: 0`), necessário para o Gitleaks.
2. Configuração do Python e instalação de dependências.
3. Geração do `.env` a partir dos Secrets do repositório.
4. Varredura de segredos no histórico com **Gitleaks**.
5. Monitor de políticas das plataformas com notificação.
6. Execução do `daily_runner.py`.
7. Commit automático dos resultados em `data/` e `ledger/`.

Os passos de Gitleaks e do monitor usam `continue-on-error`: alerta é informação, não falha de execução. Se derrubassem o job, a coleta diária de vagas também se perderia.

---

## 👥 Criadores & Autores

* **Patrik Ernandes Siqueira** — *Analista de Dados, Business Intelligence e DEV* • [LinkedIn](https://www.linkedin.com/in/patrik-e-siqueira/) • [GitHub](https://github.com/patrikesiqueira93)
* **Vinicius Eduardo Siqueira** — *Co-criador e Estrategista de Negócios*

---

<div align="center">
  <sub>Construído com rigor técnico, postura e foco em resultados de alto nível. • <b>VAIP 2026</b></sub>
</div>
