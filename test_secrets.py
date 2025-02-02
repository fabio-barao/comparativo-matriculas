import streamlit as st
import json

st.write("🔍 Teste de Credenciais - Streamlit Secrets")

try:
    if "GOOGLE_DRIVE_CREDENTIALS" in st.secrets:
        st.write("✅ A chave 'GOOGLE_DRIVE_CREDENTIALS' foi encontrada no Streamlit Secrets.")
        
        credentials_info = json.loads(st.secrets["GOOGLE_DRIVE_CREDENTIALS"])

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
