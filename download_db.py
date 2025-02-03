import os
import json
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cryptography.fernet import Fernet

# 📌 Verificar se estamos rodando dentro do Streamlit
try:
    import streamlit as st
    USANDO_STREAMLIT = True
except ImportError:
    USANDO_STREAMLIT = False  # Rodando no terminal

# 📢 Função para log de mensagens (Streamlit ou print)
def log(mensagem):
    if USANDO_STREAMLIT:
        st.write(mensagem)
    else:
        print(mensagem)

# 📌 Caminhos dos arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAVE_FILE = os.path.join(CURRENT_DIR, "chave.key")
DB_DIR = os.path.join(CURRENT_DIR, ".db")
ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")

# 📌 Nome do arquivo criptografado no Google Drive
FILE_NAME = "matriculas_encrypted.db"

# 📌 Pasta no Google Drive (se houver)
FOLDER_ID = "1gqTrWM72i44so_VXWXoLzG-xOdpoE7Rq"

# 🚀 Teste de acesso ao Streamlit Secrets
if USANDO_STREAMLIT:
    log("🔍 Teste de Credenciais - Streamlit Secrets")

try:
    if USANDO_STREAMLIT and "GOOGLE_DRIVE_CREDENTIALS" in st.secrets:
        credentials_info = st.secrets["GOOGLE_DRIVE_CREDENTIALS"]
    else:
        # Caso esteja rodando no terminal, carregar as credenciais do JSON
        with open("credentials.json") as f:
            credentials_info = json.load(f)

    log("✅ Credenciais carregadas com sucesso.")

    # 🔐 Autenticação com a conta de serviço
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    log("✅ Autenticação no Google Drive bem-sucedida.")
except Exception as e:
    log(f"❌ Erro ao autenticar no Google Drive: {e}")
    sys.exit(1)

# 🔍 Função para encontrar o arquivo no Drive
def encontrar_arquivo(nome_arquivo):
    try:
        query = f"name = '{nome_arquivo}'"
        if FOLDER_ID:
            query += f" and '{FOLDER_ID}' in parents"

        results = service.files().list(q=query, fields="files(id, name)").execute()
        arquivos = results.get("files", [])
        return arquivos[0]["id"] if arquivos else None
    except Exception as e:
        log(f"❌ Erro ao buscar o arquivo no Google Drive: {e}")
        return None

# 🔓 Função para descriptografar o banco de dados
def descriptografar_banco():
    try:
        with open(CHAVE_FILE, "rb") as chave_file:
            chave = chave_file.read()

        cipher = Fernet(chave)

        with open(ENCRYPTED_DB_PATH, "rb") as banco_encriptado:
            dados_encriptados = banco_encriptado.read()

        dados_descriptografados = cipher.decrypt(dados_encriptados)

        with open(DB_PATH, "wb") as banco:
            banco.write(dados_descriptografados)

        log("🔓 Banco de dados descriptografado com sucesso!")
    except Exception as e:
        log(f"❌ Erro ao descriptografar o banco de dados: {e}")

# 🔽 Baixar o banco de dados do Google Drive
arquivo_id = encontrar_arquivo(FILE_NAME)

if arquivo_id:
    try:
        # 🔽 Criar a pasta .db se não existir
        os.makedirs(DB_DIR, exist_ok=True)

        request = service.files().get_media(fileId=arquivo_id)

        with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
            banco_encriptado.write(request.execute())

        log("✅ Banco criptografado baixado com sucesso!")

        # 🔓 Descriptografar o banco após o download
        descriptografar_banco()
    except Exception as e:
        log(f"❌ Erro ao baixar o banco de dados: {e}")
else:
    log("❌ O banco de dados criptografado não foi encontrado no Google Drive.")
