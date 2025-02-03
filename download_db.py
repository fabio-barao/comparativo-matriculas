import os
import json
import sys
import traceback  # 🔹 Adicionado para capturar erros detalhados
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cryptography.fernet import Fernet

# 📢 Função para log de mensagens
def log(mensagem):
    """Escreve logs na tela, usando Streamlit se disponível."""
    if "streamlit" in sys.modules:
        import streamlit as st
        st.write(mensagem)
    else:
        print(mensagem)

# 🚀 Forçar exibição completa de erros no Streamlit Cloud
def capturar_erros(func):
    """Decorator para capturar e exibir erros detalhados"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log(f"❌ Erro crítico em {func.__name__}: {e}")
            log(traceback.format_exc())  # 🔹 Mostra detalhes completos do erro
            sys.exit(1)
    return wrapper

# 📌 Caminhos dos arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAVE_FILE = os.path.join(CURRENT_DIR, "chave.key")
DB_DIR = os.path.join(CURRENT_DIR, ".db")
ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")

# 📌 Nome do arquivo criptografado no Google Drive
FILE_NAME = "matriculas_encrypted.db"

# 📌 Pasta no Google Drive (se houver)
FOLDER_ID = ""

# 🚀 Carregar credenciais do Google Drive
@capturar_erros
def carregar_credenciais():
    if "streamlit" in sys.modules:
        import streamlit as st
        log("📂 Rodando no Streamlit Cloud, carregando credenciais do secrets.toml")
        return json.loads(st.secrets["GOOGLE_DRIVE_CREDENTIALS"])  # Garante que `st.secrets` seja lido corretamente
    else:
        log("🖥️ Rodando no terminal, carregando credenciais do arquivo JSON")
        with open("credentials.json") as f:
            return json.load(f)

credentials_info = carregar_credenciais()

@capturar_erros
def autenticar_google_drive():
    """Autentica no Google Drive e retorna o serviço."""
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)

service = autenticar_google_drive()
log("✅ Autenticação no Google Drive bem-sucedida.")

@capturar_erros
def encontrar_arquivo(nome_arquivo):
    """Busca o arquivo no Google Drive e retorna seu ID."""
    log(f"🔍 Buscando '{nome_arquivo}' no Google Drive...")
    query = f"name = '{nome_arquivo}'"
    if FOLDER_ID:
        query += f" and '{FOLDER_ID}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = results.get("files", [])

    if arquivos:
        log(f"✅ Arquivo encontrado: {arquivos[0]['name']} (ID: {arquivos[0]['id']})")
        return arquivos[0]["id"]
    else:
        log("❌ Nenhum arquivo correspondente encontrado no Google Drive.")
        return None

@capturar_erros
def descriptografar_banco():
    """Descriptografa o banco de dados."""
    if not os.path.exists(ENCRYPTED_DB_PATH):
        log("❌ O arquivo criptografado não existe! Impossível descriptografar.")
        return

    with open(CHAVE_FILE, "rb") as chave_file:
        chave = chave_file.read()

    cipher = Fernet(chave)

    with open(ENCRYPTED_DB_PATH, "rb") as banco_encriptado:
        dados_encriptados = banco_encriptado.read()

    dados_descriptografados = cipher.decrypt(dados_encriptados)

    with open(DB_PATH, "wb") as banco:
        banco.write(dados_descriptografados)

    log("🔓 Banco de dados descriptografado com sucesso!")

arquivo_id = encontrar_arquivo(FILE_NAME)

@capturar_erros
def baixar_banco():
    """Baixa o banco de dados do Google Drive."""
    if not arquivo_id:
        log("❌ O banco de dados criptografado não foi encontrado no Google Drive.")
        return

    log("📥 Baixando banco de dados criptografado...")
    os.makedirs(DB_DIR, exist_ok=True)

    request = service.files().get_media(fileId=arquivo_id)

    with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
        banco_encriptado.write(request.execute())

    log("✅ Banco criptografado baixado com sucesso!")

    # 🔓 Descriptografar o banco após o download
    descriptografar_banco()

baixar_banco()
