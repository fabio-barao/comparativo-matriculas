import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "matriculas.db"

def obter_dados():
    """Obtém os registros do banco e retorna um DataFrame"""
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM matriculas ORDER BY DATA_CRIACAO DESC LIMIT 660"  # Pegamos os últimos 660 registros
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def comparar_dados(df_hoje, df_ontem):
    """Compara os dados de hoje e ontem e identifica mudanças"""

    # Transformar os DataFrames em dicionários baseados no RA
    dict_hoje = df_hoje.set_index("RA").to_dict("index")
    dict_ontem = df_ontem.set_index("RA").to_dict("index")

    # Registros adicionados (existem hoje, mas não existiam ontem)
    adicionados = [ra for ra in dict_hoje.keys() if ra not in dict_ontem]

    # Registros removidos (existiam ontem, mas não existem hoje)
    removidos = [ra for ra in dict_ontem.keys() if ra not in dict_hoje]

    # Registros alterados (existem nos dois dias, mas com diferenças)
    alterados = []
    for ra in dict_hoje.keys() & dict_ontem.keys():
        if dict_hoje[ra] != dict_ontem[ra]:  # Compara os valores
            alterados.append(ra)

    return adicionados, removidos, alterados

# 🚀 Interface do Streamlit
st.title("📊 Comparação de Matrículas Diário")

df = obter_dados()

# Ordenar por data para pegar os registros mais antigos como ontem e os mais recentes como hoje
df = df.sort_values("DATA_CRIACAO", ascending=False)

# Separar os registros de ontem e hoje
df_hoje = df.iloc[:330]  # Pegamos metade dos registros mais recentes como "hoje"
df_ontem = df.iloc[330:]  # A outra metade como "ontem"

# Pegando as datas mais recentes para exibir
data_hoje = pd.to_datetime(df_hoje["DATA_CRIACAO"]).max().strftime("%d/%m/%Y")
data_ontem = pd.to_datetime(df_ontem["DATA_CRIACAO"]).max().strftime("%d/%m/%Y")

st.write(f"📆 Comparando dados de **{data_ontem}** com **{data_hoje}**")

adicionados, removidos, alterados = comparar_dados(df_hoje, df_ontem)

# 📌 Exibir métricas
st.metric(label="📥 Registros Adicionados", value=len(adicionados))
st.metric(label="📤 Registros Removidos", value=len(removidos))
st.metric(label="✏️ Registros Alterados", value=len(alterados))

# 📊 Criando tabelas para os dados
st.subheader("📥 Registros Adicionados")
df_adicionados = df_hoje[df_hoje["RA"].isin(adicionados)]
st.dataframe(df_adicionados)

st.subheader("📤 Registros Removidos")
df_removidos = df_ontem[df_ontem["RA"].isin(removidos)]
st.dataframe(df_removidos)

st.subheader("✏️ Registros Alterados")
df_alterados = df_hoje[df_hoje["RA"].isin(alterados)]
if not df_alterados.empty:
    st.dataframe(df_alterados)
else:
    st.write("✅ Nenhum registro alterado.")

# 📂 Botões para exportar cada categoria separadamente
st.subheader("📂 Exportar Dados")

# Função para gerar e baixar arquivos Excel
def gerar_download(df, nome_arquivo):
    """Cria um link de download para um DataFrame"""
    import io
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer

# Botão para baixar adicionados
if not df_adicionados.empty:
    st.download_button(
        label="📥 Baixar Registros Adicionados",
        data=gerar_download(df_adicionados, "adicionados.xlsx"),
        file_name="adicionados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Botão para baixar removidos
if not df_removidos.empty:
    st.download_button(
        label="📤 Baixar Registros Removidos",
        data=gerar_download(df_removidos, "removidos.xlsx"),
        file_name="removidos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Botão para baixar alterados
if not df_alterados.empty:
    st.download_button(
        label="✏️ Baixar Registros Alterados",
        data=gerar_download(df_alterados, "alterados.xlsx"),
        file_name="alterados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
