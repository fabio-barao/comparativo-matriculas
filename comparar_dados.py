import sqlite3
import pandas as pd

DB_NAME = "matriculas.db"

def obter_dados():
    """Obtém os registros do banco e retorna um DataFrame"""
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM matriculas ORDER BY DATA_CRIACAO DESC LIMIT 660"  # Pega os 660 últimos registros
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

if __name__ == "__main__":
    print("🔄 Comparando dados entre ontem e hoje...")

    df = obter_dados()

    # Separar os registros de ontem e hoje
    df_hoje = df.iloc[:330]   # Assumindo que a atualização diária adiciona metade dos registros
    df_ontem = df.iloc[330:]  # Pegando os registros mais antigos

    adicionados, removidos, alterados = comparar_dados(df_hoje, df_ontem)

    print(f"📥 Registros adicionados: {len(adicionados)}")
    print(f"📤 Registros removidos: {len(removidos)}")
    print(f"✏️ Registros alterados: {len(alterados)}")

    print("\n🔎 Detalhes das mudanças:")
    print(f"Adicionados: {adicionados[:5]} ...")  # Mostra só os 5 primeiros para não poluir a tela
    print(f"Removidos: {removidos[:5]} ...")
    print(f"Alterados: {alterados[:5]} ...")
