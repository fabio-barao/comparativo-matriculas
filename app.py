import streamlit as st
import sqlite3
import pandas as pd
import io

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
    df["DATA_CRIACAO"] = pd.to_datetime(df["DATA_CRIACAO"])  # Converte para datetime
    datas_unicas = sorted(df["DATA_CRIACAO"].unique(), reverse=True)  # Ordena do mais recente ao mais antigo

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

def gerar_download(df, nome_arquivo):
    """Cria um link de download para um DataFrame"""
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer

# 🚀 Interface do Streamlit
st.title("📊 Comparação de Matrículas Diário")

df = obter_dados()

# Separa os registros de ontem e hoje corretamente
df_hoje, df_ontem, data_ontem, data_hoje = separar_dias(df)

st.write(f"📆 Comparando dados de **{data_ontem.strftime('%d/%m/%Y')}** com **{data_hoje.strftime('%d/%m/%Y')}**")

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
