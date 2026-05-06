#!/bin/bash
# ============================================================
#  installa_deepaiug_linux.sh
#  Installer automatico DeepAiUG per Linux
#  v1.11.2
# ============================================================
set -e

# --- VARIABILI GLOBALI ---
DEST="$HOME/DeepAiUG"
VENV="venv"
GITHUB_ZIP="https://github.com/EnzoGitHub27/datapizza-streamlit-interface/archive/refs/heads/main.zip"
LOG="$HOME/DeepAiUG_install_log.txt"
PYTHON_CMD=""
PKG_MANAGER=""

# --- COLORI ANSI ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# --- FUNZIONI ---
log() {
    local msg="$1"
    echo -e "$msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $(echo "$msg" | sed 's/\x1b\[[0-9;]*m//g')" >> "$LOG"
}

check_ok() {
    log "  ${GREEN}[OK]${NC} $1"
}

check_err() {
    log "  ${RED}[ERRORE]${NC} $1"
    log "  ${YELLOW}Soluzione:${NC} $2"
}

# --- INIZIALIZZAZIONE LOG ---
echo "" > "$LOG"
echo "============================================================" >> "$LOG"
echo " DeepAiUG Installer Linux - Log di installazione" >> "$LOG"
echo " Data: $(date)" >> "$LOG"
echo "============================================================" >> "$LOG"

echo ""
echo -e "${BOLD}============================================================${NC}"
echo -e "${BOLD}     DeepAiUG - Installazione automatica Linux${NC}"
echo -e "${BOLD}============================================================${NC}"
echo ""

# ============================================================
# STEP 1 - DISCLAIMER
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  DISCLAIMER - Leggere attentamente${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""
echo "  Questo script installera' automaticamente:"
echo ""
echo "    - Python 3.12        (linguaggio di programmazione)"
echo "    - Ollama             (motore AI locale)"
echo "    - DeepAiUG v1.11.2  (interfaccia chat AI)"
echo "    - Un modello AI      (1-5 GB, in base alla RAM)"
echo ""
echo "  Cartella di installazione: $DEST"
echo ""
echo "  NOTA: L'installazione richiede connessione Internet e"
echo "  puo' impiegare 10-30 minuti in base alla velocita' di rete."
echo ""
echo "  L'autore non si assume responsabilita' per eventuali"
echo "  problemi derivanti dall'uso di questo software."
echo "  Il software e' fornito \"cosi' com'e'\" senza garanzie."
echo ""
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""
read -p "  Vuoi procedere con l'installazione? (s/n): " ACCETTA
log "[DISCLAIMER] Risposta utente: $ACCETTA"

if [[ "$ACCETTA" != "s" && "$ACCETTA" != "S" ]]; then
    echo ""
    log "  Installazione annullata dall'utente."
    echo ""
    exit 0
fi
echo ""
check_ok "Installazione avviata."
echo ""

# ============================================================
# STEP 2 - RILEVAMENTO DISTRO E SISTEMA
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 2 - Rilevamento sistema${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

# --- Package Manager ---
if command -v apt &>/dev/null; then
    PKG_MANAGER="apt"
    log "  ${CYAN}Distro:${NC} Debian/Ubuntu/Mint (apt)"
elif command -v dnf &>/dev/null; then
    PKG_MANAGER="dnf"
    log "  ${CYAN}Distro:${NC} Fedora/RHEL (dnf)"
elif command -v pacman &>/dev/null; then
    PKG_MANAGER="pacman"
    log "  ${CYAN}Distro:${NC} Arch Linux (pacman)"
else
    PKG_MANAGER=""
    log "  ${YELLOW}[ATTENZIONE]${NC} Package manager non rilevato. Le dipendenze di sistema non verranno installate automaticamente."
fi

# --- RAM ---
RAM_GB=$(free -g 2>/dev/null | awk '/Mem:/{print $2}')
if [[ -z "$RAM_GB" || "$RAM_GB" == "0" ]]; then
    RAM_GB=$(free -m 2>/dev/null | awk '/Mem:/{printf "%d", $2/1024}')
fi
log "  ${CYAN}RAM:${NC} ${RAM_GB} GB"
echo "[SISTEMA] RAM: ${RAM_GB} GB" >> "$LOG"

# --- GPU ---
GPU_NAME="Non rilevata"
if command -v lspci &>/dev/null; then
    GPU_LINE=$(lspci 2>/dev/null | grep -i "vga\|3d\|display" | head -1)
    if [[ -n "$GPU_LINE" ]]; then
        GPU_NAME="$GPU_LINE"
    fi
fi
log "  ${CYAN}GPU:${NC} $GPU_NAME"
echo "[SISTEMA] GPU: $GPU_NAME" >> "$LOG"
echo ""

# ============================================================
# STEP 3 - VERIFICA/INSTALLA PYTHON
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 3 - Python${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

PYTHON_FOUND=0

# Prova python3
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 10 ]]; then
        PYTHON_CMD="python3"
        PYTHON_FOUND=1
        check_ok "Python $PY_VERSION trovato (python3)."
    else
        log "  ${YELLOW}[ATTENZIONE]${NC} Python $PY_VERSION trovato ma serve >= 3.10."
    fi
fi

# Prova python
if [[ $PYTHON_FOUND -eq 0 ]] && command -v python &>/dev/null; then
    PY_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 10 ]]; then
        PYTHON_CMD="python"
        PYTHON_FOUND=1
        check_ok "Python $PY_VERSION trovato (python)."
    fi
