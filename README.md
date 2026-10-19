# VAIP Core - Repositório Central de Orquestração

Ambiente de controle, governança e orquestração do Agente Mestre **VAIP** (Vinicius + AI + Patrik).

## Estrutura do Ecossistema

```text
vaip-core/
├── .env.example              # Modelo seguro de variáveis de ambiente
├── .gitignore                # Blindagem contra vazamento de credenciais e arquivos pesados
├── config/
│   └── security_policy.md   # Políticas estritas de segurança digital e economia de tokens
├── ledger/
│   ├── PROJECTS_LEDGER.md   # Painel visual do status de cada projeto
│   └── state.json           # Estado estruturado para leitura de máquina de baixo custo
├── agents/
│   ├── vaip_master.md       # Diretrizes mestras e orquestrador supremo
│   ├── job_hunter_spec.md   # Especificação do subagente de Vagas em Dados (Mogi/Remoto)
│   └── dark_channel_spec.md # Especificação do subagente de Conteúdo Dark (YT/TikTok/Kwai)
└── data/                    # Armazenamento local de caches, relatórios e dados filtrados
```

## Projetos Ativos no Ledger
1. **`vagas-dados-mogi`**: Monitoramento diário de oportunidades na área de dados em Mogi das Cruzes, Alto Tietê e posições remotas.
2. **`canais-dark-video`**: Criação, renderização e agendamento de conteúdo automatizado para TikTok, Kwai e YouTube.
