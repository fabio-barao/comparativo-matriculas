import gspread
from google.oauth2.service_account import Credentials

# Carregar credenciais do Streamlit
import streamlit as st
creds_dict = st.secrets["google_service_account"]

# Criar credenciais
creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive"])

# Tentar autenticar no Google Drive
try:
    client = gspread.authorize(creds)
    print("✅ Autenticação bem-sucedida!")
except Exception as e:
    print(f"❌ Erro na autenticação: {e}")
