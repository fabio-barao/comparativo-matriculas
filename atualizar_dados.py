import requests
import sqlite3
import json
from datetime import datetime, timezone
import os

# 🌐 URL do JSON
URL = "https://leaoapis.unileao.edu.br/crm_integration/matriculas_novatos_veteranos?token=1b3d5fbb-678c-4f1b-bf69-c262943a5065&periodo_letivo=20251"

# 📂 Diretório seguro para o banco de dados
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".db")  # Criar diretório oculto
os.makedirs(DB_DIR, exist_ok=True)  # Garante que o diretório existe

# 📂 Caminho do banco de dados
DB_NAME = os.path.join(DB_DIR, "matriculas.db")

# 🔎 Campos desejados do JSON
CAMPOS_DESEJADOS = [
    "RA", "ALUNO", "CURSO", "STATUSPERLET", "TURNO",
    "CODCURSO", "TIPOINGRESSO", "CPF", "DATA_MATRICULA",
    "TIPO_DE_MATRICULA", "PROCESSO_SELETIVO"
]

def baixar_dados():
    """Baixa os dados do JSON e retorna como lista de dicionários"""
    print("📥 Baixando dados...")
    response = requests.get(URL)

    if response.status_code == 200:
        try:
            # Decodifica corretamente para evitar erro de BOM
            dados = json.loads(response.content.decode("utf-8-sig"))
            print(f"✅ Total de registros baixados: {len(dados)}")
            return [{chave: registro.get(chave, None) for chave in CAMPOS_DESEJADOS} for registro in dados]
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            return []
    else:
        print(f"❌ Erro ao baixar JSON. Código de status: {response.status_code}")
        return []

def criar_tabela():
    """Cria a tabela `matriculas` caso não exista no banco de dados"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matriculas (
            RA TEXT NOT NULL,
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
            DATA_CRIACAO TEXT NOT NULL,
            PRIMARY KEY (RA, DATA_CRIACAO)
        )
    """)
    conn.commit()
    conn.close()

def armazenar_dados(dados, data_atual):
    """Armazena os dados no banco SQLite"""
    conn = sqlite3.connect(DB_NAME)  # Conectar ao banco
    cursor = conn.cursor()

    print(f"🕒 Data calculada para inserção: {data_atual}")

    inseridos = 0  # Contador para saber quantos registros foram inseridos

    for registro in dados:
        try:
            cursor.execute("""
                INSERT INTO matriculas (RA, ALUNO, CURSO, STATUSPERLET, TURNO, CODCURSO, 
                    TIPOINGRESSO, CPF, DATA_MATRICULA, TIPO_DE_MATRICULA, PROCESSO_SELETIVO, DATA_CRIACAO)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(registro.values()) + (data_atual,))
            inseridos += 1

        except sqlite3.IntegrityError as e:
            print(f"⚠️ Erro ao inserir registro {registro['RA']}: {e}")

    conn.commit()  # 🚨 Agora garantimos que os dados são realmente gravados!
    conn.close()   # Fechamos a conexão apenas depois de salvar os dados no banco

    print(f"✅ {inseridos} novos registros foram inseridos no banco!")

if __name__ == "__main__":
    print("🔄 Iniciando atualização do banco de dados...")

    # 🕒 Gerar a data correta para os registros
    data_atual = datetime.now(timezone.utc).date().strftime("%Y-%m-%d") + " 08:00:00"

    # 🛠 Criar tabela se não existir
    criar_tabela()

    # 📥 Baixar dados mais recentes
    dados = baixar_dados()

    if dados:
        # 💾 Armazenar no banco com a data correta
        armazenar_dados(dados, data_atual)
        print("✅ Dados armazenados com sucesso no banco SQLite!")
    else:
        print("❌ Nenhum dado foi baixado. Verifique a conexão com a API.")
