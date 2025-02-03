import subprocess
import streamlit as st

if st.button("⚙️ Instalar Dependências"):
    try:
        result = subprocess.run(["python", "install_requirements.py"], capture_output=True, text=True, check=True)
        st.write("✅ Dependências instaladas com sucesso!")
        st.text("📜 Saída do script:\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("❌ Erro ao instalar dependências")
        st.text("📜 Erro Completo:\n" + (e.stderr if e.stderr else "Nenhuma saída"))







import subprocess
import streamlit as st
import os

st.write("## 🔍 Diagnóstico do Banco de Dados")

# 📂 Listar arquivos no diretório antes de rodar o script
if st.button("📂 Verificar Arquivos no Streamlit Cloud"):
    arquivos = os.listdir(".")
    st.write("📁 Arquivos no Diretório:", arquivos)

# 🔄 Botão para baixar o banco de dados manualmente
if st.button("🔄 Baixar Banco de Dados"):
    try:
        st.write("📢 Tentando rodar `download_db.py`...")

        # Executar o script e capturar saída e erro
        result = subprocess.run(
            ["python", "download_db.py"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        st.write("📜 Saída do script:")
        st.text(result.stdout if result.stdout else "⚠️ Nenhuma saída padrão")

        st.write("📜 Erro do script:")
        st.text(result.stderr if result.stderr else "✅ Nenhum erro detectado")

    except Exception as e:
        st.error(f"❌ Erro inesperado ao rodar download_db.py: {e}")
















import streamlit as st
import sqlite3
import pandas as pd
import io
import os
import hashlib
import subprocess



st.write("🔍 Diagnóstico do Banco de Dados no Streamlit Cloud")

db_dir = os.path.join(os.getcwd(), ".db")
encrypted_db_path = os.path.join(db_dir, "matriculas_encrypted.db")
decrypted_db_path = os.path.join(db_dir, "matriculas.db")

# 📂 Verificar se os arquivos existem
st.write(f"📂 Diretório onde os bancos devem estar: {db_dir}")

if os.path.exists(db_dir):
    arquivos_db = os.listdir(db_dir)
    st.write("📁 Arquivos na pasta .db:", arquivos_db)
else:
    st.write("❌ Diretório .db não encontrado!")

# 📌 Verificar os arquivos individualmente
st.write(f"🔍 Banco criptografado encontrado? {'✅ Sim' if os.path.exists(encrypted_db_path) else '❌ Não'}")
st.write(f"🔍 Banco descriptografado encontrado? {'✅ Sim' if os.path.exists(decrypted_db_path) else '❌ Não'}")






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
            subprocess.run(["python", "download_db.py"], check=True)
            st.success("✅ Banco de dados baixado e pronto para uso!")
        except subprocess.CalledProcessError:
            st.error("❌ Erro ao baixar o banco de dados. Tente novamente mais tarde.")

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


import sqlite3

st.write("🔍 Diagnóstico do Banco de Dados no Streamlit Cloud")

# 📌 Verificar se o arquivo do banco existe
if os.path.exists(DB_NAME):
    st.success(f"✅ Banco de dados encontrado: {DB_NAME}")

    conn = sqlite3.connect(DB_NAME)

    # 📌 Listar tabelas no banco
    tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
    st.write("📋 Tabelas no Banco de Dados:", tabelas)

    # 📌 Verificar se há registros na tabela 'matriculas'
    try:
        df_teste = pd.read_sql("SELECT * FROM matriculas LIMIT 5;", conn)
        st.write("📊 Registros na Tabela 'matriculas':", df_teste.shape[0])
        st.write("📊 Amostra de Dados:", df_teste)
    except Exception as e:
        st.write(f"❌ Erro ao acessar a tabela 'matriculas': {e}")

    conn.close()
else:
    st.error("❌ O arquivo do banco de dados não foi encontrado no ambiente do Streamlit Cloud!")









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

st.subheader("📥 Registros Adicionados")
st.dataframe(df_hoje[df_hoje["RA"].isin(adicionados)])

st.subheader("📤 Registros Removidos")
st.dataframe(df_ontem[df_ontem["RA"].isin(removidos)])

st.subheader("✏️ Registros Alterados")
st.dataframe(df_hoje[df_hoje["RA"].isin(alterados)])

st.subheader("📂 Exportar Dados")
if not df_hoje[df_hoje["RA"].isin(adicionados)].empty:
    st.download_button("📥 Baixar Registros Adicionados", data=gerar_download(df_hoje[df_hoje["RA"].isin(adicionados)], "adicionados.xlsx"), file_name="adicionados.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
