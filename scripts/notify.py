"""
VAIP Notifier - Disparo Seguro e Formatado para o Discord
Suporta canais de texto padrão e canais de fórum (criação automática de postagem).
Lê credenciais exclusivamente do arquivo .env ou variáveis de ambiente.
"""

import os
import json
import urllib.request
from datetime import datetime

def load_env(env_path=None):
    """Carrega as variáveis do arquivo .env de forma segura."""
    if env_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(base_dir, ".env")
        
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

def send_discord_report(links, candidate_name="Patrik Ernandes Siqueira") -> bool:
    """Envia o relatório diário formatado em Embed para o Discord."""
    load_env()
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("[!] DISCORD_WEBHOOK_URL não encontrada no .env.")
        return False

    today_str = datetime.now().strftime("%d/%m/%Y")
    
    fields = []
    for item in links[:12]:
        data_info = item.get("data_postagem", "Recente")
        fields.append({
            "name": f"📍 {item['portal']} • {item['regiao']}",
            "value": f"**Cargo:** {item['termo']}\n⏱️ **Publicação:** `{data_info}`\n🔗 [Acessar Vagas Filtradas]({item['url']})",
            "inline": False
        })
        
    embed = {
        "title": f"🎯 Relatório Diário de Vagas em Dados - {today_str}",
        "description": f"Salve, **{candidate_name}**! Seguem as vagas filtradas no **Alto Tietê (Mogi das Cruzes, Suzano, Guararema, Salesópolis), Guarulhos e Remoto** para o seu perfil de Analista de Dados & BI.",
        "color": 3447003, # Azul tecnológico elegante
        "fields": fields,
        "footer": {
            "text": "VAIP Master Orchestrator • Zero-Leak & Low-Token",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/4712/4712038.png"
        }
    }
    
    payload = {
        "username": "VAIP - Job Hunter",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712038.png",
        "thread_name": f"🎯 Vagas de Dados - {today_str}", # Suporta canal de fórum
        "embeds": [embed]
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            print("[+] Relatório enviado com sucesso para o Discord!")
            return True
    except Exception as e:
        print(f"[-] Erro ao disparar para Discord: {e}")
        return False

if __name__ == "__main__":
    from search_jobs import generate_search_links
    links = generate_search_links()
    send_discord_report(links)
