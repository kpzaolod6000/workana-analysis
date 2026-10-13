# 04 — ¿Qué es Playwright?

## Definición corta

Playwright es una librería de automatización de navegadores creada por Microsoft. Abre un navegador real (Chromium, Firefox o WebKit) y lo controla por código: navegar, hacer clic, esperar, extraer el HTML renderizado.

## Por qué este proyecto lo necesita

Workana carga su lista de proyectos con **JavaScript**: el servidor envía un HTML "vacío" y el navegador completa los proyectos después.

Esto se comprobó en el desarrollo:

- Con `requests` (HTTP simple) el HTML llega **sin ningún proyecto** (0 resultados)
- Con Playwright, el navegador ejecuta el JavaScript, espera a que aparezcan los `div.project-item` y entonces se extraen los datos

```
requests  →  HTML crudo (sin proyectos)  →  ✗
Playwright →  HTML renderizado (con proyectos)  →  ✓
```

## Cómo lo usa el scraper

1. Lanza un Chromium **headless** (invisible, no abre ventana)
2. Va a `https://www.workana.com/jobs?language=es&page=N`
3. Espera a que exista el selector `div.project-item` (los proyectos)
4. Entrega `pg.content()` (el HTML final) a BeautifulSoup para parsearlo
5. Usa un **contexto nuevo por página**: navegar páginas seguidas en la misma pestaña dispara el bloqueo anti-bots de Workana

## Diferencia con BeautifulSoup

No compiten, se complementan:

| Herramienta | Rol |
|---|---|
| **Playwright** | Consigue el HTML renderizado (maneja JavaScript, espera, clics) |
| **BeautifulSoup** | Parsea ese HTML y extrae los campos (título, presupuesto, skills...) |

## Saber más

- [playwright.dev/python](https://playwright.dev/python/) — documentación oficial
- También sirve para testing de aplicaciones web, automatización de formularios, capturas de pantalla y PDFs
