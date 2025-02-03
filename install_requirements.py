import os
import subprocess
import sys

def instalar_dependencias():
    print("📦 Instalando dependências do requirements.txt...")

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")

if __name__ == "__main__":
    instalar_dependencias()
