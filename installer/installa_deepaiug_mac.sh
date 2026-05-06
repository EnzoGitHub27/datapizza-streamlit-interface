#!/bin/bash
# ============================================================
#  installa_deepaiug_mac.sh
#  Installer automatico DeepAiUG per macOS
#  v1.11.2
# ============================================================
set -e

# --- VARIABILI GLOBALI ---
DEST="$HOME/DeepAiUG"
VENV="venv"
GITHUB_ZIP="https://github.com/EnzoGitHub27/datapizza-streamlit-interface/archive/refs/heads/main.zip"
LOG="$HOME/DeepAiUG_install_log.txt"
PYTHON_CMD=""
HAS_BREW=0

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
echo " DeepAiUG Installer macOS - Log di installazione" >> "$LOG"
echo " Data: $(date)" >> "$LOG"
echo "============================================================" >> "$LOG"

echo ""
echo -e "${BOLD}============================================================${NC}"
echo -e "${BOLD}     DeepAiUG - Installazione automatica macOS${NC}"
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
# STEP 2 - CHECK SISTEMA
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 2 - Controllo sistema${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

# --- macOS version ---
MACOS_VERSION=$(sw_vers -productVersion 2>/dev/null || echo "Non rilevata")
log "  ${CYAN}macOS:${NC} $MACOS_VERSION"
echo "[SISTEMA] macOS: $MACOS_VERSION" >> "$LOG"

# --- RAM ---
RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
RAM_GB=$((RAM_BYTES / 1073741824))
log "  ${CYAN}RAM:${NC} ${RAM_GB} GB"
echo "[SISTEMA] RAM: ${RAM_GB} GB" >> "$LOG"

# --- GPU/Chip ---
GPU_NAME="Non rilevata"
CHIP_INFO=$(system_profiler SPHardwareDataType 2>/dev/null | grep "Chip:" | awk -F': ' '{print $2}')
if [[ -n "$CHIP_INFO" ]]; then
    GPU_NAME="$CHIP_INFO"
else
    GPU_LINE=$(system_profiler SPDisplaysDataType 2>/dev/null | grep "Chipset Model:" | awk -F': ' '{print $2}' | head -1)
    if [[ -n "$GPU_LINE" ]]; then
        GPU_NAME="$GPU_LINE"
    fi
fi
log "  ${CYAN}GPU/Chip:${NC} $GPU_NAME"
echo "[SISTEMA] GPU: $GPU_NAME" >> "$LOG"
echo ""

# ============================================================
# STEP 3 - VERIFICA XCODE COMMAND LINE TOOLS
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 3 - Xcode Command Line Tools${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

if xcode-select -p &>/dev/null; then
    check_ok "Xcode Command Line Tools trovati."
else
    log "  Xcode Command Line Tools non trovati. Avvio installazione..."
    log "  ${YELLOW}Si aprira' una finestra di installazione. Segui le istruzioni.${NC}"
    xcode-select --install 2>/dev/null || true
    echo ""
    read -p "  Premi INVIO quando l'installazione Xcode e' completata... "
    if xcode-select -p &>/dev/null; then
        check_ok "Xcode Command Line Tools installati."
    else
        check_err "Xcode Command Line Tools non installati." \
            "Esegui manualmente: xcode-select --install"
    fi
fi
echo ""

# ============================================================
# STEP 4 - VERIFICA/INSTALLA HOMEBREW
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 4 - Homebrew (opzionale)${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

if command -v brew &>/dev/null; then
    HAS_BREW=1
    check_ok "Homebrew trovato."
    echo "[BREW] Trovato" >> "$LOG"
else
    echo "  Homebrew non trovato."
    echo "  Homebrew semplifica l'installazione di Python e Ollama."
    echo ""
    read -p "  Vuoi installare Homebrew? (s/n): " INSTALL_BREW

    if [[ "$INSTALL_BREW" == "s" || "$INSTALL_BREW" == "S" ]]; then
        log "  Installazione Homebrew in corso..."
        echo "[BREW] Avvio installazione" >> "$LOG"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Aggiungi brew al PATH per la sessione corrente
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi

        if command -v brew &>/dev/null; then
            HAS_BREW=1
            check_ok "Homebrew installato."
            echo "[BREW] Installazione completata" >> "$LOG"
        else
            log "  ${YELLOW}[ATTENZIONE]${NC} Homebrew non disponibile nel PATH. Si prosegue senza."
        fi
    else
        log "  Installazione senza Homebrew."
        echo "[BREW] Utente ha scelto di non installare" >> "$LOG"
    fi
fi
echo ""

# ============================================================
# STEP 5 - VERIFICA/INSTALLA PYTHON
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 5 - Python${NC}"
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
        echo "[PYTHON] Trovato: $PY_VERSION" >> "$LOG"
    else
        log "  ${YELLOW}[ATTENZIONE]${NC} Python $PY_VERSION trovato ma serve >= 3.10."
    fi
fi

# Installa se necessario
if [[ $PYTHON_FOUND -eq 0 ]]; then
    log "  Python >= 3.10 non trovato. Avvio installazione..."
    echo "[PYTHON] Non trovato, avvio installazione" >> "$LOG"

    if [[ $HAS_BREW -eq 1 ]]; then
        log "  Installazione Python 3.12 via Homebrew..."
        brew install python@3.12 >> "$LOG" 2>&1
        PYTHON_CMD="python3"
        check_ok "Python 3.12 installato via Homebrew."
    else
        PYTHON_PKG_URL="https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg"
        log "  Download installer Python da python.org..."
        curl -L "$PYTHON_PKG_URL" -o /tmp/python_installer.pkg --progress-bar

        echo ""
        log "  ${YELLOW}Apertura installer Python.${NC}"
        log "  ${YELLOW}Segui la procedura di installazione nella finestra che si apre.${NC}"
        open -W /tmp/python_installer.pkg
        echo ""
        read -p "  Premi INVIO quando l'installazione Python e' completata... "
        rm -f /tmp/python_installer.pkg

        PYTHON_CMD="python3"
        check_ok "Python installato."
    fi
    echo "[PYTHON] Installazione completata" >> "$LOG"
fi
echo ""

# ============================================================
# STEP 6 - VERIFICA/INSTALLA OLLAMA
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 6 - Ollama${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

if command -v ollama &>/dev/null; then
    check_ok "Ollama trovato nel PATH."
    echo "[OLLAMA] Trovato nel PATH" >> "$LOG"
else
    log "  Ollama non trovato. Avvio installazione..."
    echo "[OLLAMA] Non trovato, avvio installazione" >> "$LOG"

    OLLAMA_INSTALLED=0

    if [[ $HAS_BREW -eq 1 ]]; then
        log "  Installazione Ollama via Homebrew..."
        if brew install ollama >> "$LOG" 2>&1; then
            OLLAMA_INSTALLED=1
            check_ok "Ollama installato via Homebrew."
        fi
    fi

    if [[ $OLLAMA_INSTALLED -eq 0 ]]; then
        log "  Installazione Ollama via script ufficiale..."
        if curl -fsSL https://ollama.com/install.sh | sh >> "$LOG" 2>&1; then
            OLLAMA_INSTALLED=1
            check_ok "Ollama installato."
        fi
    fi

    if [[ $OLLAMA_INSTALLED -eq 0 ]]; then
        OLLAMA_ZIP_URL="https://ollama.com/download/Ollama-darwin.zip"
        log "  Download Ollama da $OLLAMA_ZIP_URL..."
        curl -L "$OLLAMA_ZIP_URL" -o /tmp/Ollama-darwin.zip --progress-bar
        unzip -q /tmp/Ollama-darwin.zip -d /tmp/Ollama_tmp
        if [[ -d /tmp/Ollama_tmp/Ollama.app ]]; then
            cp -r /tmp/Ollama_tmp/Ollama.app /Applications/
            check_ok "Ollama copiato in /Applications/."
        else
            check_err "Installazione Ollama fallita." \
                "Scarica manualmente da https://ollama.com/download"
        fi
        rm -rf /tmp/Ollama-darwin.zip /tmp/Ollama_tmp
    fi

    echo "[OLLAMA] Installazione completata" >> "$LOG"
fi
echo ""

# ============================================================
# STEP 7 - DOWNLOAD DEEPAIUG
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 7 - Download DeepAiUG${NC}"
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
# STEP 8 - CREA VENV E DIPENDENZE
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 8 - Ambiente virtuale e dipendenze${NC}"
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
# STEP 9 - SUGGERIMENTO MODELLO
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 9 - Scelta modello AI${NC}"
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
# STEP 10 - DOWNLOAD MODELLO
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 10 - Download modello AI: $MODELLO${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

log "  Avvio Ollama in background..."
echo "[MODELLO] Avvio Ollama" >> "$LOG"

# Avvia ollama serve in background
if command -v ollama &>/dev/null; then
    ollama serve &>/dev/null &
    OLLAMA_PID=$!
elif [[ -d /Applications/Ollama.app ]]; then
    open -a Ollama
fi
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
# STEP 11 - CREA LAUNCHER .COMMAND
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 11 - Creazione launcher${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

log "  Creazione launcher..."
echo "[LAUNCHER] Creazione DeepAiUG.command" >> "$LOG"

cat > "$DEST/DeepAiUG.command" << 'LAUNCHER_EOF'
#!/bin/bash
cd "$HOME/DeepAiUG"

# Avvia Ollama se non in esecuzione
if ! pgrep -x "ollama" > /dev/null; then
    echo "  Avvio Ollama..."
    if command -v ollama &>/dev/null; then
        ollama serve &>/dev/null &
    elif [[ -d /Applications/Ollama.app ]]; then
        open -a Ollama
    fi
    sleep 3
fi

echo "  Avvio DeepAiUG... il browser si apre in 20-30 secondi."
source venv/bin/activate
python -m streamlit run app.py
LAUNCHER_EOF

chmod +x "$DEST/DeepAiUG.command"
check_ok "Launcher creato: $DEST/DeepAiUG.command"
echo "[LAUNCHER] Launcher creato" >> "$LOG"

# --- Crea wrapper DeepAiUG.app con icona personalizzata (best-effort) ---
APP_BUNDLE="$DEST/DeepAiUG.app"
LOGO_PNG="$DEST/deepaiug-logo.png"

if [[ -f "$LOGO_PNG" ]] && command -v sips &>/dev/null && command -v iconutil &>/dev/null; then
    log "  Creazione DeepAiUG.app con icona personalizzata..."
    echo "[LAUNCHER] Creazione .app bundle" >> "$LOG"

    rm -rf "$APP_BUNDLE"
    mkdir -p "$APP_BUNDLE/Contents/MacOS" "$APP_BUNDLE/Contents/Resources"

    ICONSET_TMP="$(mktemp -d)/DeepAiUG.iconset"
    mkdir -p "$ICONSET_TMP"
    for s in 16 32 128 256 512; do
        sips -z $s $s "$LOGO_PNG" --out "$ICONSET_TMP/icon_${s}x${s}.png" >/dev/null 2>&1
        sips -z $((s*2)) $((s*2)) "$LOGO_PNG" --out "$ICONSET_TMP/icon_${s}x${s}@2x.png" >/dev/null 2>&1
    done

    if iconutil -c icns "$ICONSET_TMP" -o "$APP_BUNDLE/Contents/Resources/deepaiug-logo.icns" >> "$LOG" 2>&1; then
        cat > "$APP_BUNDLE/Contents/Info.plist" << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>DeepAiUG</string>
    <key>CFBundleIconFile</key>
    <string>deepaiug-logo.icns</string>
    <key>CFBundleIdentifier</key>
    <string>org.deepaiug.launcher</string>
    <key>CFBundleName</key>
    <string>DeepAiUG</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
</dict>
</plist>
PLIST_EOF

        cat > "$APP_BUNDLE/Contents/MacOS/DeepAiUG" << LAUNCHER_EOF
#!/bin/bash
osascript <<OSA
tell application "Terminal"
    activate
    do script "bash '$DEST/DeepAiUG.command'"
end tell
OSA
LAUNCHER_EOF
        chmod +x "$APP_BUNDLE/Contents/MacOS/DeepAiUG"
        xattr -dr com.apple.quarantine "$APP_BUNDLE" 2>/dev/null || true

        check_ok "App con icona creata: $APP_BUNDLE"
        echo "[LAUNCHER] .app bundle creato" >> "$LOG"
    else
        log "  [WARN] Conversione PNG->ICNS fallita, salto creazione .app"
        echo "[LAUNCHER] iconutil fallito, salto .app" >> "$LOG"
        rm -rf "$APP_BUNDLE"
    fi

    rm -rf "$(dirname "$ICONSET_TMP")"
fi

echo ""
echo -e "  ${YELLOW}NOTA Gatekeeper:${NC}"
echo "  Per avviare DeepAiUG la prima volta:"
echo "    1. Vai in $DEST nel Finder"
echo "    2. Tasto destro su DeepAiUG.app (o DeepAiUG.command)"
echo "    3. Scegli 'Apri' (non doppio click)"
echo "    4. Conferma nella finestra di sicurezza"
echo "    Le volte successive potrai fare doppio click normalmente."
echo ""

# ============================================================
# STEP 12 - RIEPILOGO FINALE
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
echo "    Doppio click su $DEST/DeepAiUG.app  (icona personalizzata)"
echo "    oppure: $DEST/DeepAiUG.command"
echo "    (prima volta: tasto destro > Apri)"
echo "    La prima volta attendi 20-30 secondi."
echo ""
echo "  PROBLEMI?"
echo "    Lancia: bash installer/check_deepaiug.sh"
echo ""
echo -e "  Log completo salvato in: ${CYAN}$LOG${NC}"
echo ""
echo -e "${BOLD}============================================================${NC}"
echo ""
