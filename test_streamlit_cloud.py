import streamlit as st
import os
import subprocess

st.title("🔍 Debug - Testando Ambiente no Streamlit Cloud")

# 📂 Verificar diretório de trabalho
st.write(f"📂 Diretório de trabalho atual: `{os.getcwd()}`")

# 📂 Listar arquivos no diretório
arquivos = os.listdir(".")
st.write("📂 Arquivos no diretório raiz:", arquivos)

# 📂 Verificar se o banco de dados existe
DB_PATH = "matriculas.db"
if os.path.exists(DB_PATH):
    st.success(f"✅ O banco `{DB_PATH}` existe no ambiente do Streamlit Cloud!")
else:
    st.error(f"❌ O banco `{DB_PATH}` NÃO foi encontrado no ambiente do Streamlit Cloud!")

# 📡 Testar Download do Banco de Dados
st.subheader("📡 Testar Download do Banco de Dados")

if st.button("📥 Baixar Banco do Google Drive"):
    try:
        subprocess.run(["python", "download_db.py"], check=True)
        st.success("✅ Banco de dados baixado com sucesso!")
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Erro ao baixar o banco: {e}")
