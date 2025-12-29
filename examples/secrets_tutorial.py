import os
from dotenv import load_dotenv
from datapizza.clients.openai import OpenAIClient

# Carica .env (se presente)
load_dotenv()

# Prima prova a prendere la chiave dalla variabile d'ambiente
api_key = os.getenv("OPENAI_API_KEY")

# Se non è impostata, cerca il file secrets/openai_key.txt relativo a questo script
if not api_key:
    base_dir = os.path.dirname(os.path.abspath(__file__))  # cartella dello script
    key_path = os.path.join(base_dir, "secrets", "openai_key.txt")
    try:
        with open(key_path, "r") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(
            f"OPENAI_API_KEY non impostata e file non trovato: {key_path}. "
            "Crea secrets/openai_key.txt o imposta OPENAI_API_KEY in .env."
        )

# Controllo finale (chiave non vuota)
if not api_key:
    raise RuntimeError("OPENAI_API_KEY è vuota. Controlla il file o la variabile d'ambiente.")

# Crea il client e fai la richiesta
client = OpenAIClient(api_key=api_key)
result = client.invoke("Ciao come stai?")
print(result.text)
