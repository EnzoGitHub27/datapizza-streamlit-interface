@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================
::  INSTALLA_DeepAiUG.bat
::  Installer automatico DeepAiUG per Windows 11
::  v1.11.2
:: ============================================================

:: --- VARIABILI GLOBALI ---
set "DEST=%USERPROFILE%\DeepAiUG"
set "VENV=venv"
set "LOG=%USERPROFILE%\DeepAiUG_install_log.txt"
set "GITHUB_ZIP=https://github.com/EnzoGitHub27/datapizza-streamlit-interface/archive/refs/heads/main.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"
set "OLLAMA_URL=https://ollama.com/download/OllamaSetup.exe"
set "PYTHON_EXE=C:\Program Files\Python312\python.exe"

:: --- INIZIALIZZAZIONE LOG ---
echo. > "!LOG!"
echo ============================================================ >> "!LOG!"
echo  DeepAiUG Installer - Log di installazione >> "!LOG!"
echo  Data: %DATE% %TIME% >> "!LOG!"
echo ============================================================ >> "!LOG!"

title DeepAiUG - Installazione automatica

echo.
echo  ============================================================
echo       DeepAiUG - Installazione automatica Windows 11
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
    echo   Premi un tasto per uscire...
    pause >nul
    exit /b 1
)
echo   [OK] Permessi di Amministratore verificati.
echo [OK] Permessi di Amministratore verificati >> "!LOG!"
echo.

:: ============================================================
:: STEP 1 - DISCLAIMER
:: ============================================================
echo  ------------------------------------------------------------
echo   DISCLAIMER - Leggere attentamente
echo  ------------------------------------------------------------
echo.
echo   Questo script installera' automaticamente:
echo.
echo     - Python 3.12         (linguaggio di programmazione)
echo     - Ollama              (motore AI locale)
echo     - DeepAiUG v1.11.2   (interfaccia chat AI)
echo     - Un modello AI       (1-5 GB, in base alla RAM)
echo.
echo   Cartella di installazione: !DEST!
echo.
echo   NOTA: L'installazione richiede connessione Internet e
echo   puo' impiegare 10-30 minuti in base alla velocita' di rete.
echo.
echo   L'autore non si assume responsabilita' per eventuali
echo   problemi derivanti dall'uso di questo software.
echo   Il software e' fornito "cosi' com'e'" senza garanzie.
echo.
echo  ------------------------------------------------------------
echo.
set /p "ACCETTA=  Vuoi procedere con l'installazione? (S/N): "
echo [DISCLAIMER] Risposta utente: !ACCETTA! >> "!LOG!"

if /i "!ACCETTA!" neq "S" (
    echo.
    echo   Installazione annullata dall'utente.
    echo [DISCLAIMER] Installazione annullata >> "!LOG!"
    echo.
    pause
    exit /b 0
)
echo.
echo   [OK] Installazione avviata.
echo [OK] Installazione avviata >> "!LOG!"
echo.

:: ============================================================
:: STEP 2 - CHECK SISTEMA
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 2 - Controllo sistema
echo  ------------------------------------------------------------
echo.

:: --- RAM ---
set "RAM_BYTES=0"
for /f "skip=1 tokens=*" %%A in ('wmic computersystem get TotalPhysicalMemory 2^>nul') do (
    set "RAM_LINE=%%A"
    if defined RAM_LINE (
        set "RAM_LINE=!RAM_LINE: =!"
        if "!RAM_LINE!" neq "" (
            if !RAM_BYTES! equ 0 set "RAM_BYTES=!RAM_LINE!"
        )
    )
)
:: Calcolo GB via PowerShell (evita limiti aritmetici batch)
for /f %%G in ('powershell -Command "[math]::Round(!RAM_BYTES!/1GB, 0)"') do set "RAM_GB=%%G"
echo   RAM totale: !RAM_GB! GB
echo [SISTEMA] RAM: !RAM_GB! GB >> "!LOG!"

:: --- GPU ---
set "GPU_NAME=Non rilevata"
for /f "skip=1 tokens=*" %%A in ('wmic path win32_VideoController get name 2^>nul') do (
    set "GPU_LINE=%%A"
    if defined GPU_LINE (
        set "GPU_LINE=!GPU_LINE: =!"
        if "!GPU_LINE!" neq "" (
            if "!GPU_NAME!" == "Non rilevata" (
                for /f "tokens=*" %%B in ("%%A") do set "GPU_NAME=%%B"
            )
        )
    )
)
echo   GPU: !GPU_NAME!
echo [SISTEMA] GPU: !GPU_NAME! >> "!LOG!"
echo.

