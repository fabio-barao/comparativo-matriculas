import requests
import sqlite3
import json

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
            # Decodifica corretamente para evitar o erro de BOM
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
            print(f"Registro com RA {registro['RA']} já existe. Ignorando.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Baixando dados...")
    dados = baixar_dados()
    
    if dados:
        print(f"Total de registros baixados: {len(dados)}")
        armazenar_dados(dados)
        print("Dados armazenados com sucesso no banco SQLite!")
    else:
        print("Nenhum dado baixado.")
