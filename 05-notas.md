# 05 — Notas y buenas prácticas

## Ética y legalidad

- El scraper **respeta robots.txt** de Workana: solo lee `/jobs` (páginas públicas), nunca `/api/`, login ni paneles privados
- No envía propuestas ni interactúa con clientes: solo lectura de listados públicos
- Workana es marca de su dueño; este proyecto es independiente y para uso personal/análisis

## Limitaciones

| Límite | Detalle |
|---|---|
| ~9 proyectos por página | Máximo realista del listado |
| Sin login no hay más datos | Nombre completo del cliente, historial, ratings del cliente requieren cuenta |
| HTML puede cambiar | Si Workana rediseña, los selectores (`div.project-item`, `h2.project-title`, etc.) se rompen |
| `budget_min/max` vacíos | Algunos proyectos no publican presupuesto numérico (queda vacío/null) |
| `posted` es texto relativo | "Hace 2 días", "Hace 17 horas" — no fecha exacta |

## Riesgo de bloqueo

Workana usa protección anti-bots (Cloudflare). El scraper ya la evita en gran parte (contexto nuevo por página, pausas de 3 s), pero:

- Evita `--pages` altos (> 15) en una sola corrida
- Si todo da TimeoutError: espera 10-15 minutos y reintenta
- Usa filtros (`--category`, `--country`, `--keyword`) para acotar en vez de scrapear todo
- Entre corridas grandes, deja pasar unas horas

## Mantenimiento

Si un día el scraper devuelve 0 proyectos:

1. Abre `https://www.workana.com/es/jobs` en tu navegador y verifica que el sitio sigue igual
2. Si cambió el diseño, hay que actualizar los selectores CSS en `extract_projects()` (scraper_workana.py). Los clave:
   - `div.project-item` — contenedor de cada proyecto
   - `h2.project-title a` — título y URL
   - `span.bids` — propuestas
   - `div.skills a.skill h3` — skills
   - `p.budget span.values span` — presupuesto
3. F12 en el navegador → inspeccionar un proyecto → ver las clases nuevas

## Ideas para extender

- Programarlo diario con Task Scheduler de Windows (schtask) y acumular CSVs por fecha
- Enriquecer con datos de cada URL de proyecto (página de detalle)
- Unir varias corridas en un solo histórico con pandas y cargar la carpeta completa en Power BI
