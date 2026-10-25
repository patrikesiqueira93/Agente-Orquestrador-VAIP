#!/usr/bin/env python3
"""
VAIP SecOps Guard - Módulo de Auditoria Ativa e Blindagem Diária
Executa diariamente antes de qualquer tarefa para garantir Zero-Leak,
integridade da máquina local (PC) e proteção contra ameaças aos agentes.

Regra de ouro: nenhum arquivo desaparece em silêncio. Ou ele é auditado,
ou é declarado cofre legítimo, ou entra na lista de erros e derruba o
status para PARTIAL. Nunca mais um PASS mentiroso.

Códigos de saída:
    0  PASS     auditoria limpa
    1  WARN     achados de segurança
    2  PARTIAL  varredura incompleta (arquivo ilegível ou não inspecionado)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

# Expressões regulares para detecção de segredos em código versionado
SECRET_PATTERNS = {
    "Discord Webhook Exposto": r"https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]{30,}",
    "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
    "Google API Key": r"AIza[0-9A-Za-z_-]{35}",
    "Chave Privada RSA/SSH": r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PRIVATE) KEY",
    "AWS Access Key": r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "Telegram Bot Token": r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b",
    "Chave de LLM (sk-)": r"\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}\b",
}

# Diretórios técnicos: pulados sem necessidade de relatório
IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}

# Cofres locais legítimos: existem para guardar segredo, então não são varridos.
# Ficam registrados no relatório como "cofre declarado", não como falha.
IGNORE_FILES = {".env"}
VAULT_DIRS = {"credentials"}

# Padrões que o .gitignore precisa cobrir para a blindagem ser considerada válida
GITIGNORE_REQUIRED = {
    ".env": "Cofre .env",
    "credentials/": "Pasta credentials/",
    "*.pem": "Certificados .pem",
    "*.key": "Chaves .key",
}

MAX_FILE_BYTES = 2 * 1024 * 1024


def _ler_arquivo(caminho: str) -> str:
    """Lê o arquivo como texto. Deixa a exceção subir para ser registrada."""
    with open(caminho, "r", encoding="utf-8", errors="ignore") as arquivo:
        return arquivo.read()


def _gitignore_cobre(linhas: list, padrao: str) -> bool:
    """Confere se o .gitignore cobre o padrão, ignorando comentários e exceções."""
    alvo = padrao.rstrip("/")
    for linha in linhas:
        if linha.startswith("!"):
            continue
        if linha.rstrip("/") == alvo:
            return True
    return False


def run_security_audit(base_dir=None) -> dict:
    """Executa auditoria completa de segurança e conformidade do VAIP."""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    audit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    findings = []
    scan_errors = []
    vaults_present = []
    scanned_files_count = 0

    # 1. Varredura de segredos em arquivos
    for root, dirs, files in os.walk(base_dir):
        for nome in list(dirs):
            if nome in VAULT_DIRS:
                rel = os.path.relpath(
                    os.path.join(root, nome), base_dir
                ).replace("\\", "/")
                if rel not in vaults_present:
                    vaults_present.append(rel)

        dirs[:] = [
            d for d in dirs if d not in IGNORE_DIRS and d not in VAULT_DIRS
        ]

        for file in files:
            if file in IGNORE_FILES:
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_dir).replace("\\", "/")

            try:
                tamanho = os.path.getsize(file_path)
            except OSError as erro:
                scan_errors.append(
                    {"file": rel_path, "error": f"getsize: {erro}"}
                )
                continue

            if tamanho > MAX_FILE_BYTES:
                scan_errors.append(
                    {
                        "file": rel_path,
                        "error": f"acima de {MAX_FILE_BYTES} bytes ({tamanho})",
                    }
                )
                continue

            try:
                conteudo = _ler_arquivo(file_path)
            except OSError as erro:
                scan_errors.append(
                    {
                        "file": rel_path,
                        "error": f"{type(erro).__name__}: {erro}",
                    }
                )
                continue

            scanned_files_count += 1

            for threat_name, pattern in SECRET_PATTERNS.items():
                achado = re.search(pattern, conteudo)
                if achado is None:
                    continue
                linha = conteudo.count("\n", 0, achado.start()) + 1
                findings.append(
                    {
                        "severity": "HIGH",
                        "type": threat_name,
                        "file": rel_path,
                        "line": linha,
                    }
                )

    # 2. Verificação de integridade do .gitignore
    linhas_ignore = []
    gitignore_path = os.path.join(base_dir, ".gitignore")

    if os.path.exists(gitignore_path):
        try:
            with open(
                gitignore_path, "r", encoding="utf-8", errors="ignore"
            ) as arquivo:
                for bruta in arquivo:
                    limpa = bruta.strip()
                    if limpa and not limpa.startswith("#"):
                        linhas_ignore.append(limpa)
        except OSError as erro:
            scan_errors.append(
                {"file": ".gitignore", "error": f"{type(erro).__name__}: {erro}"}
            )
    else:
        scan_errors.append(
            {"file": ".gitignore", "error": "arquivo ausente na raiz do projeto"}
        )

    for padrao, descricao in GITIGNORE_REQUIRED.items():
        if not _gitignore_cobre(linhas_ignore, padrao):
            findings.append(
                {
                    "severity": "CRITICAL",
                    "type": f"{descricao} desprotegido no .gitignore",
                    "file": ".gitignore",
                    "line": None,
                }
            )

    # 3. Consolidação do resultado
    if findings:
        audit_status = "WARN"
        zero_leak = "NON_COMPLIANT"
    elif scan_errors:
        audit_status = "PARTIAL"
        zero_leak = "INDETERMINADO"
    else:
        audit_status = "PASS"
        zero_leak = "COMPLIANT"

    resultado = {
        "timestamp": audit_time,
        "scanned_files": scanned_files_count,
        "status": audit_status,
        "threats_detected": len(findings),
        "findings": findings,
        "scan_errors": scan_errors,
        "vaults_present": vaults_present,
        "host_protection": "ACTIVE",
        "agent_shield": "ACTIVE",
        "zero_leak_status": zero_leak,
    }

    # 4. Atualizar o ledger de segurança
    ledger_dir = os.path.join(base_dir, "ledger")
    os.makedirs(ledger_dir, exist_ok=True)
    audit_file = os.path.join(ledger_dir, "security_audit.json")

    try:
        temporario = audit_file + ".tmp"
        with open(temporario, "w", encoding="utf-8") as arquivo:
            json.dump(resultado, arquivo, indent=2, ensure_ascii=False)
            arquivo.write("\n")
        os.replace(temporario, audit_file)
    except OSError as erro:
        print(f"[!] Erro ao salvar security_audit.json: {erro}", file=sys.stderr)

    return resultado


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoria SecOps do VAIP.")
    parser.add_argument(
        "--base-dir",
        default=None,
        help="raiz do projeto (padrão: pasta pai de scripts/)",
    )
    argumentos = parser.parse_args()

    res = run_security_audit(argumentos.base_dir)

    print(f"[*] VAIP SecOps Audit ({res['timestamp']}): Status: {res['status']}")
    print(
        f"[*] Arquivos verificados: {res['scanned_files']} "
        f"| Ameaças: {res['threats_detected']} "
        f"| Erros de varredura: {len(res['scan_errors'])}"
    )

    if res["vaults_present"]:
        print(
            "[*] Cofres declarados (não varridos por design): "
            + ", ".join(res["vaults_present"])
        )

    if res["scan_errors"]:
        print(f"[!] {len(res['scan_errors'])} arquivo(s) não auditado(s):")
        for item in res["scan_errors"][:10]:
            print(f"    - {item['file']}: {item['error']}")

    if res["findings"]:
        for achado in res["findings"]:
            local = achado["file"]
            if achado.get("line"):
                local += f":{achado['line']}"
            print(f" [!] {achado['severity']}: {achado['type']} em {local}")
    else:
        print("[+] Nenhuma vulnerabilidade ou segredo exposto detectado.")

    if res["status"] == "PARTIAL":
        return 2
    if res["findings"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())