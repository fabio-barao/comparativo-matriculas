import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.title("🔍 Teste de Autenticação no Google Drive")

try:
    # 🔑 Testar se as credenciais estão no Streamlit Secrets
    if "GOOGLE_DRIVE_CREDENTIALS" in st.secrets:
        st.success("✅ A chave 'GOOGLE_DRIVE_CREDENTIALS' foi encontrada no Streamlit Secrets.")

        # ❌ REMOVA json.loads() E USE DIRETAMENTE st.secrets
        credentials_info = st.secrets["GOOGLE_DRIVE_CREDENTIALS"]
        
        # 🔐 Tentar autenticar
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=credentials)

        # 📂 Testar acesso ao Google Drive listando arquivos
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        arquivos = results.get("files", [])

        if arquivos:
            st.success("✅ Conexão com o Google Drive bem-sucedida! Aqui estão alguns arquivos:")
            for arquivo in arquivos:
                st.write(f"📄 {arquivo['name']} (ID: {arquivo['id']})")
        else:
            st.warning("⚠️ Conexão feita, mas nenhum arquivo foi encontrado no Google Drive.")

    else:
        st.error("❌ A chave 'GOOGLE_DRIVE_CREDENTIALS' não foi encontrada no Streamlit Secrets.")
except Exception as e:
    st.error("❌ Erro ao autenticar no Google Drive:")
    st.text(str(e))