:: ============================================================
:: STEP 3 - VERIFICA/INSTALLA PYTHON 3.12
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 3 - Python 3.12
echo  ------------------------------------------------------------
echo.

set "PYTHON_FOUND=0"
set "PYTHON_CMD="

:: Prova percorso fisso
if exist "!PYTHON_EXE!" (
    set "PYTHON_FOUND=1"
    set "PYTHON_CMD=!PYTHON_EXE!"
    echo   [OK] Python trovato in: !PYTHON_EXE!
    echo [PYTHON] Trovato in percorso fisso: !PYTHON_EXE! >> "!LOG!"
)

:: Prova PATH
if !PYTHON_FOUND! equ 0 (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%P in ('where python') do (
            if !PYTHON_FOUND! equ 0 (
                set "PYTHON_CMD=%%P"
                set "PYTHON_FOUND=1"
                echo   [OK] Python trovato nel PATH: %%P
                echo [PYTHON] Trovato nel PATH: %%P >> "!LOG!"
            )
        )
    )
)

if !PYTHON_FOUND! equ 0 (
    echo   Python 3.12 non trovato. Avvio download...
    echo [PYTHON] Non trovato, avvio download >> "!LOG!"
    echo.
    call :DownloadFile "!PYTHON_URL!" "!DEST!\python_installer.exe" "Python 3.12"
    if !errorlevel! neq 0 goto :EOF

    echo.
    echo   Installazione Python 3.12 in corso... attendere...
    echo [PYTHON] Avvio installazione silenziosa >> "!LOG!"
    "!DEST!\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 >> "!LOG!" 2>&1

    if !errorlevel! neq 0 (
        echo   [ERRORE] Installazione Python fallita.
        echo [PYTHON] ERRORE installazione, errorlevel=!errorlevel! >> "!LOG!"
        echo   Prova a installare manualmente da: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )

    set "PYTHON_CMD=!PYTHON_EXE!"
    echo   [OK] Python 3.12 installato correttamente.
    echo [PYTHON] Installazione completata >> "!LOG!"
    del "!DEST!\python_installer.exe" >nul 2>&1
)
echo.

:: ============================================================
:: STEP 4 - VERIFICA/INSTALLA OLLAMA
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 4 - Ollama
echo  ------------------------------------------------------------
echo.

set "OLLAMA_FOUND=0"
if exist "%LOCALAPPDATA%\Ollama\ollama.exe" (
    set "OLLAMA_FOUND=1"
    echo   [OK] Ollama trovato in: %LOCALAPPDATA%\Ollama\
    echo [OLLAMA] Trovato in %LOCALAPPDATA%\Ollama\ >> "!LOG!"
)

if !OLLAMA_FOUND! equ 0 (
    where ollama >nul 2>&1
    if !errorlevel! equ 0 (
        set "OLLAMA_FOUND=1"
        echo   [OK] Ollama trovato nel PATH.
        echo [OLLAMA] Trovato nel PATH >> "!LOG!"
    )
)

if !OLLAMA_FOUND! equ 0 (
    echo   Ollama non trovato. Avvio download...
    echo [OLLAMA] Non trovato, avvio download >> "!LOG!"
    echo.
    call :DownloadFile "!OLLAMA_URL!" "!DEST!\OllamaSetup.exe" "Ollama"
    if !errorlevel! neq 0 goto :EOF

    echo.
    echo   Installazione Ollama in corso... attendere...
    echo [OLLAMA] Avvio installazione silenziosa >> "!LOG!"
    "!DEST!\OllamaSetup.exe" /silent >> "!LOG!" 2>&1

    if !errorlevel! neq 0 (
        echo   [ATTENZIONE] Installazione Ollama potrebbe richiedere un riavvio.
        echo [OLLAMA] Possibile riavvio necessario, errorlevel=!errorlevel! >> "!LOG!"
    ) else (
        echo   [OK] Ollama installato correttamente.
        echo [OLLAMA] Installazione completata >> "!LOG!"
    )
    del "!DEST!\OllamaSetup.exe" >nul 2>&1
)
:: Aggiorna PATH nella sessione corrente per trovare ollama subito
set "PATH=!PATH!;%LOCALAPPDATA%\Programs\Ollama"
echo.

