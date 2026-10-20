---
name: vaip-secops-updater
description: Motor de auditoria diária e atualização contínua de ameaças e postura de segurança do ecossistema VAIP. Varre repositórios, valida integridade de scripts, detecta vazamento de segredos e atualiza o ledger de conformidade.
---

# 🛡️ VAIP SecOps Updater (Auditoria & Atualização Contínua Diária)

Esta skill orquestra a rotina diária de verificação de segurança (SecOps), assegurando que qualquer nova implementação ou alteração no projeto esteja aderente aos padrões de segurança e que vulnerabilidades emergentes sejam mitigadas ativamente.

## 📌 Rotina Diária de Conformidade (SecOps Workflow)

A cada execução do `daily_runner.py` (às 17:30 localmente ou na nuvem):

1. **Varredura Estática de Segredos (Secret Scanning)**:
   * Examina todos os arquivos modificados e versionados no repositório.
   * Se algum arquivo contiver padrões de chave de API, webhook não parametrizado ou token privado, a esteira é **bloqueada imediatamente** antes do envio.

2. **Auditoria de Integridade dos Scripts**:
   * Verifica a assinatura estrutural dos scripts principais (`daily_runner.py`, `notify.py`, `search_jobs.py`).
   * Garante que não houve injeção de código não autorizado ou chamadas a hosts suspeitos.

3. **Atualização Dinâmica do Ledger de Segurança (`ledger/security_audit.json`)**:
   * Registra a cada dia:
     * Data e hora da auditoria.
     * Número de arquivos inspecionados.
     * Status de conformidade (`HEALTHY` / `WARN` / `CRITICAL`).
     * Assinatura do guardião VAIP SecOps.

4. **Notificação de Postura no Discord**:
   * O relatório diário inclui a métrica de segurança: `🛡️ VAIP SecOps: 100% Protegido (Zero-Leak Ativo)`.
