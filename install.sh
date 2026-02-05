#!/bin/bash
# =============================================================================
# Script di Installazione per DeepAiUG Streamlit LLM Interface
# =============================================================================
# Questo script installa le dipendenze nell'ordine corretto per evitare
# conflitti tra i pacchetti datapizza-ai
# =============================================================================

set -e  # Exit on error

echo "🧠 Installazione DeepAiUG Streamlit LLM Interface"
echo "=================================================="
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi colorati
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Verifica Python
echo "Verifica versione Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 non trovato! Installa Python 3.8 o superiore."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Python ${PYTHON_VERSION} trovato"
echo ""

# Verifica pip
echo "Verifica pip..."
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    print_error "pip non trovato! Installa pip."
    exit 1
fi

# Usa pip3 se disponibile, altrimenti pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

print_status "pip trovato"
echo ""

# Aggiorna pip
echo "Aggiornamento pip..."
$PIP_CMD install --upgrade pip
print_status "pip aggiornato"
echo ""

# Installa dipendenze base
echo "📦 Installazione dipendenze base..."
$PIP_CMD install streamlit python-dotenv
print_status "streamlit e python-dotenv installati"
echo ""

# Installa datapizza AI core (libreria)
echo "📦 Installazione datapizza AI (libreria)..."
$PIP_CMD install datapizza-ai
print_status "datapizza-ai installato"
echo ""

# Chiedi quali provider installare
echo "Quali provider cloud vuoi installare?"
echo "1) Tutti (OpenAI, Anthropic, Google)"
echo "2) Solo OpenAI"
echo "3) Solo Anthropic (Claude)"
echo "4) Solo Google (Gemini)"
echo "5) Nessuno (solo Ollama locale)"
read -p "Scelta [1-5]: " choice

case $choice in
    1)
        echo "📦 Installazione tutti i provider cloud..."
        $PIP_CMD install datapizza-ai-clients-openai
        print_status "OpenAI client installato"
        $PIP_CMD install datapizza-ai-clients-anthropic
        print_status "Anthropic client installato"
        $PIP_CMD install datapizza-ai-clients-google
        print_status "Google client installato"
        ;;
    2)
        echo "📦 Installazione OpenAI client..."
        $PIP_CMD install datapizza-ai-clients-openai
        print_status "OpenAI client installato"
        ;;
    3)
        echo "📦 Installazione Anthropic client..."
        $PIP_CMD install datapizza-ai-clients-anthropic
        print_status "Anthropic client installato"
        ;;
    4)
        echo "📦 Installazione Google client..."
        $PIP_CMD install datapizza-ai-clients-google
        print_status "Google client installato"
        ;;
    5)
        print_warning "Nessun provider cloud installato. Solo modalità Ollama disponibile."
        ;;
    *)
        print_error "Scelta non valida. Installazione annullata."
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Installazione completata con successo!${NC}"
echo "=================================================="
echo ""
echo "Per avviare l'applicazione:"
echo "  streamlit run 00_interfaccia_dinamica_datapizza_Streamlit.py"
echo ""
echo "Per configurare le API keys:"
echo "  - Crea un file .env nella directory del progetto"
echo "  - Oppure crea file secrets/{provider}_key.txt"
echo ""