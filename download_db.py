import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cryptography.fernet import Fernet

# 📌 Caminho dos arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(CURRENT_DIR, "credentials.json")
CHAVE_FILE = os.path.join(CURRENT_DIR, "chave.key")
DB_DIR = os.path.join(CURRENT_DIR, ".db")
ENCRYPTED_DB_PATH = os.path.join(DB_DIR, "matriculas_encrypted.db")
DB_PATH = os.path.join(DB_DIR, "matriculas.db")

# 🔐 Autenticação com a conta de serviço
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, 
    scopes=["https://www.googleapis.com/auth/drive"]
)

# 📡 Conectar à API do Google Drive
service = build("drive", "v3", credentials=credentials)

# 📌 Nome do arquivo criptografado no Google Drive
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

# 🔓 Função para descriptografar o banco de dados
def descriptografar_banco():
    with open(CHAVE_FILE, "rb") as chave_file:
        chave = chave_file.read()
    
    cipher = Fernet(chave)

    with open(ENCRYPTED_DB_PATH, "rb") as banco_encriptado:
        dados_encriptados = banco_encriptado.read()
    
    dados_descriptografados = cipher.decrypt(dados_encriptados)

    with open(DB_PATH, "wb") as banco:
        banco.write(dados_descriptografados)
    
    print("🔓 Banco de dados descriptografado com sucesso!")

# 🔽 Baixar o banco de dados do Google Drive
arquivo_id = encontrar_arquivo(FILE_NAME)

if arquivo_id:
    request = service.files().get_media(fileId=arquivo_id)
    
    # 🔽 Corrigindo o erro: agora o download acontece corretamente
    with open(ENCRYPTED_DB_PATH, "wb") as banco_encriptado:
        banco_encriptado.write(request.execute())
    
    print("✅ Banco criptografado baixado com sucesso!")

    # 🔓 Descriptografar o banco após o download
    descriptografar_banco()

else:
    print("❌ ERRO: O banco de dados criptografado não foi encontrado no Google Drive.")
