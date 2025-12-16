import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

#Configurações iniciais
load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN") 
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "meta-llama/Llama-3.2-3B-Instruct:together") #Utiliza Mistral, uma LLM open-source

HF_ENABLED = HF_API_TOKEN is not None and HF_API_TOKEN.strip() != "" #Verifica se o token da Hugging Face está definido

print("HF_MODEL_ID:", HF_MODEL_ID)
print("HF_ENABLED:", HF_ENABLED) #Indica se a API do Hugging Face está habilitada
print("HF_API_TOKEN carregado?", bool(HF_API_TOKEN)) #Indica se o token foi carregado

csv_file_path = "SDW2023.csv" #Caminho do arquivo CSV

client = InferenceClient(model=HF_MODEL_ID, token=HF_API_TOKEN) if HF_ENABLED else None

#Extract
def fetch_users_from_csv(path: str): 
    df = pd.read_csv(path)

    #Separa colunas
    required = {"UserID", "Name", "Balance"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Colunas faltando no CSV: {missing}. Colunas enontradas: {list(df.columns)}")

    users = []
    for  _, row in df.iterrows():
        users.append({
            "id": int(row["UserID"]),
            "name": row["Name"],
            "account": {"balance": float(row["Balance"])},
            "news": []
        })
    return users

#Transform - segmentacao
def classify_user_segment(user: dict) -> str: #Classifica o usuário em um segmento baseado no saldo da conta( iniciante: até 5mil; entre 5mil e 10mil: crescendo e acima de 10mil: investidor)
    balance = float(user.get("account", {}).get("balance", 0))

    if balance <= 5000:
        return "iniciante"
    elif 5000 < balance <= 10000:
            return "crescendo"
    else:
            return "investidor"

segment_descriptions = {
    "iniciante": (
      "Usuário com saldo de até R$5.000,00. "
      "Objetivo: Perfil focado em educação financeira e primeiros investimentos, bem como mostrar a importancia de comecar a investir aos poucos"
     ),
    "crescendo": (
      "Usuário com saldo entre R$5.000,01 e R$10.000,00. "
      "Objetivo: Perfil em crescimento financeiro, buscando diversificação de investimentos e melhores rendimentos."
     ),
    "investidor": (
      "Usuário com saldo acima de R$10.000,00. "
      "Objetivo: Perfil experiente, focado em maximizar retornos, crescimento a longo prazo e explorar oportunidades avançadas de investimento."
     ),
}

fallback_templates = {
    "iniciante": "{nome_cliente}, comece a investir aos poucos e construa um futuro financeiro mais seguro.",
    "crescendo": "{nome_cliente}, direcione parte do seu saldo para investimentos e faça seu dinheiro crescer.",
    "investidor": "{nome_cliente}, diversificar investimentos pode potencializar seus resultados no longo prazo.",
}

#Gerar um template por sergmento via Hugging Face
def hf_generate_text(prompt: str) -> str:
    if not HF_ENABLED:
        raise RuntimeError("Hugging Face API não está habilitada. Verifique o token e a configuração.")
    
    messages = [
        {"role": "system", "content": "Você é um especialista em marketing bancário."},
        {"role": "user", "content": prompt}
    ]
    resp = client.chat.completions.create(
        model=HF_MODEL_ID, 
        messages=messages,
        max_tokens=140,
        temperature=0.7,
        top_p=0.9,
    )
    return resp.choices[0].message.content.strip()

def generate_segment_template(segment: str) -> str:
    description = segment_descriptions.get(segment, "")
    if isinstance(description, tuple):
        description = " ".join(description)
    prompt = (
        "Você é um especialista em marketing bancário de um grande banco. \n"
        "Crie uma mensagem personalizada de até 140 caracteres em PT_BR sobre a importância dos investimentos para clientes de acordo com os segmentos:\n"
        "use exatamente o marcador {nome_cliente} onde devo inserir o nome do cliente.\n"
        f"Segmento: {segment}\n"
        f"Descrição do segmento: {description}\n"
        "Importante: Não coloque aspas na frase. Não adicione explicações, apenas a frase final.\n"
    )
    
    try:
       text = hf_generate_text(prompt) #Gera o texto via Hugging Face
       if "{nome_cliente}" not in text:
           text = f"{{nome_cliente}}, {text}"
           text = text[:140]
           
       return text

    except Exception as e: #Trata erros na geração do template, se der algum problema, usamos msg fixas
        print(f"[warrn] Usando mensagem fixa para o segmento {segment} devido ao erro: {e}")
        return fallback_templates[segment]
    
def generate_templates_for_segments(segments): #Gera templates por segmento
    templates = {}

    for segment in set(segments):
        templates[segment] = generate_segment_template(segment)

    return templates

#Montar mensagem persolizada para cada usuário
def build_user_message(user: dict, template: str) -> str:  #Substitui o marcador {nome_cliente} pelo nome real do cliente na mensagem
    return template.format(nome_cliente=user.get("name", "cliente"))

def attach_news_to_users(users, segment_templates): #Para cada usuário descobre o segmento, pega o template correspondente, monta a mensagem personalizada e adiciona o user [news]
    for user in users:
        segment = classify_user_segment(user)
        template = segment_templates[segment]
        message = build_user_message(user, template)

        user.setdefault("news", [])
        user["news"].append({
            "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
            "description": message
            })

#Load - salvar output em JSON
def save_output(users):
    with open("output_users_with_news.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
            

#Função principal (ETL completo)
def main():
    #1. Extract
    print("Extraindo dados do CSV")
    users = fetch_users_from_csv(csv_file_path)
    print(f"[INFO] Usuários obtidos: {[u['name'] for u in users]}")

    #2. Transform
    print("\n[ETAPA] Transform - Segmentação de usuários")
    segments = [classify_user_segment(user) for user in users]
    templates = generate_templates_for_segments(segments)
    attach_news_to_users(users, templates)
    print(f"[INFO] Segmentos identificados: {set(segments)}")

    #3. Load
    print("\n[ETAPA] load - Salvando resultados")
    save_output(users)
    print("[INFO] Arquivo output_users_with_news.json salvo com sucesso.")

if __name__ == "__main__":
    main()