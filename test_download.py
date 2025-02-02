import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

st.title("📡 Teste de Download do Banco de Dados")

try:
    # 📌 Carregar credenciais do Streamlit Secrets
    credentials_info = dict(st.secrets["GOOGLE_DRIVE_CREDENTIALS"])

    # 🔐 Autenticação com a conta de serviço
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
    )

    # 📡 Conectar à API do Google Drive
    service = build("drive", "v3", credentials=credentials)

    # 📌 Nome do arquivo criptografado no Google Drive
    FILE_NAME = "matriculas_encrypted.db"

    # 🔍 Buscar o arquivo no Google Drive
    st.write("🔍 Procurando arquivo no Google Drive...")
    results = service.files().list(q=f"name = '{FILE_NAME}'", fields="files(id, name)").execute()
    arquivos = results.get("files", [])

    if not arquivos:
        st.error("❌ Arquivo não encontrado no Google Drive!")
    else:
        arquivo_id = arquivos[0]["id"]
        st.success(f"✅ Arquivo encontrado! ID: {arquivo_id}")

        # 📥 Baixar o arquivo
        st.write("⬇️ Baixando arquivo...")
        request = service.files().get_media(fileId=arquivo_id)

        # Criar pasta local para armazenar o banco de dados
        DB_DIR = os.path.join(os.getcwd(), ".db")
        os.makedirs(DB_DIR, exist_ok=True)

        # Salvar arquivo baixado
        ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")
        with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
            banco_encriptado.write(request.execute())

        st.success("✅ Arquivo baixado com sucesso!")

except Exception as e:
    st.error("❌ Erro ao conectar com o Google Drive:")
    st.code(str(e))
