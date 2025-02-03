import streamlit as st
import sqlite3
import pandas as pd
import io
import os
import hashlib
import subprocess

# 🚀 Configuração do diretório seguro para o banco de dados
DB_DIR = os.path.join(os.getcwd(), ".db")
DB_NAME = os.path.join(DB_DIR, "matriculas.db")

# Criar o diretório se não existir
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# 🔄 Função para garantir que o banco de dados esteja disponível
def verificar_e_baixar_banco():
    if not os.path.exists(DB_NAME):
        st.warning("📡 Banco de dados não encontrado. Baixando do Google Drive...")
        try:
            result = subprocess.run(["python", "download_db.py"], capture_output=True, text=True, check=True)
            st.write("📜 Saída do script:")
            st.text(result.stdout if result.stdout else "⚠️ Nenhuma saída padrão")

            if os.path.exists(DB_NAME):
                st.success("✅ Banco de dados baixado e pronto para uso!")
            else:
                st.error("❌ Banco não foi encontrado após o download.")
        except subprocess.CalledProcessError as e:
            st.error("❌ Erro ao baixar o banco de dados.")
            st.text(e.stderr if e.stderr else "Nenhuma saída de erro")

# 🔒 Configuração de Login com Hash
USER_CREDENTIALS = {
    "vamille": hashlib.sha256("Xz9@Lm3#Pq7!Vk8$Tn5".encode()).hexdigest()
}

def autenticar():
    """Função para exibir a tela de login segura."""
    st.sidebar.title("🔒 Login")
    usuario = st.sidebar.text_input("Usuário", key="usuario")
    senha = st.sidebar.text_input("Senha", type="password", key="senha")
    botao_login = st.sidebar.button("Login")

    if botao_login:
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        if usuario in USER_CREDENTIALS and USER_CREDENTIALS[usuario] == senha_hash:
            st.session_state["autenticado"] = True
            st.sidebar.success(f"✅ Bem-vindo, {usuario}!")
            st.rerun()
        else:
            st.sidebar.error("❌ Usuário ou senha incorretos!")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    autenticar()
    st.stop()

# 🔄 Verificar se o banco existe e baixá-lo caso necessário
verificar_e_baixar_banco()

def obter_dados():
    """Obtém os dados do banco de dados SQLite e verifica a existência da tabela e coluna."""
    if not os.path.exists(DB_NAME):
        st.error("❌ O banco de dados ainda não foi criado. Aguarde a primeira atualização!")
        return pd.DataFrame()

    conn = sqlite3.connect(DB_NAME)

    # 📌 Verificar se a tabela existe
    query_check_table = "SELECT name FROM sqlite_master WHERE type='table' AND name='matriculas';"
    tabela_existe = pd.read_sql(query_check_table, conn)

    if tabela_existe.empty:
        st.error("❌ A tabela 'matriculas' não foi encontrada no banco de dados!")
        conn.close()
        return pd.DataFrame()

    # 📌 Verificar se a coluna DATA_CRIACAO existe
    query_check_columns = "PRAGMA table_info(matriculas);"
    colunas = pd.read_sql(query_check_columns, conn)

    if "DATA_CRIACAO" not in colunas["name"].values:
        st.error("❌ A coluna 'DATA_CRIACAO' não existe na tabela 'matriculas'.")
        conn.close()
        return pd.DataFrame()

    # 📌 Se tudo estiver certo, carregar os dados
    query = "SELECT * FROM matriculas ORDER BY DATA_CRIACAO DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    
    df["DATA_CRIACAO"] = pd.to_datetime(df["DATA_CRIACAO"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["DATA_CRIACAO"])  # Remover valores NaT

    return df

def separar_dias(df, data_hoje, data_ontem):
    """Filtra os registros para as datas selecionadas."""
    df_hoje = df[df["DATA_CRIACAO"].dt.date == data_hoje]
    df_ontem = df[df["DATA_CRIACAO"].dt.date == data_ontem]
    return df_hoje, df_ontem

def comparar_dados(df_hoje, df_ontem):
    """Compara os dados de hoje e ontem e identifica mudanças."""
    df_hoje_filtrado = df_hoje.drop(columns=["DATA_CRIACAO"], errors="ignore")
    df_ontem_filtrado = df_ontem.drop(columns=["DATA_CRIACAO"], errors="ignore")

    dict_hoje = df_hoje_filtrado.set_index("RA").to_dict("index")
    dict_ontem = df_ontem_filtrado.set_index("RA").to_dict("index")

    adicionados = [ra for ra in dict_hoje.keys() if ra not in dict_ontem]
    removidos = [ra for ra in dict_ontem.keys() if ra not in dict_hoje]
    alterados = [ra for ra in dict_hoje.keys() & dict_ontem.keys() 
                 if not pd.Series(dict_hoje[ra]).equals(pd.Series(dict_ontem[ra]))]

    return adicionados, removidos, alterados

def gerar_download(df, nome_arquivo):
    """Gera um arquivo Excel para download."""
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer

# Ajustar a exibição do título
st.markdown("""
    <h1 style='text-align: center;'>📊 Comparação de Matrículas Diário</h1>
""", unsafe_allow_html=True)

df = obter_dados()

if df.empty:
    st.error("❌ Nenhum dado disponível no banco. Aguarde atualizações!")
    st.stop()

datas_unicas = sorted(df["DATA_CRIACAO"].dropna().dt.date.unique(), reverse=True)

if len(datas_unicas) < 2:
    st.error("❌ Dados insuficientes para comparar. Aguarde mais atualizações!")
    st.stop()

st.sidebar.header("📅 Selecione as Datas para Comparação")
data_hoje = st.sidebar.selectbox("Selecione a data mais recente", datas_unicas, index=0)
data_ontem = st.sidebar.selectbox("Selecione a data anterior", datas_unicas, index=1 if len(datas_unicas) > 1 else 0)

df_hoje, df_ontem = separar_dias(df, data_hoje, data_ontem)

st.write(f"📆 Comparando dados de **{data_ontem.strftime('%d/%m/%Y')}** com **{data_hoje.strftime('%d/%m/%Y')}**")

adicionados, removidos, alterados = comparar_dados(df_hoje, df_ontem)

st.metric(label="📥 Registros Adicionados", value=len(adicionados))
st.metric(label="📤 Registros Removidos", value=len(removidos))
st.metric(label="✏️ Registros Alterados", value=len(alterados))
