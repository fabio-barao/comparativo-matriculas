import json
import os
import sys
import traceback
from google.oauth2 import service_account
from googleapiclient.discovery import build

def log(mensagem):
    """Escreve logs no terminal"""
    print(mensagem)

log("🚀 Iniciando download_db.py...")

CREDENTIALS_PATH = "credentials.json"

if not os.path.exists(CREDENTIALS_PATH):
    log("❌ ERRO: O arquivo credentials.json não foi encontrado!")
    sys.exit(1)

try:
    with open(CREDENTIALS_PATH, "r") as cred_file:
        credentials_info = json.load(cred_file)

    if not credentials_info:
        log("❌ ERRO: O arquivo credentials.json está vazio ou corrompido!")
        sys.exit(1)

    # 🔹 Restaurando quebras de linha na private_key
    if "private_key" in credentials_info:
        credentials_info["private_key"] = credentials_info["private_key"].replace(" ", "\n")

    log("✅ Credenciais carregadas com sucesso do arquivo JSON.")

except Exception as e:
    log(f"❌ Erro ao carregar credentials.json: {e}")
    log(traceback.format_exc())
    sys.exit(1)

# 🔐 Autenticação no Google Drive
try:
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    log("✅ Autenticação no Google Drive bem-sucedida.")
except Exception as e:
    log(f"❌ Erro ao autenticar no Google Drive: {e}")
    log(traceback.format_exc())
    sys.exit(1)
