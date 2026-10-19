"""
VAIP Copilot de Candidatura - Preenchimento Assistido e Geração de Respostas
Gera as respostas customizadas para cada vaga com base no perfil real do Patrik.
"""

import os
import json
import sys

def load_profile():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_path = os.path.join(base_dir, "data", "profile.json")
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_application_pack(job_title: str, company: str, job_description: str = ""):
    """Gera o pacote de candidatura pronto: dados padrão + carta de apresentação assertiva."""
    profile = load_profile()
    
    cover_letter = f"""Olá, time de Atração e Seleção da {company}!

Meu nome é {profile['nome_completo']}, sou profissional de Dados & Business Intelligence com sólida vivência na construção e governança de indicadores, modelagem dimensional e automação de ETL em ambientes analíticos de alta exigência.

Atualmente atuo como Analista de Dados no projeto da Petrobras (Bacia de Campos), onde fui condecorado com Prêmio de Reconhecimento Técnico pela criação e governança de dashboards estratégicos em Power BI/DAX e otimização de rotinas de ETL com SQL Server. 

Estou muito motivado pela oportunidade para a posição de {job_title} na {company}, trazendo minha visão de negócios e capacidade de transformar dados complexos em decisões acionáveis para o time.

Fico à disposição para uma conversa!
{profile['nome_completo']} | {profile['contato']['telefone']}
LinkedIn: {profile['contato']['linkedin']}
"""
    return {
        "candidato": profile['nome_completo'],
        "contatos": profile['contato'],
        "formacao": profile['formacao_academica'],
        "skills_chave": profile['competencias']['hard_skills'],
        "carta_apresentacao": cover_letter
    }

if __name__ == "__main__":
    pack = generate_application_pack("Analista de Dados Pleno", "Empresa Alvo")
    print("=== PACOTE DO COPILOTO GERADO ===")
    print(pack['carta_apresentacao'])
