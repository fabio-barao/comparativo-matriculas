import os
from cryptography.fernet import Fernet

# Gerar uma chave segura (execute isso apenas UMA VEZ)
def gerar_chave():
    chave = Fernet.generate_key()
    with open("chave.key", "wb") as chave_file:
        chave_file.write(chave)
    print("✅ Chave de criptografia gerada com sucesso!")

# Se a chave ainda não existir, gerar uma
if not os.path.exists("chave.key"):
    gerar_chave()
