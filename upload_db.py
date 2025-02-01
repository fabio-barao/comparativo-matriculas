import os
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

# 🔎 Verificar se o arquivo existe antes de fazer o upload
if not os.path.exists(DB_PATH):
    print(f"❌ ERRO: O arquivo {DB_PATH} não existe. Crie o banco de dados antes de fazer o upload.")
    exit(1)

# 📤 Criar o metadado do arquivo no Drive
file_metadata = {
    "name": FILE_NAME
}

# 📤 Fazer upload do arquivo para o Google Drive
media = MediaFileUpload(DB_PATH, mimetype="application/octet-stream")
file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

# 📌 Exibir o ID do arquivo no Google Drive
file_id = file.get("id")
print(f"✅ Upload concluído! ID do arquivo: {file_id}")
