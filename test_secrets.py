import streamlit as st
import json

st.title("🔍 Teste de Credenciais - Streamlit Secrets")

# Verificar se o Streamlit está acessando as credenciais corretamente
try:
    credentials_info = dict(st.secrets["GOOGLE_DRIVE_CREDENTIALS"])  # Converte para dicionário normal
    st.success("✅ Streamlit conseguiu acessar as credenciais!")

    # Exibir os primeiros 200 caracteres das credenciais de forma segura
    credentials_preview = json.dumps(credentials_info, indent=2)[:200]
    st.code(credentials_preview, language="json")

except Exception as e:
    st.error("❌ Erro ao acessar as credenciais no Streamlit Secrets:")
    st.code(str(e))
