import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

st.title("🔍 Teste de Download do Banco do Google Drive")

# 📌 Nome do arquivo e ID do Google Drive (pegamos da saída do `test_auth_google.py`)
FILE_NAME = "matriculas_encrypted.db"

# 🔐 Autenticar com o Google Drive
try:
    credentials_info = st.secrets["GOOGLE_DRIVE_CREDENTIALS"]
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    st.success("✅ Autenticação no Google Drive bem-sucedida.")
except Exception as e:
    st.error(f"❌ Erro ao autenticar no Google Drive: {e}")
    st.stop()

# 🔍 Buscar o arquivo no Google Drive
def encontrar_arquivo(nome_arquivo):
    try:
        query = f"name = '{nome_arquivo}'"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        arquivos = results.get("files", [])
        return arquivos[0]["id"] if arquivos else None
    except Exception as e:
        st.error(f"❌ Erro ao buscar o arquivo no Google Drive: {e}")
        return None

arquivo_id = encontrar_arquivo(FILE_NAME)

# 📥 Fazer download do banco de dados
if arquivo_id:
    try:
        st.write(f"📄 Baixando o arquivo `{FILE_NAME}` com ID `{arquivo_id}`...")

        # Criar diretório para armazenar o banco
        DB_DIR = os.path.join(os.getcwd(), ".db")
        os.makedirs(DB_DIR, exist_ok=True)
        ENCRYPTED_DB_PATH = os.path.join(DB_DIR, FILE_NAME)

        request = service.files().get_media(fileId=arquivo_id)

        with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
            banco_encriptado.write(request.execute())

        st.success(f"✅ Arquivo `{FILE_NAME}` baixado com sucesso para `{ENCRYPTED_DB_PATH}`!")
    except Exception as e:
        st.error(f"❌ Erro ao baixar o banco de dados: {e}")
else:
    st.error(f"❌ O arquivo `{FILE_NAME}` não foi encontrado no Google Drive.")
