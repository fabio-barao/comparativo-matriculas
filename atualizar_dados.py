import requests
import sqlite3
import json
import datetime

print("Iniciando script...")

# URL do JSON
URL = "https://leaoapis.unileao.edu.br/crm_integration/matriculas_novatos_veteranos?token=1b3d5fbb-678c-4f1b-bf69-c262943a5065&periodo_letivo=20251"

# Nome do banco de dados
DB_NAME = "matriculas.db"

# Campos desejados no JSON
CAMPOS_DESEJADOS = [
    "RA", "ALUNO", "CURSO", "HABILITACAO", "STATUSPERLET", "TURNO",
    "CODCURSO", "TIPOINGRESSO", "CPF", "DATA_MATRICULA",
    "TIPO_DE_MATRICULA", "PROCESSO_SELETIVO"
]

def baixar_dados():
    """Baixa os dados do JSON e retorna como lista de dicionários"""
    response = requests.get(URL)
    if response.status_code == 200:
        try:
            # Decodifica corretamente para evitar erro de BOM (Byte Order Mark)
            dados = json.loads(response.content.decode("utf-8-sig"))

            # Filtra os campos desejados e adiciona a DATA_CRIACAO
            data_hoje = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return [{**{chave: registro.get(chave, None) for chave in CAMPOS_DESEJADOS}, "DATA_CRIACAO": data_hoje} for registro in dados]

        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            return []
    else:
        print(f"❌ Erro ao baixar JSON: {response.status_code}")
        return []

def armazenar_dados(dados):
    """Cria a tabela se não existir e armazena os dados no banco SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ✅ Criar a tabela antes de inserir os dados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matriculas (
            RA TEXT,
            ALUNO TEXT,
            CURSO TEXT,
            HABILITACAO TEXT,
            STATUSPERLET TEXT,
            TURNO TEXT,
            CODCURSO TEXT,
            TIPOINGRESSO TEXT,
            CPF TEXT,
            DATA_MATRICULA TEXT,
            TIPO_DE_MATRICULA TEXT,
            PROCESSO_SELETIVO TEXT,
            DATA_CRIACAO TEXT,
            PRIMARY KEY (RA, DATA_CRIACAO) -- Permite múltiplos registros do mesmo RA em dias diferentes
        )
    """)

    for registro in dados:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO matriculas (RA, ALUNO, CURSO, HABILITACAO, STATUSPERLET, TURNO, CODCURSO, 
                                                  TIPOINGRESSO, CPF, DATA_MATRICULA, TIPO_DE_MATRICULA, PROCESSO_SELETIVO, DATA_CRIACAO)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(registro.values()))
        except sqlite3.IntegrityError:
            print(f"⚠️ Registro com RA {registro['RA']} já existe para esta data. Ignorando.")

    conn.commit()
    conn.close()
    print("✅ Dados armazenados com sucesso no banco SQLite!")

if __name__ == "__main__":
    print("📥 Baixando dados...")
    dados = baixar_dados()
    
    if dados:
        print(f"✅ Total de registros baixados: {len(dados)}")
        armazenar_dados(dados)
        print("✅ Dados armazenados com sucesso!")
    else:
        print("❌ Nenhum dado baixado.")
