#!/bin/bash
# ============================================================
#  aggiorna_deepaiug_mac.sh
#  Script di aggiornamento DeepAiUG per macOS
#  Preserva conversazioni e configurazioni personali
# ============================================================
set -e

# --- VARIABILI GLOBALI ---
DEST="$HOME/DeepAiUG"
VENV="venv"
GITHUB_ZIP="https://github.com/EnzoGitHub27/datapizza-streamlit-interface/archive/refs/heads/main.zip"
BACKUP="$HOME/DeepAiUG_backup_conversations"
LOG="$HOME/DeepAiUG_update_log.txt"
TEMP_ZIP="/tmp/deepaiug_update.zip"
TEMP_DIR="/tmp/deepaiug_update_tmp"
SRC="$TEMP_DIR/datapizza-streamlit-interface-main"

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
echo " DeepAiUG Updater macOS - Log di aggiornamento" >> "$LOG"
echo " Data: $(date)" >> "$LOG"
echo "============================================================" >> "$LOG"

echo ""
echo -e "${BOLD}============================================================${NC}"
echo -e "${BOLD}     DeepAiUG - Aggiornamento automatico macOS${NC}"
echo -e "${BOLD}============================================================${NC}"
echo ""

# ============================================================
# STEP 1 - VERIFICA INSTALLAZIONE ESISTENTE
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 1 - Verifica installazione esistente${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

if [[ ! -d "$DEST" ]]; then
    check_err "DeepAiUG non trovato in: $DEST" \
        "Usa installa_deepaiug_mac.sh per la prima installazione."
    exit 1
fi

if [[ ! -f "$DEST/$VENV/bin/python" ]]; then
    check_err "Ambiente virtuale non trovato in: $DEST/$VENV" \
        "Usa installa_deepaiug_mac.sh per reinstallare."
    exit 1
fi

check_ok "DeepAiUG trovato in: $DEST"
echo ""

# ============================================================
# STEP 2 - LEGGI VERSIONE ATTUALE
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 2 - Versione attuale${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

OLD_VERSION="sconosciuta"
if [[ -f "$DEST/config/constants.py" ]]; then
    OLD_VERSION=$(grep 'VERSION = ' "$DEST/config/constants.py" | head -1 | awk -F'"' '{print $2}')
fi
log "  Versione attuale: ${CYAN}$OLD_VERSION${NC}"
echo "[VERSIONE] Attuale: $OLD_VERSION" >> "$LOG"
echo ""

# ============================================================
# STEP 3 - BACKUP CONVERSAZIONI
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 3 - Backup conversazioni${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

if [[ -d "$DEST/conversations" ]]; then
    log "  Backup conversazioni in corso..."
    echo "[BACKUP] Avvio backup conversazioni" >> "$LOG"
    mkdir -p "$BACKUP"
    cp -r "$DEST/conversations/." "$BACKUP/" 2>/dev/null || true
    check_ok "Backup conversazioni salvato in: $BACKUP"
    echo "[BACKUP] Completato: $BACKUP" >> "$LOG"
else
    log "  ${CYAN}[INFO]${NC} Nessuna cartella conversations/ trovata. Nulla da salvare."
    echo "[BACKUP] Nessuna conversazione trovata" >> "$LOG"
fi
echo ""

# ============================================================
# STEP 4 - DOWNLOAD NUOVA VERSIONE
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 4 - Download nuova versione da GitHub${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

log "  Download in corso..."
echo "[DOWNLOAD] Avvio download da GitHub" >> "$LOG"

curl -L "$GITHUB_ZIP" -o "$TEMP_ZIP" --progress-bar

if [[ ! -f "$TEMP_ZIP" ]]; then
    check_err "Download fallito." "Controlla la connessione Internet e riprova."
    exit 1
fi
check_ok "Download completato."
echo "[DOWNLOAD] Completato" >> "$LOG"
echo ""

# ============================================================
# STEP 5 - ESTRAI IN CARTELLA TEMPORANEA
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 5 - Estrazione file${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

rm -rf "$TEMP_DIR"
log "  Estrazione in corso..."
echo "[ESTRAZIONE] Avvio" >> "$LOG"

unzip -q "$TEMP_ZIP" -d "$TEMP_DIR"

check_ok "Estrazione completata."
echo "[ESTRAZIONE] Completato" >> "$LOG"
echo ""

# ============================================================
# STEP 6 - AGGIORNA SOLO IL CODICE
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 6 - Aggiornamento codice${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""
log "  Aggiornamento file di codice..."
log "  (conversazioni e configurazioni preservate)"
echo "[AGGIORNAMENTO] Avvio copia selettiva" >> "$LOG"

# --- File singoli ---
cp "$SRC/app.py" "$DEST/"
cp "$SRC/requirements.txt" "$DEST/"
[[ -f "$SRC/pyproject.toml" ]] && cp "$SRC/pyproject.toml" "$DEST/"

# --- Cartelle di codice ---
cp -r "$SRC/config/." "$DEST/config/"
cp -r "$SRC/core/." "$DEST/core/"
cp -r "$SRC/ui/." "$DEST/ui/"
cp -r "$SRC/rag/." "$DEST/rag/"
cp -r "$SRC/export/." "$DEST/export/"
cp -r "$SRC/installer/." "$DEST/installer/"
[[ -d "$SRC/.streamlit" ]] && cp -r "$SRC/.streamlit/." "$DEST/.streamlit/"

# NON copiati: conversations/, branding.yaml, cloud_models.yaml,
# remote_servers.yaml, security_settings.yaml, wiki_sources.yaml,
# secrets/, .env

echo ""
check_ok "Codice aggiornato."
log "  ${CYAN}[INFO]${NC} Preservati: conversations/, branding.yaml, cloud_models.yaml,"
log "         remote_servers.yaml, security_settings.yaml, wiki_sources.yaml,"
log "         secrets/, .env"
echo "[AGGIORNAMENTO] Copia selettiva completata" >> "$LOG"
echo ""

# ============================================================
# STEP 7 - AGGIORNA DIPENDENZE PIP
# ============================================================
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo -e "${BOLD}  STEP 7 - Aggiornamento dipendenze Python${NC}"
echo -e "${BOLD}------------------------------------------------------------${NC}"
echo ""

cd "$DEST"
source "$DEST/$VENV/bin/activate"

log "  Aggiornamento datapizza-ai..."
echo "[PIP] Aggiornamento datapizza-ai" >> "$LOG"
pip install datapizza-ai --upgrade --quiet >> "$LOG" 2>&1
check_ok "datapizza-ai aggiornato."

log "  Aggiornamento dipendenze da requirements.txt"
echo ""
echo -e "  ${YELLOW}ATTESA LUNGA possibile su update v1.15.0+ (5-15 min, fino a 30).${NC}"
echo -e "  ${YELLOW}Nuovo: 'sentence-transformers' scarica torch (~250 MB su Mac) + altri.${NC}"
echo -e "  ${YELLOW}Vedrai le barre di pip a schermo. NON CHIUDERE LA FINESTRA.${NC}"
echo ""
echo "[PIP] Aggiornamento requirements.txt" >> "$LOG"
# v1.15.1 — output a schermo + tee. Rimosso --quiet (mascherava lo stato).
# --prefer-binary preferisce wheel pre-compilati, accelera l'install.
pip install -r requirements.txt --upgrade --prefer-binary 2>&1 | tee -a "$LOG"
PIP_RC=${PIPESTATUS[0]}
if [[ $PIP_RC -ne 0 ]]; then
    echo -e "  ${RED}[ERRORE]${NC} pip aggiornamento fallito (codice $PIP_RC)"
    echo "[PIP] ERRORE requirements.txt (rc=$PIP_RC)" >> "$LOG"
    exit 1
fi
check_ok "Dipendenze aggiornate."
echo "[PIP] Aggiornamento completato" >> "$LOG"

deactivate
echo ""

# ============================================================
# STEP 8 - CLEANUP E RIEPILOGO
# ============================================================
rm -f "$TEMP_ZIP"
rm -rf "$TEMP_DIR"
echo "[CLEANUP] File temporanei rimossi" >> "$LOG"

NEW_VERSION="sconosciuta"
if [[ -f "$DEST/config/constants.py" ]]; then
    NEW_VERSION=$(grep 'VERSION = ' "$DEST/config/constants.py" | head -1 | awk -F'"' '{print $2}')
fi
echo "[VERSIONE] Nuova: $NEW_VERSION" >> "$LOG"
echo "[FINE] Aggiornamento completato" >> "$LOG"

echo ""
echo -e "${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}     AGGIORNAMENTO COMPLETATO!${NC}"
echo -e "${BOLD}============================================================${NC}"
echo ""
echo -e "  Versione precedente:  ${CYAN}$OLD_VERSION${NC}"
echo -e "  Versione installata:  ${CYAN}$NEW_VERSION${NC}"
echo ""
echo "  Conversazioni preservate in: $DEST/conversations"
echo "  Backup conversazioni in:     $BACKUP"
echo ""
echo -e "  Log completo salvato in: ${CYAN}$LOG${NC}"
echo ""
echo -e "${BOLD}============================================================${NC}"
echo ""
