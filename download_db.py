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
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as cred_file:
        raw_data = cred_file.read()

    # 🔹 Removendo caracteres de controle inválidos
    raw_data = raw_data.replace("\r", "").strip()

    # 🔹 Decodificando JSON corretamente
    credentials_info = json.loads(raw_data)

    if not credentials_info:
        log("❌ ERRO: O arquivo credentials.json está vazio ou corrompido!")
        sys.exit(1)

    # 🔹 Restaurando quebras de linha na private_key
    if "private_key" in credentials_info:
        credentials_info["private_key"] = credentials_info["private_key"].replace("\\n", "\n")

    log("✅ Credenciais carregadas com sucesso do arquivo JSON.")

except json.JSONDecodeError as e:
    log(f"❌ Erro ao carregar credentials.json: JSON inválido! {e}")
    log(traceback.format_exc())
    sys.exit(1)

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
