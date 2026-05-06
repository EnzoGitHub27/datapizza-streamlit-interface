@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================
::  AGGIORNA_DeepAiUG.bat
::  Script di aggiornamento DeepAiUG per Windows 11
::  Preserva conversazioni e configurazioni personali
:: ============================================================

:: --- VARIABILI GLOBALI ---
set "DEST=%USERPROFILE%\DeepAiUG"
set "VENV=venv"
set "GITHUB_ZIP=https://github.com/EnzoGitHub27/datapizza-streamlit-interface/archive/refs/heads/main.zip"
set "BACKUP=%USERPROFILE%\DeepAiUG_backup_conversations"
set "LOG=%USERPROFILE%\DeepAiUG_update_log.txt"
set "TEMP_ZIP=%TEMP%\deepaiug_update.zip"
set "TEMP_DIR=%TEMP%\deepaiug_update_tmp"
set "SRC=%TEMP_DIR%\datapizza-streamlit-interface-main"

:: --- INIZIALIZZAZIONE LOG ---
echo. > "!LOG!"
echo ============================================================ >> "!LOG!"
echo  DeepAiUG Updater - Log di aggiornamento >> "!LOG!"
echo  Data: %DATE% %TIME% >> "!LOG!"
echo ============================================================ >> "!LOG!"

title DeepAiUG - Aggiornamento

echo.
echo  ============================================================
echo       DeepAiUG - Aggiornamento automatico
echo  ============================================================
echo.

:: ============================================================
:: STEP 0 - VERIFICA ADMIN
:: ============================================================
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo   [ERRORE] Questo script richiede i permessi di Amministratore.
    echo   [ERRORE] Permessi di Amministratore richiesti >> "!LOG!"
    echo.
    echo   Tasto destro sul file ^> "Esegui come amministratore"
    echo.
    pause
    exit /b 1
)
echo   [OK] Permessi di Amministratore verificati.
echo [OK] Permessi di Amministratore verificati >> "!LOG!"
echo.

:: ============================================================
:: STEP 1 - VERIFICA INSTALLAZIONE ESISTENTE
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 1 - Verifica installazione esistente
echo  ------------------------------------------------------------
echo.

if not exist "!DEST!" (
    echo   [ERRORE] DeepAiUG non trovato in: !DEST!
    echo [ERRORE] Cartella non trovata: !DEST! >> "!LOG!"
    echo.
    echo   Usa INSTALLA_DeepAiUG.bat per la prima installazione.
    echo.
    pause
    exit /b 1
)

if not exist "!DEST!\!VENV!\Scripts\python.exe" (
    echo   [ERRORE] Ambiente virtuale non trovato in: !DEST!\!VENV!
    echo [ERRORE] venv non trovato >> "!LOG!"
    echo.
    echo   Usa INSTALLA_DeepAiUG.bat per reinstallare.
    echo.
    pause
    exit /b 1
)

echo   [OK] DeepAiUG trovato in: !DEST!
echo [OK] Installazione trovata: !DEST! >> "!LOG!"
echo.

:: ============================================================
:: STEP 2 - LEGGI VERSIONE ATTUALE
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 2 - Versione attuale
echo  ------------------------------------------------------------
echo.

set "OLD_VERSION=sconosciuta"
if exist "!DEST!\config\constants.py" (
    for /f "tokens=3 delims= " %%V in ('findstr /C:"VERSION = " "!DEST!\config\constants.py" 2^>nul') do (
        set "OLD_VERSION=%%~V"
    )
)
echo   Versione attuale: !OLD_VERSION!
echo [VERSIONE] Attuale: !OLD_VERSION! >> "!LOG!"
echo.

:: ============================================================
:: STEP 3 - BACKUP CONVERSAZIONI
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 3 - Backup conversazioni
echo  ------------------------------------------------------------
echo.

if exist "!DEST!\conversations" (
    echo   Backup conversazioni in corso...
    echo [BACKUP] Avvio backup conversazioni >> "!LOG!"
    if not exist "!BACKUP!" mkdir "!BACKUP!" >> "!LOG!" 2>&1
    xcopy /E /Y /Q "!DEST!\conversations\*" "!BACKUP!\" >> "!LOG!" 2>&1
    echo   [OK] Backup conversazioni salvato in: !BACKUP!
    echo [BACKUP] Completato: !BACKUP! >> "!LOG!"
) else (
    echo   [INFO] Nessuna cartella conversations/ trovata. Nulla da salvare.
    echo [BACKUP] Nessuna conversazione trovata >> "!LOG!"
)
echo.

:: ============================================================
:: STEP 4 - DOWNLOAD NUOVA VERSIONE
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 4 - Download nuova versione da GitHub
echo  ------------------------------------------------------------
echo.

echo   Download in corso...
echo [DOWNLOAD] Avvio download da GitHub >> "!LOG!"

powershell -Command "Invoke-WebRequest -Uri '!GITHUB_ZIP!' -OutFile '!TEMP_ZIP!' -UseBasicParsing" >> "!LOG!" 2>&1

if !errorlevel! neq 0 (
    echo   [ERRORE] Download fallito.
    echo [DOWNLOAD] ERRORE download >> "!LOG!"
    echo   Controlla la connessione Internet e riprova.
    echo.
    pause
    exit /b 1
)
echo   [OK] Download completato.
echo [DOWNLOAD] Completato >> "!LOG!"
echo.

:: ============================================================
:: STEP 5 - ESTRAI IN CARTELLA TEMPORANEA
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 5 - Estrazione file
echo  ------------------------------------------------------------
echo.

