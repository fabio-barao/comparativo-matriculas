import subprocess
import sys

print("🚀 Instalando dependências do requirements.txt...")

try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("✅ Instalação concluída com sucesso!")
except subprocess.CalledProcessError as e:
    print(f"❌ Erro ao instalar dependências: {e}")