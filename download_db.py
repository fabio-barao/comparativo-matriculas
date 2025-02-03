import os
import json
import sys
import traceback
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cryptography.fernet import Fernet

# 📢 Função de Log Simples (sem Streamlit)
def log(mensagem):
    """Escreve logs diretamente no terminal"""
    print(mensagem)

log("🚀 Iniciando download_db.py...")

# 📂 Listar diretório atual e arquivos disponíveis
try:
    log(f"📂 Diretório atual: {os.getcwd()}")
    log(f"📁 Arquivos no diretório: {os.listdir(os.getcwd())}")
except Exception as e:
    log(f"❌ Erro ao listar arquivos no diretório: {e}")
    log(traceback.format_exc())

# 📌 Caminhos dos arquivos
CURRENT_DIR = os.getcwd()
CHAVE_FILE = os.path.join(CURRENT_DIR, "chave.key")
DB_DIR = os.path.join(CURRENT_DIR, ".db")
ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")  # <-- ADICIONADO AQUI

# 🚀 Carregar credenciais do Google Drive corretamente
try:
    import streamlit as st

    # Streamlit Cloud -> Pegamos as credenciais do secrets.toml
    if "GOOGLE_DRIVE_CREDENTIALS" in st.secrets:
        log("📂 Rodando no Streamlit Cloud, carregando credenciais do secrets.toml")
        credentials_info = dict(st.secrets["GOOGLE_DRIVE_CREDENTIALS"])  # Correção aqui
    
    # Ambiente Local -> Usamos credentials.json
    elif os.path.exists("credentials.json"):
        log("🖥️ Rodando no terminal, carregando credenciais do arquivo JSON")
        with open("credentials.json") as f:
            credentials_info = json.load(f)
    
    # Caso nenhuma credencial seja encontrada
    else:
        raise FileNotFoundError("Nenhuma credencial foi encontrada! Verifique `secrets.toml` no Streamlit Cloud ou `credentials.json` no ambiente local.")

    log("✅ Credenciais carregadas com sucesso.")
except Exception as e:
    log(f"❌ Erro ao carregar credenciais: {e}")
    log(traceback.format_exc())
    sys.exit(1)


log(f"🔍 Variáveis de ambiente disponíveis: {os.environ.keys()}")
log(f"🔍 GOOGLE_DRIVE_CREDENTIALS detectado? {'GOOGLE_DRIVE_CREDENTIALS' in os.environ}")


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
    os.makedirs(DB_DIR, exist_ok=True)

    request = service.files().get_media(fileId=arquivo_id)

    with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
        banco_encriptado.write(request.execute())

    log(f"✅ Banco criptografado baixado com sucesso e salvo em {ENCRYPTED_DB_PATH}")

except Exception as e:
    log(f"❌ Erro ao baixar o banco de dados: {e}")
    log(traceback.format_exc())
    sys.exit(1)

log("✅ `download_db.py` finalizado com sucesso!")

# 🔓 Função para descriptografar o banco de dados
def descriptografar_banco():
    try:
        log("🔓 Tentando descriptografar o banco de dados...")

        # Verificar se a chave existe
        if not os.path.exists(CHAVE_FILE):
            log("❌ Arquivo de chave de criptografia não encontrado!")
            return

        # Ler a chave
        with open(CHAVE_FILE, "rb") as chave_file:
            chave = chave_file.read()

        cipher = Fernet(chave)

        # Verificar se o banco criptografado existe
        if not os.path.exists(ENCRYPTED_DB_PATH):
            log("❌ Banco criptografado não encontrado!")
            return

        # Ler o banco criptografado e descriptografar
        with open(ENCRYPTED_DB_PATH, "rb") as banco_encriptado:
            dados_encriptados = banco_encriptado.read()

        dados_descriptografados = cipher.decrypt(dados_encriptados)

        # Salvar o banco descriptografado
        with open(DB_PATH, "wb") as banco:
            banco.write(dados_descriptografados)

        log(f"✅ Banco de dados descriptografado com sucesso e salvo em {DB_PATH}")
    except Exception as e:
        log(f"❌ Erro ao descriptografar o banco de dados: {e}")
        log(traceback.format_exc())

# 🔓 Rodar a descriptografia após o download
descriptografar_banco()
