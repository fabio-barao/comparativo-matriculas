import requests
import sqlite3
import os
import json

# 🚀 Define diretório seguro para armazenar o banco de dados
DB_DIR = os.path.join(os.getcwd(), ".db")
DB_NAME = os.path.join(DB_DIR, "matriculas.db")

# Criar o diretório se não existir
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

print("Iniciando script...")

# 🔹 URL do JSON
URL = "https://leaoapis.unileao.edu.br/crm_integration/matriculas_novatos_veteranos?token=1b3d5fbb-678c-4f1b-bf69-c262943a5065&periodo_letivo=20251"

# 🔹 Campos que queremos salvar no banco
CAMPOS_DESEJADOS = [
    "RA", "ALUNO", "CURSO", "HABILITACAO", "STATUSPERLET", "TURNO",
    "CODCURSO", "TIPOINGRESSO", "CPF", "DATA_MATRICULA",
    "TIPO_DE_MATRICULA", "PROCESSO_SELETIVO"
]

def inicializar_banco():
    """Cria a tabela no banco caso ainda não exista"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matriculas (
            RA TEXT PRIMARY KEY,
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
            DATA_CRIACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def baixar_dados():
    """Baixa os dados do JSON e retorna uma lista de dicionários"""
    response = requests.get(URL)
    if response.status_code == 200:
        try:
            dados = json.loads(response.content.decode("utf-8-sig"))
            return [{chave: registro.get(chave, None) for chave in CAMPOS_DESEJADOS} for registro in dados]
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return []
    else:
        print(f"Erro ao baixar JSON: {response.status_code}")
        return []

def armazenar_dados(dados):
    """Armazena os dados no banco SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for registro in dados:
        try:
            cursor.execute("""
                INSERT INTO matriculas (RA, ALUNO, CURSO, HABILITACAO, STATUSPERLET, TURNO, CODCURSO, 
                    TIPOINGRESSO, CPF, DATA_MATRICULA, TIPO_DE_MATRICULA, PROCESSO_SELETIVO)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(registro.values()))
        except sqlite3.IntegrityError:
            pass  # Ignora registros duplicados

    conn.commit()
    conn.close()

# 🚀 Primeiro, garantimos que o banco está pronto
inicializar_banco()

print("Baixando dados...")
dados = baixar_dados()

if dados:
    print(f"Total de registros baixados: {len(dados)}")
    armazenar_dados(dados)
    print("✅ Dados armazenados com sucesso no banco SQLite!")
else:
    print("❌ Nenhum dado baixado.")
