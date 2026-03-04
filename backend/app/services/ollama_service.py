import requests
import os

OLLAMA_ULR = os.getenv(
    "OLLAMA_URL",
    "http://ollama:11434/api/generate"
)

def ask_model(prompt: str):
    response = requests.post(
        OLLAMA_ULR,
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        },
    )

    response.raise_for_status()
    return response.json()["response"]