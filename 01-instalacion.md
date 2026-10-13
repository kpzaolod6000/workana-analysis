# 01 — Instalación

## Requisitos

- **Python 3.10+** (verificado con 3.14)
  - Descargar de [python.org](https://www.python.org/downloads/) si no lo tienes
  - Verificar: `python --version`
- Windows / macOS / Linux (comandos hechos para PowerShell de Windows)

## Pasos

### 1. Instalar dependencias del proyecto

Parado en la carpeta del proyecto (`D:\Project\scrapingWorkana`):

```powershell
pip install -r requirements.txt
```

Instala: `playwright`, `beautifulsoup4`, `pandas`, `lxml`.

### 2. Descargar el navegador de Playwright (solo la primera vez)

```powershell
python -m playwright install chromium
```

Descarga un Chromium (~200 MB) a tu carpeta de usuario. **No** se toca tu Chrome instalado.

### 3. Verificar que todo funciona

```powershell
python scraper_workana.py --pages 1
```

Si termina con "Saved: workana_projects.csv", está listo.

## Problemas comunes

| Error | Solución |
|---|---|
| `python` no se reconoce | Reinstalar Python marcando "Add to PATH", o usar `py` en su lugar |
| `pip` da error de permisos | `pip install --user -r requirements.txt` |
| `playwright` no encontrado | Cerrar y reabrir la terminal tras instalar |
| Timeout al scrapear | Reintentar; Workana a veces bloquea unos minutos (ver [05-notas.md](05-notas.md)) |
