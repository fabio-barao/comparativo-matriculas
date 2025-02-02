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
st.subheader("📡 Testar Execução Manual do `download_db.py`")

if st.button("🔄 Rodar `download_db.py`"):
    try:
        result = subprocess.run(
            ["python", "download_db.py"],
            capture_output=True,
            text=True,
            check=True
        )
        st.success("✅ `download_db.py` foi executado com sucesso!")
        st.text("📜 Saída do script (stdout):\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("❌ Erro ao rodar `download_db.py`")
        st.text("📜 Saída Padrão (stdout):\n" + (e.stdout if e.stdout else "Nenhuma saída"))
        st.text("📜 Erro Completo (stderr):\n" + (e.stderr if e.stderr else "Nenhuma saída"))