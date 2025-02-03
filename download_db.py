import os
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cryptography.fernet import Fernet
import json

# 🚀 Teste de acesso ao Streamlit Secrets
st.write("🔍 Teste de Credenciais - Streamlit Secrets")

try:
    if "GOOGLE_DRIVE_CREDENTIALS" in st.secrets:
        st.write("✅ A chave 'GOOGLE_DRIVE_CREDENTIALS' foi encontrada no Streamlit Secrets.")
        
        credentials_info = st.secrets["GOOGLE_DRIVE_CREDENTIALS"]

        # Validar estrutura das credenciais
        campos_obrigatorios = ["type", "project_id", "private_key", "client_email", "token_uri"]
        campos_faltando = [campo for campo in campos_obrigatorios if campo not in credentials_info]

        if campos_faltando:
            st.write(f"⚠️ Campos faltando nas credenciais: {', '.join(campos_faltando)}")
        else:
            st.write("✅ Estrutura das credenciais está correta.")
        
        st.write("🔑 Primeiros 200 caracteres das credenciais:")
        st.write(json.dumps(credentials_info)[:200])  # Mostrar apenas um trecho por segurança
    else:
        st.write("❌ A chave 'GOOGLE_DRIVE_CREDENTIALS' não foi encontrada no Streamlit Secrets.")
except Exception as e:
    st.write("❌ Erro ao acessar as credenciais no Streamlit Secrets:")
    st.write(str(e))
    st.stop()  # Para evitar erros posteriores se as credenciais estiverem incorretas

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

# 🔐 Autenticação com a conta de serviço
try:
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    st.write("✅ Autenticação no Google Drive bem-sucedida.")
except Exception as e:
    st.write("❌ Erro ao autenticar no Google Drive:")
    st.write(str(e))
    st.stop()

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
        st.write(f"❌ Erro ao buscar o arquivo no Google Drive: {e}")
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

        st.write("🔓 Banco de dados descriptografado com sucesso!")
    except Exception as e:
        st.write("❌ Erro ao descriptografar o banco de dados:")
        st.write(str(e))

# 🔽 Baixar o banco de dados do Google Drive
arquivo_id = encontrar_arquivo(FILE_NAME)

if arquivo_id:
    try:
        # 🔽 Criar a pasta .db se não existir
        os.makedirs(DB_DIR, exist_ok=True)

        request = service.files().get_media(fileId=arquivo_id)

        with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
            banco_encriptado.write(request.execute())

        st.write("✅ Banco criptografado baixado com sucesso!")

        # 🔓 Descriptografar o banco após o download
        descriptografar_banco()
    except Exception as e:
        st.write(f"❌ Erro ao baixar o banco de dados: {e}")
else:
    st.write("❌ O banco de dados criptografado não foi encontrado no Google Drive.")