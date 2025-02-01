import os
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# 📌 Caminho do arquivo de credenciais
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(CURRENT_DIR, "credentials.json")

# 📌 Substitua pelo ID do arquivo do banco no Google Drive (pegue o ID no link do arquivo)
FILE_ID = "1l9SbpjKF2HgmfgFmZJnNsYPJwHAZn3yS"

# 📂 Diretório e caminho onde o banco será salvo
DB_DIR = os.path.join(CURRENT_DIR, ".db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")

# 📂 Criar pasta `.db/` se não existir
os.makedirs(DB_DIR, exist_ok=True)

# 🔐 Autenticação com a conta de serviço
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, 
    scopes=["https://www.googleapis.com/auth/drive"]
)

# 📡 Conectar à API do Google Drive
service = build("drive", "v3", credentials=credentials)

# ⬇️ Baixar o banco de dados do Google Drive
print("Baixando banco de dados...")
request = service.files().get_media(fileId=FILE_ID)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False

while not done:
    status, done = downloader.next_chunk()
    print(f"Progresso do download: {int(status.progress() * 100)}%")

# 📂 Salvar o arquivo baixado
with open(DB_PATH, "wb") as f:
    f.write(fh.getvalue())

print(f"✅ Banco de dados baixado com sucesso: {DB_PATH}")