:: ============================================================
:: STEP 5 - DOWNLOAD DEEPAIUG
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 5 - Download DeepAiUG
echo  ------------------------------------------------------------
echo.

if not exist "!DEST!" (
    mkdir "!DEST!" >> "!LOG!" 2>&1
    echo   [OK] Cartella creata: !DEST!
    echo [DOWNLOAD] Cartella creata: !DEST! >> "!LOG!"
)

echo   Download repository da GitHub...
echo [DOWNLOAD] Avvio download ZIP da GitHub >> "!LOG!"
call :DownloadFile "!GITHUB_ZIP!" "!DEST!\deepaiug.zip" "DeepAiUG"
if !errorlevel! neq 0 goto :EOF

echo.
echo   Estrazione file... attendere...
echo [DOWNLOAD] Estrazione ZIP >> "!LOG!"
powershell -Command "Expand-Archive -Path '!DEST!\deepaiug.zip' -DestinationPath '!DEST!\temp_extract' -Force" >> "!LOG!" 2>&1

if !errorlevel! neq 0 (
    echo   [ERRORE] Estrazione ZIP fallita.
    echo [DOWNLOAD] ERRORE estrazione ZIP >> "!LOG!"
    pause
    exit /b 1
)
echo   [OK] Estrazione completata.
echo [DOWNLOAD] Estrazione completata >> "!LOG!"

:: Copia file dalla sottocartella estratta alla destinazione
echo   Copia file in !DEST!...
echo [DOWNLOAD] xcopy in corso >> "!LOG!"
xcopy "!DEST!\temp_extract\datapizza-streamlit-interface-main\*" "!DEST!\" /E /Y /Q >> "!LOG!" 2>&1

if !errorlevel! neq 0 (
    echo   [ERRORE] Copia file fallita.
    echo [DOWNLOAD] ERRORE xcopy >> "!LOG!"
    pause
    exit /b 1
)

:: Pulizia
del "!DEST!\deepaiug.zip" >nul 2>&1
rmdir /S /Q "!DEST!\temp_extract" >nul 2>&1
echo   [OK] File DeepAiUG copiati in: !DEST!
echo [DOWNLOAD] File copiati e pulizia completata >> "!LOG!"
echo.

:: ============================================================
:: STEP 6 - CREA VENV E DIPENDENZE
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 6 - Ambiente virtuale e dipendenze
echo  ------------------------------------------------------------
echo.

cd /d "!DEST!"

echo   Creazione ambiente virtuale (venv)... attendere...
echo [VENV] Creazione venv >> "!LOG!"
"!PYTHON_CMD!" -m venv !VENV! >> "!LOG!" 2>&1

if !errorlevel! neq 0 (
    echo   [ERRORE] Creazione venv fallita.
    echo [VENV] ERRORE creazione venv >> "!LOG!"
    pause
    exit /b 1
)
echo   [OK] Ambiente virtuale creato.
echo [VENV] Creazione completata >> "!LOG!"

echo.
echo   Aggiornamento pip... attendere...
echo [PIP] Aggiornamento pip >> "!LOG!"
.\!VENV!\Scripts\python.exe -m pip install --upgrade pip >> "!LOG!" 2>&1
echo   [OK] pip aggiornato.
echo [PIP] pip aggiornato >> "!LOG!"

echo.
echo   Installazione datapizza-ai... attendere...
echo [PIP] Installazione datapizza-ai >> "!LOG!"
.\!VENV!\Scripts\pip.exe install datapizza-ai >> "!LOG!" 2>&1

if !errorlevel! neq 0 (
    echo   [ERRORE] Installazione datapizza-ai fallita.
    echo [PIP] ERRORE datapizza-ai >> "!LOG!"
    pause
    exit /b 1
)
echo   [OK] datapizza-ai installato.
echo [PIP] datapizza-ai installato >> "!LOG!"

