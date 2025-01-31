import requests
import sqlite3
import json
from datetime import datetime

# 🌐 URL do JSON
URL = "https://leaoapis.unileao.edu.br/crm_integration/matriculas_novatos_veteranos?token=1b3d5fbb-678c-4f1b-bf69-c262943a5065&periodo_letivo=20251"

# 💂️ Diretório seguro para o banco de dados
DB_NAME = "matriculas.db"

# 🔍 Campos desejados do JSON
CAMPOS_DESEJADOS = [
    "RA", "ALUNO", "CURSO", "STATUSPERLET", "TURNO",
    "CODCURSO", "TIPOINGRESSO", "CPF", "DATA_MATRICULA",
    "TIPO_DE_MATRICULA", "PROCESSO_SELETIVO"
]

def baixar_dados():
    """Baixa os dados do JSON e retorna como lista de dicionários"""
    print("\ud83d\udd04 Baixando dados...")
    response = requests.get(URL)

    if response.status_code == 200:
        try:
            # Decodifica corretamente para evitar erro de BOM
            dados = json.loads(response.content.decode("utf-8-sig"))
            print(f"\u2705 Total de registros baixados: {len(dados)}")
            return [{chave: registro.get(chave, None) for chave in CAMPOS_DESEJADOS} for registro in dados]
        except json.JSONDecodeError as e:
            print(f"\u274c Erro ao decodificar JSON: {e}")
            return []
    else:
        print(f"\u274c Erro ao baixar JSON. Código de status: {response.status_code}")
        return []

def criar_tabela():
    """Cria a tabela `matriculas` caso não exista no banco de dados"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matriculas (
            RA TEXT,
            ALUNO TEXT,
            CURSO TEXT,
            STATUSPERLET TEXT,
            TURNO TEXT,
            CODCURSO TEXT,
            TIPOINGRESSO TEXT,
            CPF TEXT,
            DATA_MATRICULA TEXT,
            TIPO_DE_MATRICULA TEXT,
            PROCESSO_SELETIVO TEXT,
            DATA_CRIACAO TEXT,
            PRIMARY KEY (RA, DATA_CRIACAO)
        )
    """)
    conn.commit()
    conn.close()

def armazenar_dados(dados):
    """Armazena os dados no banco SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    registros_inseridos = 0
    for registro in dados:
        try:
            cursor.execute("""
                INSERT INTO matriculas (RA, ALUNO, CURSO, STATUSPERLET, TURNO, CODCURSO, 
                    TIPOINGRESSO, CPF, DATA_MATRICULA, TIPO_DE_MATRICULA, PROCESSO_SELETIVO, DATA_CRIACAO)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(registro.values()) + (data_atual,))
            registros_inseridos += 1
        except sqlite3.IntegrityError:
            pass  # Ignorar duplicatas

    conn.commit()
    conn.close()
    print(f"\u2705 {registros_inseridos} registros foram inseridos no banco!")

if __name__ == "__main__":
    print("\ud83d\ude80 Iniciando atualização do banco de dados...")
    
    # Criar tabela se não existir
    criar_tabela()

    # Baixar dados mais recentes
    dados = baixar_dados()

    if dados:
        # Armazenar no banco
        armazenar_dados(dados)
        print("\u2705 Dados armazenados com sucesso no banco SQLite!")
    else:
        print("\u26a0\ufe0f Nenhum dado foi baixado. Verifique a conexão com a API.")
