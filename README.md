# ScrapingWorkana

Scraper de proyectos públicos de Workana (`workana.com/jobs`) para análisis de mercado y visualización en Power BI.

## Documentación

| Archivo | Contenido |
|---|---|
| [01-instalacion.md](01-instalacion.md) | Requisitos y comandos para levantar todo |
| [02-uso-scraper.md](02-uso-scraper.md) | Cómo ejecutar el scraper, filtros y campos de salida |
| [03-power-bi.md](03-power-bi.md) | Guía paso a paso de Power BI (desde cero) |
| [04-playwright.md](04-playwright.md) | ¿Qué es Playwright y por qué es necesario? |
| [05-notas.md](05-notas.md) | Limitaciones, buenas prácticas y solución de problemas |
| [06-dashboard.md](06-dashboard.md) | Dashboard enfocado a estudio fullstack con filtro por categoría |

## Inicio rápido

```powershell
pip install -r requirements.txt
python -m playwright install chromium
python scraper_workana.py --pages 4
```

Genera `workana_projects.csv` (+ copia `.json`) listo para Power BI.