echo.
echo   Installazione dipendenze da requirements.txt... attendere...
echo   (potrebbe richiedere qualche minuto)
echo [PIP] Installazione requirements.txt >> "!LOG!"
.\!VENV!\Scripts\pip.exe install -r requirements.txt >> "!LOG!" 2>&1

if !errorlevel! neq 0 (
    echo   [ERRORE] Installazione dipendenze fallita.
    echo [PIP] ERRORE requirements.txt >> "!LOG!"
    echo   Controlla il log per dettagli: !LOG!
    pause
    exit /b 1
)
echo   [OK] Librerie installate.
echo [PIP] Tutte le dipendenze installate >> "!LOG!"
echo.

:: ============================================================
:: STEP 7 - SUGGERIMENTO MODELLO
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 7 - Scelta modello AI
echo  ------------------------------------------------------------
echo.

set "DEFAULT_MODEL=phi3:mini"

if !RAM_GB! lss 8 (
    set "DEFAULT_MODEL=phi3:mini"
    echo   RAM: !RAM_GB! GB - Modelli consigliati:
    echo.
    echo     [Default] phi3:mini     (~2.3 GB)
    echo              tinyllama      (~1.1 GB)
    echo.
) else if !RAM_GB! lss 16 (
    set "DEFAULT_MODEL=llama3.2:3b"
    echo   RAM: !RAM_GB! GB - Modelli consigliati:
    echo.
    echo     [Default] llama3.2:3b   (~2.0 GB)
    echo              phi3           (~2.3 GB)
    echo              phi3:mini      (~2.3 GB)
    echo.
) else if !RAM_GB! lss 32 (
    set "DEFAULT_MODEL=mistral:7b"
    echo   RAM: !RAM_GB! GB - Modelli consigliati:
    echo.
    echo     [Default] mistral:7b    (~4.1 GB)
    echo              llama3.2:3b    (~2.0 GB)
    echo              gemma2:9b      (~5.4 GB)
    echo.
) else (
    set "DEFAULT_MODEL=llama3.1:8b"
    echo   RAM: !RAM_GB! GB - Modelli consigliati:
    echo.
    echo     [Default] llama3.1:8b   (~4.7 GB)
    echo              mistral:7b     (~4.1 GB)
    echo              gemma2:9b      (~5.4 GB)
    echo.
)

echo   Premi INVIO per usare il modello default: !DEFAULT_MODEL!
echo   Oppure scrivi il nome di un altro modello.
echo.
set /p "MODELLO=  Modello (INVIO = !DEFAULT_MODEL!): "

if "!MODELLO!" == "" set "MODELLO=!DEFAULT_MODEL!"

echo.
echo   [OK] Modello scelto: !MODELLO!
echo [MODELLO] Scelto: !MODELLO! >> "!LOG!"
echo.

:: ============================================================
:: STEP 8 - DOWNLOAD MODELLO
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 8 - Download modello AI: !MODELLO!
echo  ------------------------------------------------------------
echo.
echo   Avvio Ollama in background...
echo [MODELLO] Avvio Ollama >> "!LOG!"

:: Avvia Ollama app in background
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe" (
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe"
) else if exist "%LOCALAPPDATA%\Ollama\ollama app.exe" (
    start "" "%LOCALAPPDATA%\Ollama\ollama app.exe"
) else (
    start /B ollama serve 2>nul
)

echo   Attesa avvio Ollama...
timeout /t 6 /nobreak >nul

