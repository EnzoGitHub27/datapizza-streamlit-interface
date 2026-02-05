@echo off
REM =============================================================================
REM Script di Installazione per DeepAiUG Streamlit LLM Interface (Windows)
REM =============================================================================

echo.
echo ============================================================
echo    Installazione DeepAiUG Streamlit LLM Interface
echo ============================================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato! Installa Python 3.8 o superiore.
    pause
    exit /b 1
)

echo [OK] Python trovato
echo.

REM Aggiorna pip
echo Aggiornamento pip...
python -m pip install --upgrade pip
echo [OK] pip aggiornato
echo.

REM Installa dipendenze base
echo [1/4] Installazione dipendenze base...
python -m pip install streamlit python-dotenv
if errorlevel 1 (
    echo [ERRORE] Installazione dipendenze base fallita!
    pause
    exit /b 1
)
echo [OK] streamlit e python-dotenv installati
echo.

REM Installa datapizza AI core (libreria)
echo [2/4] Installazione datapizza AI (libreria)...
python -m pip install datapizza-ai
if errorlevel 1 (
    echo [ERRORE] Installazione datapizza-ai fallita!
    pause
    exit /b 1
)
echo [OK] datapizza-ai installato
echo.

REM Chiedi quali provider installare
echo Quali provider cloud vuoi installare?
echo 1) Tutti (OpenAI, Anthropic, Google)
echo 2) Solo OpenAI
echo 3) Solo Anthropic (Claude)
echo 4) Solo Google (Gemini)
echo 5) Nessuno (solo Ollama locale)
echo.
set /p choice="Scelta [1-5]: "

if "%choice%"=="1" goto install_all
if "%choice%"=="2" goto install_openai
if "%choice%"=="3" goto install_anthropic
if "%choice%"=="4" goto install_google
if "%choice%"=="5" goto install_none
goto invalid_choice

:install_all
echo [3/4] Installazione tutti i provider cloud...
python -m pip install datapizza-ai-clients-openai
echo [OK] OpenAI client installato
python -m pip install datapizza-ai-clients-anthropic
echo [OK] Anthropic client installato
python -m pip install datapizza-ai-clients-google
echo [OK] Google client installato
goto done

:install_openai
echo [3/4] Installazione OpenAI client...
python -m pip install datapizza-ai-clients-openai
echo [OK] OpenAI client installato
goto done

:install_anthropic
echo [3/4] Installazione Anthropic client...
python -m pip install datapizza-ai-clients-anthropic
echo [OK] Anthropic client installato
goto done

:install_google
echo [3/4] Installazione Google client...
python -m pip install datapizza-ai-clients-google
echo [OK] Google client installato
goto done

:install_none
echo [AVVISO] Nessun provider cloud installato.
echo Solo modalita Ollama disponibile.
goto done

:invalid_choice
echo [ERRORE] Scelta non valida!
pause
exit /b 1

:done
echo.
echo ============================================================
echo    Installazione completata con successo!
echo ============================================================
echo.
echo Per avviare l'applicazione:
echo   streamlit run 00_interfaccia_dinamica_datapizza_Streamlit.py
echo.
echo Per configurare le API keys:
echo   - Crea un file .env nella directory del progetto
echo   - Oppure crea file secrets\{provider}_key.txt
echo.
pause