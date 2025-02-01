import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 📌 Caminho do arquivo de credenciais
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(CURRENT_DIR, "credentials.json")

# 📂 Diretório e caminho do banco de dados
DB_DIR = os.path.join(CURRENT_DIR, ".db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")

# 🔐 Autenticação com a conta de serviço
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, 
    scopes=["https://www.googleapis.com/auth/drive"]
)

# 📡 Conectar à API do Google Drive
service = build("drive", "v3", credentials=credentials)

# 📌 Nome do arquivo no Google Drive
FILE_NAME = "matriculas.db"

# 📌 Pasta onde o banco será salvo (deixe vazio para salvar na raiz do Google Drive)
FOLDER_ID = ""  # Se quiser salvar dentro de uma pasta, coloque o ID da pasta aqui.

# 🔍 Função para encontrar o arquivo no Google Drive
def encontrar_arquivo(nome_arquivo):
    query = f"name = '{nome_arquivo}'"
    if FOLDER_ID:
        query += f" and '{FOLDER_ID}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = results.get("files", [])
    return arquivos[0]["id"] if arquivos else None

# 🔍 Verificar se o arquivo existe no Drive
arquivo_atual_id = encontrar_arquivo(FILE_NAME)

# 🔄 Se o banco já existe, renomeia para manter histórico
if arquivo_atual_id:
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    novo_nome = f"matriculas_{data_atual}.db"
    
    service.files().update(
        fileId=arquivo_atual_id,
        body={"name": novo_nome}
    ).execute()
    
    print(f"🔄 Banco de dados renomeado para {novo_nome} para manter histórico.")

# 📤 Criar novo upload do banco atualizado
file_metadata = {"name": FILE_NAME}
if FOLDER_ID:
    file_metadata["parents"] = [FOLDER_ID]

media = MediaFileUpload(DB_PATH, mimetype="application/octet-stream")

file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

print(f"✅ Upload concluído! Novo banco de dados salvo com ID: {file.get('id')}")
