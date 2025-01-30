import sqlite3
import pandas as pd

DB_NAME = "matriculas.db"

def obter_dados():
    """Obtém os registros do banco e retorna um DataFrame"""
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM matriculas ORDER BY DATA_CRIACAO DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def separar_dias(df):
    """Separa os registros do dia mais recente e do dia anterior"""
    df["DATA_CRIACAO"] = pd.to_datetime(df["DATA_CRIACAO"])  # Converte para datetime
    data_hoje = df["DATA_CRIACAO"].max()  # Última data disponível
    data_ontem = df[df["DATA_CRIACAO"] < data_hoje]["DATA_CRIACAO"].max()  # Segunda data mais recente

    df_hoje = df[df["DATA_CRIACAO"] == data_hoje]
    df_ontem = df[df["DATA_CRIACAO"] == data_ontem]

    return df_hoje, df_ontem

def comparar_dados(df_hoje, df_ontem):
    """Compara os dados de hoje e ontem, ignorando a DATA_CRIACAO"""

    # Remover a coluna DATA_CRIACAO antes da comparação
    df_hoje_filtrado = df_hoje.drop(columns=["DATA_CRIACAO"], errors="ignore")
    df_ontem_filtrado = df_ontem.drop(columns=["DATA_CRIACAO"], errors="ignore")

    # Transformar os DataFrames em dicionários baseados no RA
    dict_hoje = df_hoje_filtrado.set_index("RA").to_dict("index")
    dict_ontem = df_ontem_filtrado.set_index("RA").to_dict("index")

    # Registros adicionados (existem hoje, mas não existiam ontem)
    adicionados = [ra for ra in dict_hoje.keys() if ra not in dict_ontem]

    # Registros removidos (existiam ontem, mas não existem hoje)
    removidos = [ra for ra in dict_ontem.keys() if ra not in dict_hoje]

    # Registros alterados (existem nos dois dias, mas com diferenças)
    alterados = []
    for ra in dict_hoje.keys() & dict_ontem.keys():
        if dict_hoje[ra] != dict_ontem[ra]:  # Compara os valores sem a DATA_CRIACAO
            alterados.append(ra)

    return adicionados, removidos, alterados

if __name__ == "__main__":
    print("🔄 Comparando dados entre ontem e hoje...")

    df = obter_dados()
    df_hoje, df_ontem = separar_dias(df)

    adicionados, removidos, alterados = comparar_dados(df_hoje, df_ontem)

    print(f"📥 Registros adicionados: {len(adicionados)}")
    print(f"📤 Registros removidos: {len(removidos)}")
    print(f"✏️ Registros alterados: {len(alterados)}")

    print("\n🔎 Detalhes das mudanças:")
    print(f"Adicionados: {adicionados[:5]} ...")  # Mostra só os 5 primeiros para não poluir a tela
    print(f"Removidos: {removidos[:5]} ...")
    print(f"Alterados: {alterados[:5]} ...")
