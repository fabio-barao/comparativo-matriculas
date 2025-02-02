import streamlit as st
from cryptography.fernet import Fernet
import os

st.title("🔍 Teste de Descriptografia do Banco de Dados")

# 📌 Caminhos dos arquivos
DB_DIR = os.path.join(os.getcwd(), ".db")
ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")
CHAVE_FILE = os.path.join(os.getcwd(), "chave.key")  # Ajuste conforme necessário

# 🔍 Verificar se os arquivos existem
if not os.path.exists(ENCRYPTED_DB_PATH):
    st.error(f"❌ O banco de dados criptografado `{ENCRYPTED_DB_PATH}` não foi encontrado.")
    st.stop()

if not os.path.exists(CHAVE_FILE):
    st.error(f"❌ O arquivo de chave `{CHAVE_FILE}` não foi encontrado.")
    st.stop()

# 🔓 Função para descriptografar o banco de dados
def descriptografar_banco():
    try:
        # Ler a chave de criptografia
        with open(CHAVE_FILE, "rb") as chave_file:
            chave = chave_file.read()

        cipher = Fernet(chave)

        # Ler o banco criptografado
        with open(ENCRYPTED_DB_PATH, "rb") as banco_encriptado:
            dados_encriptados = banco_encriptado.read()

        # Descriptografar os dados
        dados_descriptografados = cipher.decrypt(dados_encriptados)

        # Salvar o banco descriptografado
        with open(DB_PATH, "wb") as banco:
            banco.write(dados_descriptografados)

        st.success(f"✅ Banco de dados descriptografado com sucesso para `{DB_PATH}`!")
    except Exception as e:
        st.error(f"❌ Erro ao descriptografar o banco de dados: {e}")

# 🔓 Executar descriptografia
st.write("🔄 Tentando descriptografar o banco de dados...")
descriptografar_banco()
