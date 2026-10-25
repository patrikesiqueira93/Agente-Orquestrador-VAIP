#!/usr/bin/env python3
"""VAIP - Monitor de Politicas de Plataforma.

Compara o conteudo normalizado das paginas de politica usando similaridade
de shingles (indice de Jaccard), em vez de hash exato. Paginas de suporte
mudam trechos volateis (datas, IDs de sessao, artigos relacionados) a cada
acesso, e o hash exato transformaria isso em alarme falso permanente.

Uso:
    python scripts/check_platform_policy.py
    python scripts/check_platform_policy.py --dry-run
    python scripts/check_platform_policy.py --notify

Codigos de saida:
    0   nenhuma mudanca relevante
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
LIMIAR_PADRAO = 0.97
TAMANHO_SHINGLE = 5
AMOSTRA_SHINGLE = 2

USER_AGENT = (
    "VAIP-PolicyWatcher/1.1 "
    "(+https://github.com/patrikesiqueira93/Agente-Orquestrador-VAIP)"
)

# limiar: similaridade minima para considerar a pagina igual.
# Abaixo disso o status vira MUDOU e o gate exige revisao humana.
PAGINAS: dict[str, dict] = {
    "youtube_monetizacao": {
        "url": "https://support.google.com/youtube/answer/1311392?hl=en",
        "limiar": 0.97,
    },
    "youtube_diretrizes": {
        "url": "https://www.youtube.com/t/community_guidelines",
        "limiar": 0.97,
    },
    "tiktok_integridade": {
        "url": (
            "https://www.tiktok.com/safety/en/policies-and-engagement/"
            "integrity-authenticity"
        ),
        "limiar": 0.97,
    },
    "tiktok_diretrizes": {
        "url": "https://www.tiktok.com/community-guidelines",
        "limiar": 0.97,
    },
    # Kwai nao entrou: confirme a URL oficial da politica e descomente.
    # "kwai_diretrizes": {"url": "https://...", "limiar": 0.97},
}

_RE_COMENTARIO = re.compile(r"<!--.*?-->", re.DOTALL)
_RE_SCRIPT = re.compile(
    r"<(script|style|noscript|svg)\b[^>]*>.*?</\1>",
    re.DOTALL | re.IGNORECASE,
)
_RE_TAG = re.compile(r"<[^>]+>")
_RE_ESPACO = re.compile(r"\s+")

_RE_UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
)
_RE_HEX = re.compile(r"\b[0-9a-f]{16,}\b")
_RE_URL = re.compile(r"https?://\S+")
_RE_ISO = re.compile(r"\d{4}-\d{2}-\d{2}(?:[t ]\d{2}:\d{2}(?::\d{2})?)?")
_RE_DATA = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
_RE_NUM_LONGO = re.compile(r"\b\d{7,}\b")
_RE_SO_PONTUACAO = re.compile(r"[^\w\s]+")


def normalizar(bruto: str) -> str:
    """Reduz o HTML a texto comparavel, removendo ruido de markup."""
    texto = _RE_COMENTARIO.sub(" ", bruto)
    texto = _RE_SCRIPT.sub(" ", texto)
    texto = _RE_TAG.sub(" ", texto)
    texto = html.unescape(texto)
    texto = _RE_ESPACO.sub(" ", texto).strip().lower()
    return texto


def limpar_volatil(texto: str) -> str:
    """Remove trechos que mudam a cada acesso e nao sao politica."""
    texto = _RE_UUID.sub(" ", texto)
    texto = _RE_HEX.sub(" ", texto)
    texto = _RE_URL.sub(" ", texto)
    texto = _RE_ISO.sub(" ", texto)
    texto = _RE_DATA.sub(" ", texto)
    texto = _RE_NUM_LONGO.sub(" ", texto)
    texto = _RE_SO_PONTUACAO.sub(" ", texto)
    texto = _RE_ESPACO.sub(" ", texto).strip()
    return texto


def gerar_shingles(texto: str) -> list[str]:
    """Fingerprint amostral do texto, resistente a ruido pontual."""
    palavras = texto.split()
    if not palavras:
        return []
    if len(palavras) < TAMANHO_SHINGLE:
        base = " ".join(palavras)
        resumo = hashlib.blake2b(base.encode("utf-8"), digest_size=8).hexdigest()
        return [resumo]

    amostra: list[str] = []
    limite = len(palavras) - TAMANHO_SHINGLE + 1
    for indice in range(limite):
        pedaco = " ".join(palavras[indice : indice + TAMANHO_SHINGLE])
        resumo = hashlib.blake2b(pedaco.encode("utf-8"), digest_size=8).hexdigest()
        if int(resumo[0], 16) < AMOSTRA_SHINGLE:
            amostra.append(resumo)
    return sorted(amostra)


def similaridade(antigos: list[str], novos: list[str]) -> float:
    """Indice de Jaccard entre dois conjuntos de shingles."""
    conjunto_a = set(antigos)
    conjunto_b = set(novos)
    if not conjunto_a or not conjunto_b:
        return 0.0
    intersecao = len(conjunto_a & conjunto_b)
    uniao = len(conjunto_a | conjunto_b)
    return intersecao / uniao if uniao else 0.0


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
    paginas: dict[str, dict],
    estado: dict,
    timeout: int,
    tentativas: int,
) -> list[dict]:
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    resultados: list[dict] = []

    for chave, configuracao in paginas.items():
        url = configuracao["url"]
        limiar = float(configuracao.get("limiar", LIMIAR_PADRAO))
        anterior = estado.get(chave, {})
        conteudo, erro = baixar(url, timeout, tentativas)

        if erro is not None or conteudo is None:
            resultados.append(
                {
                    "chave": chave,
                    "url": url,
                    "status": "ERRO_DE_REDE",
                    "erro": erro,
                    "similaridade": None,
                    "shingles": [],
                    "limiar": limiar,
                    "caracteres": anterior.get("caracteres"),
                    "verificado_em": agora,
                    "primeira_leitura": anterior.get("primeira_leitura"),
                }
            )
            continue

        texto = limpar_volatil(normalizar(conteudo))

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
                    "similaridade": None,
                    "shingles": [],
                    "limiar": limiar,
                    "caracteres": len(texto),
                    "verificado_em": agora,
                    "primeira_leitura": anterior.get("primeira_leitura"),
                }
            )
            continue

        novos_shingles = gerar_shingles(texto)
        antigos_shingles = anterior.get("shingles") or []

        if not antigos_shingles or not novos_shingles:
            status = "NOVA"
            sim = None
        else:
            sim = similaridade(antigos_shingles, novos_shingles)
            status = "IGUAL" if sim >= limiar else "MUDOU"

        resultados.append(
            {
                "chave": chave,
                "url": url,
                "status": status,
                "erro": None,
                "similaridade": round(sim, 4) if sim is not None else None,
                "shingles": novos_shingles,
                "limiar": limiar,
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
        "| Politica | Status | Similaridade | Caracteres | URL |",
        "|---|---|---|---|---|",
    ]
    for item in resultados:
        if item.get("similaridade") is None:
            sim = "-"
        else:
            sim = f"{item['similaridade']:.1%}"
        caracteres = item.get("caracteres") or "-"
        linhas.append(
            f"| {item['chave']} | {item['status']} | {sim} | {caracteres} | {item['url']} |"
        )
    linhas += [
        "",
        "Status possiveis:",
        "",
        "- IGUAL: similaridade acima do limiar, sem mudanca relevante.",
        "- NOVA: primeira leitura, criou a linha de base.",
        "- MUDOU: similaridade abaixo do limiar, revisar o gate manualmente.",
        "- ERRO_DE_REDE: a pagina nao respondeu ou mudou de endereco.",
        "",
        "Mudanca de status exige revisao humana antes da proxima publicacao.",
        "",
    ]
    return "\n".join(linhas)


def notificar_discord(resultados: list[dict], webhook: str) -> None:
    linhas = ["**VAIP - Monitor de Politicas**"]
    for item in resultados:
        if item.get("similaridade") is None:
            detalhe_sim = ""
        else:
            detalhe_sim = f" ({item['similaridade']:.1%})"
        linhas.append(f"- {item['status']} | {item['chave']}{detalhe_sim}")
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
        if item.get("similaridade") is None:
            detalhe = item.get("erro") or ""
            print(f"[{item['status']:>12}] {item['chave']} {detalhe}".rstrip())
        else:
            print(
                f"[{item['status']:>12}] {item['chave']} "
                f"similaridade {item['similaridade']:.1%} "
                f"(limiar {item['limiar']:.0%})"
            )

    if not argumentos.dry_run:
        novo_estado = dict(estado)
        for item in resultados:
            if item["status"] == "ERRO_DE_REDE":
                continue
            chave = item["chave"]
            anterior = estado.get(chave, {})
            if item["status"] in ("NOVA", "MUDOU"):
                novo_estado[chave] = {
                    "url": item["url"],
                    "shingles": item["shingles"],
                    "caracteres": item["caracteres"],
                    "limiar": item["limiar"],
                    "primeira_leitura": (
                        anterior.get("primeira_leitura") or item["verificado_em"]
                    ),
                    "ultima_verificacao": item["verificado_em"],
                    "ultimo_status": item["status"],
                }
            else:
                registro = dict(anterior)
                registro["url"] = item["url"]
                registro["caracteres"] = item["caracteres"]
                registro["limiar"] = item["limiar"]
                registro["ultima_verificacao"] = item["verificado_em"]
                registro["ultimo_status"] = item["status"]
                novo_estado[chave] = registro
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