fi

# Installa se necessario
if [[ $PYTHON_FOUND -eq 0 ]]; then
    log "  Python >= 3.10 non trovato. Avvio installazione..."
    echo "[PYTHON] Non trovato, avvio installazione" >> "$LOG"

    if [[ "$PKG_MANAGER" == "apt" ]]; then
        sudo apt update >> "$LOG" 2>&1
        sudo apt install -y python3 python3-pip python3-venv >> "$LOG" 2>&1
    elif [[ "$PKG_MANAGER" == "dnf" ]]; then
        sudo dnf install -y python3 python3-pip >> "$LOG" 2>&1
    elif [[ "$PKG_MANAGER" == "pacman" ]]; then
        sudo pacman -S --noconfirm python python-pip >> "$LOG" 2>&1
    else
        check_err "Impossibile installare Python automaticamente." \
            "Installa Python 3.10+ manualmente dal sito https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_CMD="python3"
    check_ok "Python installato."
    echo "[PYTHON] Installazione completata" >> "$LOG"
fi

# Verifica python3-venv su Debian/Ubuntu
if [[ "$PKG_MANAGER" == "apt" ]]; then
    if ! $PYTHON_CMD -m venv --help &>/dev/null; then
        log "  Installazione python3-venv..."
        sudo apt install -y python3-venv >> "$LOG" 2>&1
        check_ok "python3-venv installato."
    fi
fi
echo ""

