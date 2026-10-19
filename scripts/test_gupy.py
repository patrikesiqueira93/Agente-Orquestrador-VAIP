import urllib.request
import json

terms = ["dados", "power bi", "business intelligence", "sql"]
cities = ["Mogi das Cruzes", "Suzano", "Guarulhos", "Remoto"]

url = "https://portal.api.gupy.io/api/v1/jobs?jobName=dados&limit=10"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"Sucesso! Total retornado: {len(data.get('data', []))}")
        for job in data.get("data", [])[:3]:
            print(f"- {job.get('name')} | {job.get('city')}-{job.get('state')} | {job.get('type')} | {job.get('jobUrl')}")
except Exception as e:
    print("Erro na requisicao:", e)
