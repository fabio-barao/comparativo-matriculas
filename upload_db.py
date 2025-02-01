import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from cryptography.fernet import Fernet

# 📌 Caminho dos arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(CURRENT_DIR, "credentials.json")
CHAVE_FILE = os.path.join(CURRENT_DIR, "chave.key")
DB_DIR = os.path.join(CURRENT_DIR, ".db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")
ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")

# 🔐 Autenticação com a conta de serviço
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, 
    scopes=["https://www.googleapis.com/auth/drive"]
)

# 📡 Conectar à API do Google Drive
service = build("drive", "v3", credentials=credentials)

# 📌 Nome do arquivo no Google Drive
FILE_NAME = "matriculas_encrypted.db"

# 📌 Pasta no Google Drive (deixe vazio para salvar na raiz)
FOLDER_ID = ""

# 🔍 Função para encontrar o arquivo no Drive
def encontrar_arquivo(nome_arquivo):
    query = f"name = '{nome_arquivo}'"
    if FOLDER_ID:
        query += f" and '{FOLDER_ID}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = results.get("files", [])
    return arquivos[0]["id"] if arquivos else None

# 🔐 Função para criptografar o banco de dados
def criptografar_banco():
    with open(CHAVE_FILE, "rb") as chave_file:
        chave = chave_file.read()
    
    cipher = Fernet(chave)

    with open(DB_PATH, "rb") as banco:
        dados_banco = banco.read()
    
    dados_encriptados = cipher.encrypt(dados_banco)

    with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
        banco_encriptado.write(dados_encriptados)
    
    print("🔒 Banco de dados criptografado com sucesso!")

# 🔍 Verificar se o arquivo existe no Drive e renomear a versão antiga
arquivo_atual_id = encontrar_arquivo(FILE_NAME)

if arquivo_atual_id:
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    novo_nome = f"matriculas_encrypted_{data_atual}.db"
    
    service.files().update(
        fileId=arquivo_atual_id,
        body={"name": novo_nome}
    ).execute()
    
    print(f"🔄 Versão antiga renomeada para {novo_nome}")

# 🔐 Criptografar o banco antes do upload
criptografar_banco()

# 📤 Criar novo upload do banco atualizado
file_metadata = {"name": FILE_NAME}
if FOLDER_ID:
    file_metadata["parents"] = [FOLDER_ID]

media = MediaFileUpload(ENCRYPTED_DB_PATH, mimetype="application/octet-stream")

file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

print(f"✅ Upload concluído! Banco criptografado salvo com ID: {file.get('id')}")