echo.
echo   Download modello !MODELLO! in corso...
echo   (il download puo' richiedere qualche minuto)
echo.
echo [MODELLO] Avvio download: !MODELLO! >> "!LOG!"
ollama pull !MODELLO! 2>> "!LOG!"

if !errorlevel! neq 0 (
    echo.
    echo   [ATTENZIONE] Download modello fallito o Ollama non raggiungibile.
    echo [MODELLO] ERRORE download: !MODELLO! >> "!LOG!"
    echo.
    echo   Puoi scaricarlo manualmente dopo l'installazione con:
    echo     ollama pull !MODELLO!
    echo.
    echo   L'installazione prosegue comunque...
    echo.
) else (
    echo.
    echo   [OK] Modello !MODELLO! scaricato.
    echo [MODELLO] Download completato: !MODELLO! >> "!LOG!"
)
echo.

:: ============================================================
:: STEP 9 - CREA LAUNCHER E SHORTCUT DESKTOP
:: ============================================================
echo  ------------------------------------------------------------
echo   STEP 9 - Creazione launcher e collegamento Desktop
echo  ------------------------------------------------------------
echo.

:: --- Crea launcher DeepAiUG.bat ---
echo   Creazione launcher...
echo [LAUNCHER] Creazione DeepAiUG.bat >> "!LOG!"

(
    echo @echo off
    echo title DeepAiUG
    echo cd /d "!DEST!"
    echo.
    echo :: Controlla se Ollama e' in esecuzione
    echo tasklist /FI "IMAGENAME eq ollama.exe" 2^>nul ^| find /I "ollama.exe" ^>nul
    echo if %%errorlevel%% neq 0 ^(
    echo     echo   Avvio Ollama...
    echo     if exist "%%LOCALAPPDATA%%\Programs\Ollama\ollama app.exe" ^(
    echo         start "" "%%LOCALAPPDATA%%\Programs\Ollama\ollama app.exe"
    echo     ^) else if exist "%%LOCALAPPDATA%%\Ollama\ollama app.exe" ^(
    echo         start "" "%%LOCALAPPDATA%%\Ollama\ollama app.exe"
    echo     ^) else ^(
    echo         start /B ollama serve 2^>nul
    echo     ^)
    echo     timeout /t 5 /nobreak ^>nul
    echo ^)
    echo.
    echo echo   Avvio DeepAiUG... il browser si apre in 20-30 secondi.
    echo .\venv\Scripts\python.exe -m streamlit run app.py
) > "!DEST!\DeepAiUG.bat"

echo   [OK] Launcher creato: !DEST!\DeepAiUG.bat
echo [LAUNCHER] Launcher creato >> "!LOG!"

:: --- Crea shortcut Desktop via VBScript ---
echo   Creazione collegamento sul Desktop...
echo [SHORTCUT] Creazione shortcut Desktop >> "!LOG!"

set "VBS_TEMP=!DEST!\create_shortcut.vbs"
(
    echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
    echo strDesktop = WshShell.SpecialFolders^("Desktop"^)
    echo Set oLink = WshShell.CreateShortcut^(strDesktop ^& "\DeepAiUG.lnk"^)
    echo oLink.TargetPath = "!DEST!\DeepAiUG.bat"
    echo oLink.WorkingDirectory = "!DEST!"
    echo oLink.Description = "Avvia DeepAiUG - AI locale privacy-first"
    echo oLink.Save
) > "!VBS_TEMP!"

cscript //nologo "!VBS_TEMP!" >> "!LOG!" 2>&1
del "!VBS_TEMP!" >nul 2>&1

echo   [OK] Collegamento creato sul Desktop.
echo [SHORTCUT] Shortcut creato >> "!LOG!"
echo.

:: ============================================================
:: RIEPILOGO FINALE
:: ============================================================
echo [FINE] Installazione completata >> "!LOG!"

echo.
echo  ============================================================
echo       INSTALLAZIONE COMPLETATA!
echo  ============================================================
echo.
echo   Percorso installazione:  !DEST!
echo   Modello installato:      !MODELLO!
echo.
echo   COME AVVIARE:
echo     Clicca l'icona "DeepAiUG" sul Desktop.
echo     La prima volta attendi 20-30 secondi.
echo.
echo   PROBLEMI?
echo     Lancia CHECK_DeepAiUG.bat per la diagnostica.
echo.
echo   Log completo salvato in: !LOG!
echo.
echo  ============================================================
echo.
pause
exit /b 0

:: ============================================================
:: SUBROUTINE :DownloadFile
:: Parametri: %1=URL  %2=destinazione  %3=descrizione
:: ============================================================
:DownloadFile
echo   Download %~3 in corso...
echo [DOWNLOAD] %~3: %~1 >> "!LOG!"

powershell -Command "Invoke-WebRequest -Uri '%~1' -OutFile '%~2'"

if !errorlevel! neq 0 (
    echo.
    echo   [ERRORE] Download %~3 fallito.
    echo [DOWNLOAD] ERRORE download %~3 >> "!LOG!"
    echo   Controlla la connessione Internet e riprova.
    echo.
    exit /b 1
)

echo   [OK] Download %~3 completato.
echo [DOWNLOAD] %~3 completato >> "!LOG!"
exit /b 0