if exist "!TEMP_DIR!" rmdir /S /Q "!TEMP_DIR!" >nul 2>&1
echo   Estrazione in corso...
echo [ESTRAZIONE] Avvio >> "!LOG!"

powershell -Command "Expand-Archive -Path '!TEMP_ZIP!' -DestinationPath '!TEMP_DIR!' -Force" >> "!LOG!" 2>&1

if !errorlevel! neq 0 (
    echo   [ERRORE] Estrazione fallita.
    echo [ESTRAZIONE] ERRORE >> "!LOG!"
    pause
    exit /b 1
)
echo   [OK] Estrazione completata.
echo [ESTRAZIONE] Completato >> "!LOG!"
echo.

:: ============================================================
:: STEP 6 - AGGIORNA SOLO IL CODICE
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 6 - Aggiornamento codice
echo  ------------------------------------------------------------
echo.
echo   Aggiornamento file di codice...
echo   (conversazioni e configurazioni preservate)
echo [AGGIORNAMENTO] Avvio copia selettiva >> "!LOG!"

:: --- File singoli ---
copy /Y "!SRC!\app.py" "!DEST!\" >> "!LOG!" 2>&1
copy /Y "!SRC!\requirements.txt" "!DEST!\" >> "!LOG!" 2>&1
copy /Y "!SRC!\pyproject.toml" "!DEST!\" >> "!LOG!" 2>&1

:: --- Cartelle di codice ---
xcopy /E /Y /Q "!SRC!\config\*" "!DEST!\config\" >> "!LOG!" 2>&1
xcopy /E /Y /Q "!SRC!\core\*" "!DEST!\core\" >> "!LOG!" 2>&1
xcopy /E /Y /Q "!SRC!\ui\*" "!DEST!\ui\" >> "!LOG!" 2>&1
xcopy /E /Y /Q "!SRC!\rag\*" "!DEST!\rag\" >> "!LOG!" 2>&1
xcopy /E /Y /Q "!SRC!\export\*" "!DEST!\export\" >> "!LOG!" 2>&1
xcopy /E /Y /Q "!SRC!\installer\*" "!DEST!\installer\" >> "!LOG!" 2>&1
xcopy /E /Y /Q "!SRC!\.streamlit\*" "!DEST!\.streamlit\" >> "!LOG!" 2>&1

:: --- Ripristina file preservati (sovrascritti da config/) ---
:: I YAML nella root NON vengono copiati — solo il codice
echo.
echo   [OK] Codice aggiornato.
echo   [OK] Preservati: conversations/, branding.yaml, cloud_models.yaml,
echo        remote_servers.yaml, security_settings.yaml, wiki_sources.yaml,
echo        secrets/, .env
echo [AGGIORNAMENTO] Copia selettiva completata >> "!LOG!"
echo.

:: ============================================================
:: STEP 7 - AGGIORNA DIPENDENZE PIP
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 7 - Aggiornamento dipendenze Python
echo  ------------------------------------------------------------
echo.

cd /d "!DEST!"

echo   Aggiornamento datapizza-ai...
echo [PIP] Aggiornamento datapizza-ai >> "!LOG!"
.\!VENV!\Scripts\pip.exe install datapizza-ai --upgrade --quiet >> "!LOG!" 2>&1
echo   [OK] datapizza-ai aggiornato.

echo.
echo   Aggiornamento dipendenze da requirements.txt
echo.
echo   ATTESA LUNGA possibile su update v1.15.0+ (5-15 min, fino a 30 min).
echo   Nuovo: sentence-transformers scarica torch (anche oltre 1 GB) + altri.
echo   Vedrai le barre di pip a schermo. NON CHIUDERE LA FINESTRA.
echo.
echo [PIP] Aggiornamento requirements.txt >> "!LOG!"
:: v1.15.1 - output a schermo (no redirect su LOG, no --quiet) per visibilita'.
:: --prefer-binary preferisce wheel pre-compilati, accelera l'install.
.\!VENV!\Scripts\pip.exe install -r requirements.txt --upgrade --prefer-binary

if !errorlevel! neq 0 (
    echo   [ERRORE] Aggiornamento dipendenze fallito.
    echo [PIP] ERRORE requirements.txt >> "!LOG!"
    pause
    exit /b 1
)
echo   [OK] Dipendenze aggiornate.
echo [PIP] Aggiornamento completato >> "!LOG!"
echo.

:: ============================================================
:: STEP 8 - CLEANUP
:: ============================================================
del "!TEMP_ZIP!" >nul 2>&1
rmdir /S /Q "!TEMP_DIR!" >nul 2>&1
echo [CLEANUP] File temporanei rimossi >> "!LOG!"

:: ============================================================
:: STEP 9 - RIEPILOGO
:: ============================================================
set "NEW_VERSION=sconosciuta"
if exist "!DEST!\config\constants.py" (
    for /f "tokens=3 delims= " %%V in ('findstr /C:"VERSION = " "!DEST!\config\constants.py" 2^>nul') do (
        set "NEW_VERSION=%%~V"
    )
)
echo [VERSIONE] Nuova: !NEW_VERSION! >> "!LOG!"
echo [FINE] Aggiornamento completato >> "!LOG!"

echo.
echo  ============================================================
echo       AGGIORNAMENTO COMPLETATO!
echo  ============================================================
echo.
echo   Versione precedente:  !OLD_VERSION!
echo   Versione installata:  !NEW_VERSION!
echo.
echo   Conversazioni preservate in: !DEST!\conversations
echo   Backup conversazioni in:     !BACKUP!
echo.
echo   Log completo salvato in: !LOG!
echo.
echo  ============================================================
echo.
pause
exit /b 0
