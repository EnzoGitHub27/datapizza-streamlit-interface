import os

from datapizza.clients import ClientFactory
from datapizza.clients.factory import Provider
from dotenv import load_dotenv

load_dotenv()

# Create any provider with the same interface
openai_= ClientFactory.create(
    provider=Provider.OPENAI,
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo",
    temperature=0.7 # Optional temperature parameter
)

anthropic = ClientFactory.create(
    provider=Provider.ANTHROPIC,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-sonnet-4-20250514",
    temperature=0.7 # Optional temperature parameter
)

gemini_ = ClientFactory.create(
    provider=Provider.GOOGLE,
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-pro",
    temperature=0.7 # Optional temperature parameter
)

ollama_ = ClientFactory.create(
    provider=Provider.OLLAMA,
    base_url="http://localhost:11434/v1",  # Notare che il /v1 è necessario
    api_key="ollama",
    model="llama3.2",
    temperature=0.7 # Optional temperature parameter
)


prompt = "Spiegami in una frase perché Linux è il top."

openai_response = openai_.invoke(prompt)
print(f"OpenaAI: {openai_response.text}")

anthropic_response = anthropic_.invoke(prompt)
print(f"Anthropic: {anthropic_response.text}")

google_response = gemini_.invoke(prompt)
print(f"Gemini: {google_response.text}")

ollama_response = ollama_.invoke(prompt)
print(f"Ollama: {ollama_response.text}")
# Now you can use the same interface to interact with different providers
