import sqlite3

# Nome do banco de dados
DB_NAME = "matriculas.db"

# Criando a conexão com o banco de dados
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Criando a tabela (se não existir)
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

# Fechando a conexão
conn.commit()
conn.close()
