
---

## 3. `scripts/check_platform_policy.py`

```python
#!/usr/bin/env python3
"""VAIP - Monitor de Politicas de Plataforma.

Compara o hash SHA-256 do texto normalizado das paginas de politica de
YouTube e TikTok. Qualquer mudanca gera alerta e codigo de saida 10,
para o workflow abrir uma issue de revisao humana do gate.

Uso:
    python scripts/check_platform_policy.py
    python scripts/check_platform_policy.py --dry-run
    python scripts/check_platform_policy.py --notify

Codigos de saida:
    0   tudo verificado, nenhuma mudanca
    1   falha de rede em pelo menos uma pagina
    2   erro de configuracao
    10  mudanca de politica detectada
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LEDGER = RAIZ / "ledger"
ARQ_ESTADO = LEDGER / "platform_policy_hashes.json"
ARQ_RELATORIO = LEDGER / "platform_policy_report.md"

TIMEOUT_PADRAO = 25
TENTATIVAS_PADRAO = 3
MINIMO_CARACTERES_UTEIS = 500

USER_AGENT = (
    "VAIP-PolicyWatcher/1.0 "
    "(+https://github.com/patrikesiqueira93/Agente-Orquestrador-VAIP)"
)

# Confirme cada URL no navegador antes de confiar no monitor.
# Se uma pagina mudar de endereco, o status vira ERRO_DE_REDE e o script avisa.
PAGINAS: dict[str, str] = {
    "youtube_monetizacao": (
        "https://support.google.com/youtube/answer/1311392?hl=en"
    ),
    "youtube_diretrizes": "https://www.youtube.com/t/community_guidelines",
    "tiktok_integridade": (
        "https://www.tiktok.com/safety/en/policies-and-engagement/"
        "integrity-authenticity"
    ),
    "tiktok_diretrizes": "https://www.tiktok.com/community-guidelines",
    "tiktok_ia": (
        "https://support.tiktok.com/en/using-tiktok/creating-videos/"
        "ai-generated-content"
    ),
    # Kwai nao entrou: confirme a URL oficial da politica e descomente.
    # "kwai_diretrizes": "https://...",
}

_RE_COMENTARIO = re.compile(r"<!--.*?-->", re.DOTALL)
_RE_SCRIPT = re.compile(
    r"<(script|style|noscript|svg)\b[^>]*>.*?</\1>",
    re.DOTALL | re.IGNORECASE,
)
_RE_TAG = re.compile(r"<[^>]+>")
_RE_ESPACO = re.compile(r"\s+")


def normalizar(bruto: str) -> str:
    """Reduz o HTML a texto comparavel, removendo ruido de markup."""
    texto = _RE_COMENTARIO.sub(" ", bruto)
    texto = _RE_SCRIPT.sub(" ", texto)
    texto = _RE_TAG.sub(" ", texto)
    texto = html.unescape(texto)
    texto = _RE_ESPACO.sub(" ", texto).strip().lower()
    return texto


def baixar(url: str, timeout: int, tentativas: int) -> tuple[str | None, str | None]:
    """Baixa a pagina. Devolve (conteudo, erro). Nunca esconde a excecao."""
    ultimo_erro = "erro desconhecido"

    for tentativa in range(1, tentativas + 1):
        requisicao = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en,pt-BR;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
                return resposta.read().decode("utf-8", errors="replace"), None
        except urllib.error.HTTPError as erro:
            ultimo_erro = f"HTTP {erro.code} em {url}"
            if erro.code in (401, 403, 404, 410):
                break
        except (urllib.error.URLError, TimeoutError, OSError) as erro:
            ultimo_erro = f"{type(erro).__name__} em {url}: {erro}"
        if tentativa < tentativas:
            time.sleep(2 * tentativa)

    return None, ultimo_erro


def carregar_estado() -> dict:
    if not ARQ_ESTADO.exists():
        return {}
    try:
        with ARQ_ESTADO.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return dados if isinstance(dados, dict) else {}
    except (json.JSONDecodeError, OSError) as erro:
        print(f"[!] Estado ilegivel, tratando como vazio: {erro}", file=sys.stderr)
        return {}


def gravar_json(caminho: Path, dados: dict) -> None:
    """Escrita atomica: grava em .tmp e substitui, evitando arquivo pela metade."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    with temporario.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False, sort_keys=True)
        arquivo.write("\n")
    temporario.replace(caminho)


def verificar(
    paginas: dict[str, str],
    estado: dict,
    timeout: int,
    tentativas: int,
) -> list[dict]:
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    resultados: list[dict] = []

    for chave, url in paginas.items():
        anterior = estado.get(chave, {})
        conteudo, erro = baixar(url, timeout, tentativas)

        if erro is not None or conteudo is None:
            resultados.append(
                {
                    "chave": chave,
                    "url": url,
                    "status": "ERRO_DE_REDE",
                    "erro": erro,
                    "hash": anterior.get("hash"),
                    "caracteres": anterior.get("caracteres"),
                    "verificado_em": agora,
                    "primeira_leitura": anterior.get("primeira_leitura"),
                }
            )
            continue

        texto = normalizar(conteudo)
        if len(texto) < MINIMO_CARACTERES_UTEIS:
            resultados.append(
                {
                    "chave": chave,
                    "url": url,
                    "status": "ERRO_DE_REDE",
                    "erro": (
                        f"conteudo suspeito: {len(texto)} caracteres uteis "
                        f"(minimo {MINIMO_CARACTERES_UTEIS})"
                    ),
                    "hash": anterior.get("hash"),
                    "caracteres": len(texto),
                    "verificado_em": agora,
                    "primeira_leitura": anterior.get("primeira_leitura"),
                }
            )
            continue

        resumo = hashlib.sha256(texto.encode("utf-8")).hexdigest()

        if not anterior.get("hash"):
            status = "NOVA"
        elif anterior["hash"] != resumo:
            status = "MUDOU"
        else:
            status = "IGUAL"

        resultados.append(
            {
                "chave": chave,
                "url": url,
                "status": status,
                "erro": None,
                "hash": resumo,
                "hash_anterior": anterior.get("hash"),
                "caracteres": len(texto),
                "verificado_em": agora,
                "primeira_leitura": anterior.get("primeira_leitura") or agora,
            }
        )

    return resultados


def montar_relatorio(resultados: list[dict]) -> str:
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    linhas = [
        "# Monitor de Politicas - Ultima Verificacao",
        "",
        f"Executado em {agora}.",
        "",
        "| Politica | Status | Caracteres | URL |",
        "|---|---|---|---|",
    ]
    for item in resultados:
        caracteres = item.get("caracteres") or "-"
        linhas.append(
            f"| {item['chave']} | {item['status']} | {caracteres} | {item['url']} |"
        )
    linhas += [
        "",
        "Status possiveis:",
        "",
        "- IGUAL: sem mudanca desde a ultima leitura.",
        "- NOVA: primeira leitura, criou a linha de base.",
        "- MUDOU: revisar o gate de conformidade manualmente antes de publicar.",
        "- ERRO_DE_REDE: a pagina nao respondeu ou mudou de endereco.",
        "",
        "Mudanca de status exige revisao humana antes da proxima publicacao.",
        "",
    ]
    return "\n".join(linhas)


def notificar_discord(resultados: list[dict], webhook: str) -> None:
    linhas = ["**VAIP - Monitor de Politicas**"]
    for item in resultados:
        linhas.append(f"- {item['status']} | {item['chave']}")
        if item.get("erro"):
            linhas.append(f"  motivo: {item['erro']}")
    corpo = json.dumps({"content": "\n".join(linhas)[:1900]}).encode("utf-8")
    requisicao = urllib.request.Request(
        webhook,
        data=corpo,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=15) as resposta:
            print(f"[+] Discord respondeu {resposta.status}", file=sys.stderr)
    except (urllib.error.URLError, TimeoutError, OSError) as erro:
        print(f"[!] Falha ao notificar o Discord: {erro}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monitor de mudanca de politicas das plataformas."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verifica sem gravar estado nem relatorio",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="envia resumo ao Discord quando houver mudanca ou falha",
    )
    parser.add_argument("--timeout", type=int, default=TIMEOUT_PADRAO)
    parser.add_argument("--tentativas", type=int, default=TENTATIVAS_PADRAO)
    argumentos = parser.parse_args()

    if not PAGINAS:
        print("[!] Nenhuma pagina configurada em PAGINAS.", file=sys.stderr)
        return 2

    estado = carregar_estado()
    resultados = verificar(
        PAGINAS, estado, argumentos.timeout, argumentos.tentativas
    )

    houve_mudanca = any(item["status"] == "MUDOU" for item in resultados)
    houve_erro = any(item["status"] == "ERRO_DE_REDE" for item in resultados)

    for item in resultados:
        detalhe = item.get("erro") or ""
        print(f"[{item['status']:>12}] {item['chave']} {detalhe}".rstrip())

    if not argumentos.dry_run:
        novo_estado = dict(estado)
        for item in resultados:
            if item["status"] == "ERRO_DE_REDE":
                continue
            novo_estado[item["chave"]] = {
                "url": item["url"],
                "hash": item["hash"],
                "caracteres": item["caracteres"],
                "primeira_leitura": item["primeira_leitura"],
                "ultima_verificacao": item["verificado_em"],
            }
        gravar_json(ARQ_ESTADO, novo_estado)
        ARQ_RELATORIO.parent.mkdir(parents=True, exist_ok=True)
        ARQ_RELATORIO.write_text(
            montar_relatorio(resultados), encoding="utf-8"
        )
        print(f"[+] Estado gravado em {ARQ_ESTADO.relative_to(RAIZ)}")

    if argumentos.notify and (houve_mudanca or houve_erro):
        webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
        if webhook:
            notificar_discord(resultados, webhook)
        else:
            print(
                "[!] DISCORD_WEBHOOK_URL ausente: notificacao ignorada.",
                file=sys.stderr,
            )

    if houve_mudanca:
        return 10
    if houve_erro:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
