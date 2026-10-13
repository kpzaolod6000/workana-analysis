# 02 — Uso del scraper

## Comandos básicos

```powershell
# 3 páginas (~27 proyectos)
python scraper_workana.py --pages 3

# Con filtros: categoría + país
python scraper_workana.py --pages 5 --category it-programming --country MX

# Por palabra clave (busca en título, descripción y skills)
python scraper_workana.py --pages 2 --keyword python

# Por skill específico
python scraper_workana.py --pages 2 --skill logo-design-1

# Salida con nombre personalizado
python scraper_workana.py --pages 4 --output my_data.csv
```

Cada página contiene ~9 proyectos. La salida es `workana_projects.csv` con una copia espejo `.json` con el mismo nombre, en UTF-8 con BOM (`utf-8-sig`), lista para Excel y Power BI.

> Nota: el código y las columnas de salida están en inglés; el *contenido* extraído (títulos, skills, "Publicado: Hace 2 días") llega en español porque el scraper consulta la interfaz en español de Workana.

## Filtros disponibles

| Filtro | Valores ejemplo |
|---|---|
| `--category` | `it-programming`, `design-multimedia`, `writing-translation`, `sales-marketing`, `admin-support`, `legal`, `finance-management`, `engineering-manufacturing` |
| `--country` | Código de 2 letras: `MX`, `AR`, `CO`, `ES`, `PE`, `US`... |
| `--keyword` | Cualquier palabra (`python`, `shopify`, `marketing`) |
| `--skill` | Slug de skill: `python`, `graphic-design`, `javascript`, `logo-design-1` |
| `--pages` | N° de páginas a recorrer |
| `--output` | Nombre del archivo final (`.csv` o `.json`) |

Los filtros se pueden combinar:

```powershell
python scraper_workana.py --pages 5 --category it-programming --country MX --keyword python
```

## Campos de salida

| Campo | Descripción |
|---|---|
| `id` | Autoincremental (1, 2, 3...) — número de fila de esa corrida |
| `slug` | ID único del proyecto (sirve para deduplicar entre corridas) |
| `title`, `url`, `description` | Datos del proyecto |
| `budget_text` | Texto original ("USD 50 - 100") |
| `budget_min` / `budget_max` | Valores numéricos parseados |
| `currency` | USD / MXN |
| `is_hourly` | TRUE si es tarifa por hora |
| `posted` | Fecha relativa ("Hace 2 días") |
| `bids` | N° de propuestas recibidas |
| `skills` | Skills separadas por "; " |
| `client`, `country`, `country_code` | Cliente que publica |
| `payment_verified`, `featured` | Flags de calidad |
| `category` | Valor del `--category` usado (vacío = todas) — sirve para filtrar en Power BI |
| `scraped_at` | Timestamp de la extracción |

## Comportamiento

- **Deduplicación automática**: si un proyecto ya apareció (mismo `slug`), no se repite en la salida.
- **Detección de fin**: si una página no trae proyectos nuevos, el scraper se detiene.
- **Reintentos**: cada página se intenta hasta 3 veces antes de omitirla.
- **Pausas**: 3 segundos entre páginas para no saturar el sitio.

## Estrategia sugerida para análisis de mercado

Para tener un histórico, ejecuta una vez al día con fecha en el nombre:

```powershell
python scraper_workana.py --pages 5 --output data_2026-10-07.csv
```

Así puedes comparar en Power BI cómo cambian presupuestos, skills y demanda a lo largo del tiempo.
