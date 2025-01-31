import streamlit as st
import sqlite3
import pandas as pd
import io

# 🚀 Configuração de Login
USER_CREDENTIALS = {
    "vamille": "Xz9@Lm3#Pq7!Vk8$Tn5"  # Defina um usuário e senha aqui
}

def autenticar():
    """Função para exibir a tela de login"""
    st.sidebar.title("🔒 Login")
    usuario = st.sidebar.text_input("Usuário", key="usuario")
    senha = st.sidebar.text_input("Senha", type="password", key="senha")
    botao_login = st.sidebar.button("Login")

    if botao_login:
        if usuario in USER_CREDENTIALS and USER_CREDENTIALS[usuario] == senha:
            # ⚠️ Corrigindo o erro de sessão do Streamlit
            st.session_state["autenticado"] = True
            st.experimental_set_query_params(usuario=usuario)  # Armazena de forma segura
            st.sidebar.success(f"✅ Bem-vindo, {usuario}!")
            st.rerun()  # ⚠️ Força a página a recarregar corretamente
        else:
            st.sidebar.error("❌ Usuário ou senha incorretos!")

# 🚀 Verifica se o usuário está autenticado
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    autenticar()
    st.stop()  # Para o Streamlit até que o usuário faça login

# 💾 Conectar ao banco SQLite
DB_NAME = "matriculas.db"

def obter_dados():
    """Obtém os registros do banco e retorna um DataFrame ordenado por data mais recente"""
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM matriculas ORDER BY DATA_CRIACAO DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def separar_dias(df):
    """Separa os registros do dia mais recente e do dia anterior"""
    df["DATA_CRIACAO"] = pd.to_datetime(df["DATA_CRIACAO"])  
    datas_unicas = sorted(df["DATA_CRIACAO"].unique(), reverse=True)  

    if len(datas_unicas) < 2:
        return df[df["DATA_CRIACAO"] == datas_unicas[0]], pd.DataFrame(), datas_unicas[0], datas_unicas[0]

    data_hoje = datas_unicas[0]
    data_ontem = datas_unicas[1]

    df_hoje = df[df["DATA_CRIACAO"] == data_hoje]
    df_ontem = df[df["DATA_CRIACAO"] == data_ontem]

    return df_hoje, df_ontem, data_ontem, data_hoje

def comparar_dados(df_hoje, df_ontem):
    """Compara os dados de hoje e ontem e identifica mudanças"""
    df_hoje_filtrado = df_hoje.drop(columns=["DATA_CRIACAO"], errors="ignore")
    df_ontem_filtrado = df_ontem.drop(columns=["DATA_CRIACAO"], errors="ignore")

    dict_hoje = df_hoje_filtrado.set_index("RA").to_dict("index")
    dict_ontem = df_ontem_filtrado.set_index("RA").to_dict("index")

    adicionados = [ra for ra in dict_hoje.keys() if ra not in dict_ontem]
    removidos = [ra for ra in dict_ontem.keys() if ra not in dict_hoje]
    alterados = [ra for ra in dict_hoje.keys() & dict_ontem.keys() if dict_hoje[ra] != dict_ontem[ra]]

    return adicionados, removidos, alterados

# 🚀 Interface do Streamlit
st.title("📊 Comparação de Matrículas Diário")

df = obter_dados()
df_hoje, df_ontem, data_ontem, data_hoje = separar_dias(df)

st.write(f"📆 Comparando dados de **{data_ontem.strftime('%d/%m/%Y')}** com **{data_hoje.strftime('%d/%m/%Y')}**")

adicionados, removidos, alterados = comparar_dados(df_hoje, df_ontem)

# 📌 Exibir métricas
st.metric(label="📥 Registros Adicionados", value=len(adicionados))
st.metric(label="📤 Registros Removidos", value=len(removidos))
st.metric(label="✏️ Registros Alterados", value=len(alterados))

st.subheader("📂 Exportar Dados")

def gerar_download(df, nome_arquivo):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer

# Botão para baixar adicionados
if len(adicionados) > 0:
    df_adicionados = df_hoje[df_hoje["RA"].isin(adicionados)]
    st.download_button(
        label="📥 Baixar Registros Adicionados",
        data=gerar_download(df_adicionados, "adicionados.xlsx"),
        file_name="adicionados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Botão para baixar removidos
if len(removidos) > 0:
    df_removidos = df_ontem[df_ontem["RA"].isin(removidos)]
    st.download_button(
        label="📤 Baixar Registros Removidos",
        data=gerar_download(df_removidos, "removidos.xlsx"),
        file_name="removidos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Botão para baixar alterados
if len(alterados) > 0:
    df_alterados = df_hoje[df_hoje["RA"].isin(alterados)]
    st.download_button(
        label="✏️ Baixar Registros Alterados",
        data=gerar_download(df_alterados, "alterados.xlsx"),
        file_name="alterados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
