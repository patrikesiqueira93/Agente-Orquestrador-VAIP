---
name: vaip-host-defense
description: Diretrizes de proteção ativa e integridade da máquina física (PC) do usuário (Patrik). Bloqueia comandos destrutivos, isola processos locais, previne alterações indevidas no sistema operacional e blinda credenciais do host.
---

# 🛡️ VAIP Host Defense Skill (Proteção da Máquina Local)

Esta skill estabelece barreiras de segurança física e lógica no ambiente do computador local (Windows/Host) para garantir que nenhum agente, script ou automação comprometa a integridade do sistema operacional ou dos dados do usuário.

## 📌 Pilares de Proteção do Host

### 1. Fronteiras de Diretório e Bloqueio Destrutivo
- **Escopo Restrito**: O agente e seus scripts só operam dentro do diretório do ecossistema VAIP (`vaip-core`).
- **Comandos Proibidos**:
  * Formatação de unidades (`Format-Volume`, `diskpart`, etc.).
  * Exclusão recursiva de diretórios de sistema (`C:\Windows`, `C:\Program Files`, `C:\Users\PpontoS\AppData` fora do cache do projeto).
  * Comandos de desligamento ou reinicialização forçada sem aprovação explícita.
- **Prevenção de Perda de Dados**: Qualquer deleção de arquivo de dados que não seja temporário exige confirmação de governança do usuário.

### 2. Blindagem de Credenciais do Windows
- **Isolamento de Chaves**: Bloqueio de leitura de chaves SSH privadas (`~/.ssh/id_*`), certificados de segurança e credenciais mestras do Windows Credential Manager.
- **Variáveis de Ambiente**: Credenciais operacionais residem estritamente no `.env` do projeto e são protegidas por `.gitignore`. Nenhuma variável sensível deve ser persistida globalmente nas variáveis de sistema do Windows.

### 3. Isolamento de Dependências (Anti-Supply Chain Attack)
- **Zero Poluição Global**: Proibido instalar bibliotecas Python desconhecidas globalmente no Python base do Windows.
- **Ambientes Virtuais**: Módulos utilitários e testes com pacotes externos devem rodar em ambientes virtuais (`.venv`) isolados.
- **Validação de Pacotes**: Uso exclusivo de pacotes estáveis e verificados (ex: standard library, PyNaCl, requests, urllib).

### 4. Bloqueio de Execução Remota Arbitrária
- Proibido executar scripts baixados diretamente da web via pipe (`Invoke-Expression (Invoke-WebRequest ...)` ou `curl | bash`).
- Qualquer código executado deve estar versionado no repositório ou inspecionado localmente.