# ============================================================
# STEP 4 - VERIFICA/INSTALLA CURL E UNZIP
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 4 - Dipendenze di sistema (curl, unzip)${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

for DEP in curl unzip; do
    if command -v $DEP &>/dev/null; then
        check_ok "$DEP trovato."
    else
        log "  $DEP non trovato. Installazione..."
        if [[ "$PKG_MANAGER" == "apt" ]]; then
            sudo apt install -y $DEP >> "$LOG" 2>&1
        elif [[ "$PKG_MANAGER" == "dnf" ]]; then
            sudo dnf install -y $DEP >> "$LOG" 2>&1
        elif [[ "$PKG_MANAGER" == "pacman" ]]; then
            sudo pacman -S --noconfirm $DEP >> "$LOG" 2>&1
        else
            check_err "$DEP non trovato." "Installa $DEP manualmente."
            exit 1
        fi
        check_ok "$DEP installato."
    fi
done
echo ""

# ============================================================
# STEP 5 - VERIFICA/INSTALLA OLLAMA
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 5 - Ollama${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

if command -v ollama &>/dev/null; then
    check_ok "Ollama trovato nel PATH."
    echo "[OLLAMA] Trovato nel PATH" >> "$LOG"
else
    log "  Ollama non trovato. Avvio installazione..."
    echo "[OLLAMA] Non trovato, avvio installazione" >> "$LOG"
    curl -fsSL https://ollama.com/install.sh | sh >> "$LOG" 2>&1

    if command -v ollama &>/dev/null; then
        check_ok "Ollama installato."
        echo "[OLLAMA] Installazione completata" >> "$LOG"
    else
        check_err "Installazione Ollama fallita." \
            "Installa manualmente da https://ollama.com/download"
        echo "[OLLAMA] ERRORE installazione" >> "$LOG"
        # Non bloccare, continua
    fi
fi
echo ""

# ============================================================
# STEP 6 - DOWNLOAD DEEPAIUG
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 6 - Download DeepAiUG${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

mkdir -p "$DEST"
check_ok "Cartella creata: $DEST"
echo "[DOWNLOAD] Cartella: $DEST" >> "$LOG"

log "  Download repository da GitHub..."
echo "[DOWNLOAD] Avvio download ZIP" >> "$LOG"
curl -L "$GITHUB_ZIP" -o /tmp/deepaiug.zip --progress-bar

if [[ ! -f /tmp/deepaiug.zip ]]; then
    check_err "Download fallito." "Controlla la connessione Internet."
    exit 1
fi
check_ok "Download completato."

log "  Estrazione file..."
rm -rf /tmp/deepaiug_tmp
unzip -q /tmp/deepaiug.zip -d /tmp/deepaiug_tmp
cp -r /tmp/deepaiug_tmp/datapizza-streamlit-interface-main/. "$DEST/"
rm -rf /tmp/deepaiug.zip /tmp/deepaiug_tmp
check_ok "File DeepAiUG copiati in: $DEST"
echo "[DOWNLOAD] Estrazione e copia completate" >> "$LOG"
echo ""

# ============================================================
# STEP 7 - CREA VENV E DIPENDENZE
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 7 - Ambiente virtuale e dipendenze${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

cd "$DEST"

log "  Creazione ambiente virtuale (venv)..."
echo "[VENV] Creazione venv" >> "$LOG"
$PYTHON_CMD -m venv $VENV >> "$LOG" 2>&1
check_ok "Ambiente virtuale creato."

log "  Aggiornamento pip..."
echo "[PIP] Aggiornamento pip" >> "$LOG"
./$VENV/bin/python -m pip install --upgrade pip >> "$LOG" 2>&1
check_ok "pip aggiornato."

log "  Installazione datapizza-ai... attendere..."
echo "[PIP] Installazione datapizza-ai" >> "$LOG"
./$VENV/bin/pip install datapizza-ai >> "$LOG" 2>&1
check_ok "datapizza-ai installato."

log "  Installazione dipendenze da requirements.txt... attendere..."
log "  (potrebbe richiedere qualche minuto)"
echo "[PIP] Installazione requirements.txt" >> "$LOG"
./$VENV/bin/pip install -r requirements.txt >> "$LOG" 2>&1
check_ok "Librerie installate."
echo "[PIP] Tutte le dipendenze installate" >> "$LOG"
echo ""

# ============================================================
# STEP 8 - SUGGERIMENTO MODELLO
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 8 - Scelta modello AI${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

DEFAULT_MODEL="phi3:mini"

if [[ $RAM_GB -lt 8 ]]; then
    DEFAULT_MODEL="phi3:mini"
    echo "  RAM: ${RAM_GB} GB - Modelli consigliati:"
    echo ""
    echo "    [Default] phi3:mini     (~2.3 GB)"
    echo "              tinyllama      (~1.1 GB)"
    echo ""
elif [[ $RAM_GB -lt 16 ]]; then
    DEFAULT_MODEL="llama3.2:3b"
    echo "  RAM: ${RAM_GB} GB - Modelli consigliati:"
    echo ""
    echo "    [Default] llama3.2:3b   (~2.0 GB)"
    echo "              phi3           (~2.3 GB)"
    echo "              phi3:mini      (~2.3 GB)"
    echo ""
elif [[ $RAM_GB -lt 32 ]]; then
    DEFAULT_MODEL="mistral:7b"
    echo "  RAM: ${RAM_GB} GB - Modelli consigliati:"
    echo ""
    echo "    [Default] mistral:7b    (~4.1 GB)"
    echo "              llama3.2:3b    (~2.0 GB)"
    echo "              gemma2:9b      (~5.4 GB)"
    echo ""
else
    DEFAULT_MODEL="llama3.1:8b"
    echo "  RAM: ${RAM_GB} GB - Modelli consigliati:"
    echo ""
    echo "    [Default] llama3.1:8b   (~4.7 GB)"
    echo "              mistral:7b     (~4.1 GB)"
    echo "              gemma2:9b      (~5.4 GB)"
    echo ""
fi

echo "  Premi INVIO per usare il modello default: $DEFAULT_MODEL"
echo "  Oppure scrivi il nome di un altro modello."
echo ""
read -p "  Modello (INVIO = $DEFAULT_MODEL): " MODELLO
[[ -z "$MODELLO" ]] && MODELLO="$DEFAULT_MODEL"

echo ""
check_ok "Modello scelto: $MODELLO"
echo "[MODELLO] Scelto: $MODELLO" >> "$LOG"
echo ""

# ============================================================
# STEP 9 - DOWNLOAD MODELLO
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 9 - Download modello AI: $MODELLO${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

log "  Avvio Ollama in background..."
echo "[MODELLO] Avvio Ollama" >> "$LOG"

# Avvia ollama serve in background
ollama serve &>/dev/null &
OLLAMA_PID=$!
sleep 5

log "  Download modello $MODELLO in corso..."
log "  (il download puo' richiedere qualche minuto)"
echo ""
echo "[MODELLO] Avvio download: $MODELLO" >> "$LOG"

if ollama pull "$MODELLO" 2>> "$LOG"; then
    echo ""
    check_ok "Modello $MODELLO scaricato."
    echo "[MODELLO] Download completato: $MODELLO" >> "$LOG"
else
    echo ""
    log "  ${YELLOW}[ATTENZIONE]${NC} Download modello fallito o Ollama non raggiungibile."
    echo "[MODELLO] ERRORE download: $MODELLO" >> "$LOG"
    echo ""
    echo "  Puoi scaricarlo manualmente dopo l'installazione con:"
    echo "    ollama pull $MODELLO"
    echo ""
    echo "  L'installazione prosegue comunque..."
fi
echo ""

# ============================================================
# STEP 10 - CREA LAUNCHER E FILE .DESKTOP
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 10 - Creazione launcher${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

# --- Crea launcher avvia_deepaiug.sh ---
log "  Creazione launcher..."
echo "[LAUNCHER] Creazione avvia_deepaiug.sh" >> "$LOG"

cat > "$DEST/avvia_deepaiug.sh" << 'LAUNCHER_EOF'
#!/bin/bash
cd "$HOME/DeepAiUG"

# Avvia Ollama se non in esecuzione
if ! pgrep -x "ollama" > /dev/null; then
    echo "  Avvio Ollama..."
    ollama serve &>/dev/null &
    sleep 3
fi

echo "  Avvio DeepAiUG... il browser si apre in 20-30 secondi."
source venv/bin/activate
python -m streamlit run app.py
LAUNCHER_EOF

chmod +x "$DEST/avvia_deepaiug.sh"
check_ok "Launcher creato: $DEST/avvia_deepaiug.sh"

# --- Crea file .desktop ---
log "  Creazione collegamento nel menu applicazioni..."
echo "[SHORTCUT] Creazione .desktop" >> "$LOG"

DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/deepaiug.desktop" << DESKTOP_EOF
[Desktop Entry]
Name=DeepAiUG
Comment=AI locale privacy-first
Exec=bash $HOME/DeepAiUG/avvia_deepaiug.sh
Icon=$HOME/DeepAiUG/deepaiug-logo.png
Terminal=true
Type=Application
Categories=Utility;
DESKTOP_EOF

check_ok "Collegamento creato nel menu applicazioni."
echo "[SHORTCUT] .desktop creato" >> "$LOG"
echo ""

# ============================================================
# STEP 11 - RIEPILOGO FINALE
# ============================================================
echo "[FINE] Installazione completata" >> "$LOG"

echo ""
echo -e "${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}     INSTALLAZIONE COMPLETATA!${NC}"
echo -e "${BOLD}============================================================${NC}"
echo ""
echo -e "  Percorso installazione:  ${CYAN}$DEST${NC}"
echo -e "  Modello installato:      ${CYAN}$MODELLO${NC}"
echo ""
echo "  COME AVVIARE:"
echo "    bash $DEST/avvia_deepaiug.sh"
echo "    Oppure cerca 'DeepAiUG' nel menu applicazioni."
echo "    La prima volta attendi 20-30 secondi."
echo ""
echo "  PROBLEMI?"
echo "    Lancia: bash installer/check_deepaiug.sh"
echo ""
echo -e "  Log completo salvato in: ${CYAN}$LOG${NC}"
echo ""
echo -e "${BOLD}============================================================${NC}"
echo ""
