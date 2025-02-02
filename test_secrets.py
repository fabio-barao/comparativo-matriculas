import streamlit as st
import json

st.title("🔍 Teste de Credenciais - Streamlit Secrets")

# Verificar se o Streamlit está acessando as credenciais corretamente
try:
    credentials_info = st.secrets["GOOGLE_DRIVE_CREDENTIALS"]
    st.success("✅ Streamlit conseguiu acessar as credenciais!")
    st.write("🔑 Primeiros 200 caracteres das credenciais:")
    st.code(json.dumps(credentials_info)[:200], language="json")
except Exception as e:
    st.error("❌ Erro ao acessar as credenciais no Streamlit Secrets:")
    st.code(str(e))
