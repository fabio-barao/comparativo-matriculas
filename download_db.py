import os
import json
import sys
import traceback
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cryptography.fernet import Fernet

def log(mensagem):
    """Escreve logs na tela, usando Streamlit se disponível."""
    if "streamlit" in sys.modules:
        import streamlit as st
        st.write(mensagem)
    else:
        print(mensagem)

log("🚀 Iniciando download_db.py...")

try:
    log("📂 Diretório atual: " + os.getcwd())
    log("📁 Arquivos no diretório: " + str(os.listdir(".")))
except Exception as e:
    log(f"❌ Erro ao listar arquivos no diretório: {e}")
    log(traceback.format_exc())

# 🚀 Carregar credenciais do Google Drive corretamente
try:
    if "GOOGLE_DRIVE_CREDENTIALS" in os.environ or "streamlit" in sys.modules:
        import streamlit as st
        log("📂 Rodando no Streamlit Cloud, carregando credenciais do secrets.toml")
        credentials_info = json.loads(st.secrets["GOOGLE_DRIVE_CREDENTIALS"])  # Garante que é um dicionário
    else:
        log("🖥️ Rodando no terminal, carregando credenciais do arquivo JSON")
        with open("credentials.json") as f:
            credentials_info = json.load(f)

    log("✅ Credenciais carregadas com sucesso.")
except Exception as e:
    log(f"❌ Erro ao carregar credenciais: {e}")
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

# 🔍 Buscar arquivo no Google Drive
try:
    FILE_NAME = "matriculas_encrypted.db"
    log(f"🔍 Buscando '{FILE_NAME}' no Google Drive...")

    query = f"name = '{FILE_NAME}'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = results.get("files", [])

    if arquivos:
        arquivo_id = arquivos[0]["id"]
        log(f"✅ Arquivo encontrado: {arquivos[0]['name']} (ID: {arquivo_id})")
    else:
        log("❌ Nenhum arquivo correspondente encontrado no Google Drive.")
        sys.exit(1)
except Exception as e:
    log(f"❌ Erro ao buscar arquivo no Google Drive: {e}")
    log(traceback.format_exc())
    sys.exit(1)

# 🔽 Baixar o banco de dados
try:
    log("📥 Iniciando download do banco de dados...")
    DB_DIR = os.path.join(os.getcwd(), ".db")
    os.makedirs(DB_DIR, exist_ok=True)

    ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")

    request = service.files().get_media(fileId=arquivo_id)

    with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
        banco_encriptado.write(request.execute())

    log("✅ Banco criptografado baixado com sucesso!")
except Exception as e:
    log(f"❌ Erro ao baixar o banco de dados: {e}")
    log(traceback.format_exc())
    sys.exit(1)

log("✅ `download_db.py` finalizado com sucesso!")
