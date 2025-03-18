import os
import requests

# Carrega a chave do ambiente (requer python-dotenv)
from dotenv import load_dotenv
load_dotenv()

HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
FLASK_URL = "http://localhost:5000/gerar-imagem"

try:
    # Testa a geração de imagem via endpoint Flask
    response = requests.post(
        FLASK_URL,
        json={
            "prompt": "Um gato fofo com óculos lendo um livro",
            "model": "stable-diffusion"
        },
        headers={
            "Authorization": f"Bearer {HUGGING_FACE_TOKEN}"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("Imagem gerada com sucesso!")
        print("Formato:", data.get('imagem_base64')[:30] + "...")
        print("Timestamp:", data.get('timestamp'))
    else:
        print(f"Erro {response.status_code}:")
        print(response.json())

except Exception as e:
    print("Erro na requisição:")
    print(str(e))