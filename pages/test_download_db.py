import streamlit as st
import subprocess

st.title("🔍 Teste de Download do Banco no Streamlit Cloud")

if st.button("🔄 Baixar Banco do Google Drive"):
    try:
        result = subprocess.run(
            ["python", "download_db.py"],
            capture_output=True,
            text=True,
            check=True
        )
        st.success("✅ Banco de dados baixado com sucesso!")
        st.text("📜 Saída do script (stdout):\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("❌ Erro ao baixar o banco de dados")
        st.text("📜 Saída Padrão (stdout):\n" + (e.stdout if e.stdout else "Nenhuma saída"))
        st.text("📜 Erro Completo (stderr):\n" + (e.stderr if e.stderr else "Nenhuma saída"))
