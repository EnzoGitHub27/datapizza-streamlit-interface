# 🎨 Guida ai Temi — Business Modern & Matrix

## Come Cambiare Tema

Il tema si configura tramite il file **`branding.yaml`** nella root del progetto.

### Opzione 1: Business Modern (Professionale) — DEFAULT ✅

```yaml
# branding.yaml
theme: "business_modern"
```

**Caratteristiche:**
- ✅ Colori: Bianco, grigio neutro, blu moderno (#0066cc)
- ✅ Font: Inter (sans-serif) — pulito e professionale
- ✅ Design: Minimalista, moderno, adatto a contesti aziendali
- ✅ Chat: Card con sottili ombre, angoli arrotondati
- ✅ Bottoni: Blu solido, hover con ombra
- ✅ Dark mode: Supportato automaticamente (grigio scuro, testo chiaro)

**Quando usarlo:**
- Presentazioni aziendali
- Ambienti corporate
- Clienti professionali
- Contesti dove il "cool fattore" non è prioritario

---

### Opzione 2: Matrix (Nerd/Tech) — Originale

```yaml
# branding.yaml
theme: "matrix"
```

**Caratteristiche:**
- 🟢 Colori: Teal (#00d4aa), verde Matrix (#00ff41), nero profondo
- 🟢 Font: Share Tech Mono (monospace) — stile retro
- 🟢 Effetti: Scanlines CRT, glitch H1, pioggia Matrix
- 🟢 Design: Cyberpunk, atmosferico, audace
- 🟢 Configurazione pioggia:
  ```yaml
  theme: "matrix"
  matrix_rain: true                 # on/off
  matrix_rain_intensity: 0.055      # 0.01-0.20
  ```

**Quando usarlo:**
- Hackathon, demo tech
- Ambienti research/AI
- Quando vuoi fare impressione
- Team di developer che apprezza l'estetica

---

## Struttura Tecnica

### File Coinvolti

| File | Ruolo |
|------|-------|
| `branding.yaml` | **Config principale** — scegli il tema qui |
| `config/branding.py` | Carica il valore `theme` come costante `THEME` |
| `ui/style.py` | Factory che decide quale tema iniettare |
| `ui/business_style.py` | CSS tema Business Modern |
| `ui/style.py` (linee 1-200) | CSS tema Matrix (originale) |
| `app.py:137` | Chiama `inject_theme()` all'avvio |

### Come Funziona

```
1. Startup app (app.py)
   ↓
2. Legge branding.yaml
   ↓
3. config/branding.py calcola THEME = "business_modern" o "matrix"
   ↓
4. app.py chiama inject_theme()
   ↓
5. ui/style.py::inject_theme() controlla THEME
   ├─ Se "matrix" → inject_matrix_style()
   └─ Se "business_modern" → inject_business_style()
   ↓
6. CSS iniettato nel Streamlit app
```

---

## Personalizzazione

### Variare i Colori del Business Moderno

Se vuoi usare Business Modern ma con colori aziendali personalizzati, modifica `ui/business_style.py`:

```python
# ui/business_style.py linee 15-25
:root {
  --primary: #0066cc;         # ← Cambia il blu con il tuo colore brand
  --primary-dark: #0052a3;    # ← Versione scura
  --primary-light: #e6f2ff;   # ← Versione leggera
  --success: #27ae60;
  --warning: #f39c12;
  --error: #e74c3c;
}
```

### Variare Intensità Pioggia Matrix

```yaml
# branding.yaml
theme: "matrix"
matrix_rain_intensity: 0.01    # Molto leggera (fantasma)
matrix_rain_intensity: 0.055   # Default
matrix_rain_intensity: 0.20    # Molto densa
```

---

## Confronto Visivo

| Aspetto | Business Modern | Matrix |
|---------|-----------------|--------|
| **Sfondo** | Bianco | Nero profondo |
| **Testo** | Grigio scuro | Verde luminoso |
| **Bottoni** | Blu solido + hover | Border teal + glow |
| **Font** | Inter (sans) | Share Tech Mono |
| **Effetti** | Ombre subtili | Scanlines, glitch |
| **Impressione** | Serio, affidabile | Cool, futuristico |
| **Professionale?** | ✅ Sì | ⚠️ Per tech audience |

---

## Troubleshooting

### Il tema non cambia dopo il restart

1. **Cancella cache Streamlit:**
   ```bash
   streamlit cache clear
   ```

2. **Verifica che `branding.yaml` sia nel formato giusto:**
   ```yaml
   theme: "business_modern"    # Con virgolette, lowercase
   ```

3. **Se usi Matrix, assicurati che il valore sia esatto:**
   ```yaml
   theme: "matrix"  # Esattamente così
   ```

### I colori sono strani

- Se Matrix appare con colori chiari → controlla che sia `theme: "matrix"` e non Business
- Se Business appare con colori scuri → svuota la cache del browser (Ctrl+Shift+Delete)

### Vuoi tornare a Matrix dopo aver usato Business?

```yaml
# branding.yaml
theme: "matrix"
matrix_rain: true
matrix_rain_intensity: 0.055
```

---

## Tips per Aziende

✅ **Consigliato per clienti:** Business Modern con colori brand aziendali
✅ **Consigliato per team interno:** Personalizza con colori aziendali
✅ **Consigliato per demo tech:** Matrix con intensità pioggia ridotta (0.03)
✅ **Dark mode:** Business Modern supporta automaticamente preferenza OS

---

**v1.12.2** — Sistema temi introdotto
