# v1.12.2 — Sistema Temi Selezionabili

## 🎨 Nuove Features

### Sistema Temi Dual
- **Business Modern** (default): Tema professionale bianco/blu per contesti aziendali
  - Font: Inter (sans-serif) — pulito e moderno
  - Colori: Bianco background, blu primary (#0066cc), grigio neutro
  - Dark mode: Supportato automaticamente
  - Design: Minimalista, moderno, corporate-ready

- **Matrix** (preservato): Tema originale nerd/tech
  - Font: Share Tech Mono (monospace) — retro futuristico
  - Colori: Nero profondo, teal (#00d4aa), verde Matrix (#00ff41)
  - Effetti: Scanlines CRT, glitch H1, pioggia Matrix
  - Design: Cyberpunk, atmosferico, audace

### Configurazione Semplice
Cambia tema in una sola riga di `branding.yaml`:
```yaml
theme: "business_modern"   # oppure "matrix"
```

## 📝 File Modificati

| File | Modifica |
|------|----------|
| `branding.yaml` | ✅ Aggiunto campo `theme:` con default "business_modern" |
| `config/branding.py` | ✅ Aggiunta costante `THEME` caricata da branding.yaml |
| `ui/style.py` | ✅ Rinominata `inject_matrix_style()` → funzione dedicata |
| `ui/style.py` | ✅ Aggiunta nuova funzione `inject_theme()` — factory pattern |
| `ui/style.py` | ✅ Rinominato `_inject_css()` → `_inject_matrix_css()` |
| `app.py` | ✅ Sostituito `inject_matrix_style()` con `inject_theme()` |
| `app.py` | ✅ Aggiornato import da ui.style |
| `.streamlit/config.toml` | ✅ Aggiornati colori fallback con commento Matrix |

## 🆕 File Creati

| File | Scopo |
|------|-------|
| `ui/business_style.py` | CSS Business Modern — nuovo tema professionale |
| `THEME_GUIDE.md` | Documentazione completa temi e personalizzazione |
| `CHANGELOG_v1.12.2.md` | Questo file |

## 🔄 Backward Compatibility

✅ **Totalmente compatibile:**
- Chi aveva `theme: "matrix"` in branding.yaml: continua a funzionare
- Chi non ha il campo `theme`: default automatico a "business_modern"
- Supporto pioggia Matrix (`matrix_rain`, `matrix_rain_intensity`) mantenuto

## 🎯 Quando Usare Quale Tema

### Business Modern
- ✅ Clienti/aziende
- ✅ Presentazioni formali
- ✅ Ambienti corporate
- ✅ Quando professionalità > cool fattore

### Matrix
- ✅ Team interno (tech/dev)
- ✅ Demo su hackathon
- ✅ Quando devi fare impressione su dev audience
- ✅ Research/AI showcase

## 📚 Documentazione

- **Guida completa:** [THEME_GUIDE.md](THEME_GUIDE.md)
- **Architettura:** [CLAUDE.md](CLAUDE.md#7-sistema-temi-v1122)
- **Come personalizzare colori:** [THEME_GUIDE.md - Personalizzazione](THEME_GUIDE.md#personalizzazione)

## 🚀 Come Testare

1. **Avvia l'app con tema default (Business Modern):**
   ```bash
   streamlit run app.py
   ```
   Dovrebbe vedere interfaccia bianca, pulita, professionale.

2. **Cambia tema a Matrix:**
   ```yaml
   # branding.yaml
   theme: "matrix"
   ```
   Riavvia app — dovrebbe vedere colori teal, scanlines, pioggia.

3. **Prova dark mode:**
   - Business Modern: Passa automaticamente a tema scuro se il browser/OS lo richiede
   - Matrix: Rimane nero (già scuro)

## 🔧 Personalizzazione

### Colori Business Modern
Modifica le variabili CSS in `ui/business_style.py` linee 15-32:
```python
:root {
  --primary: #0066cc;         # ← Cambia con il tuo colore brand
  --primary-dark: #0052a3;
  --bg: #ffffff;
  # etc...
}
```

### Intensità Pioggia Matrix
```yaml
theme: "matrix"
matrix_rain_intensity: 0.03   # Leggera
matrix_rain_intensity: 0.055  # Default
matrix_rain_intensity: 0.15   # Densa
```

## 🐛 Note Tecniche

- La scelta tema avviene **all'avvio** (letto da config at startup)
- Il CSS viene **iniettato** tramite `st.markdown(..., unsafe_allow_html=True)`
- Entrambi i temi supportano **dark mode** (via CSS `@media prefers-color-scheme`)
- La rinomina di `_inject_css()` → `_inject_matrix_css()` è **backward compatible** (funzione privata, non esposta)

## ✅ Testing Completato

- ✅ Syntax check Python (no errors)
- ✅ Config YAML valido
- ✅ Funzione `inject_theme()` routing corretto
- ✅ CSS Business Modern valido
- ✅ CSS Matrix preservato
- ✅ Costante THEME caricata correttamente

