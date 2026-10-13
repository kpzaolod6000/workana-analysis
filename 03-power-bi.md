# 03 — Guía de Power BI (desde cero)

> Esta guía usa los **nombres de menú en inglés** (tu Power BI está en inglés).
> Power BI Desktop es gratis y solo funciona en Windows: [descargar aquí](https://www.microsoft.com/es-es/power-platform/products/power-bi/desktop).

## 0. Reconoce dónde estás

Power BI tiene 3 vistas (esquina izquierda, iconos verticales):

1. **Report** — el lienzo donde haces los gráficos (barrita con gráfico)
2. **Table** — los datos en tabla
3. **Model** — relaciones entre tablas

El editor con pestañas **File | Home | Transform | Add Column | View** (donde ves *Column From Examples, Custom Column, Merge Columns, Index Column*) es el **Power Query Editor**: aquí solo se limpian los datos. Tu captura muestra ese panel — es el lugar correcto para los pasos 2 y 3.

## 1. Cargar los datos

1. **Home → Get Data → Text/CSV** → selecciona `workana_projects.csv`
2. En el preview:
   - **File Origin**: elige *65001: Unicode (UTF-8)* (evita caracteres rotos tipo `DiseÃ±o`)
   - Los tipos que detecte no importa, los arreglamos después
3. Clic en **Transform Data** (NO en Load) → abre el Power Query Editor

## 2. Asignar tipos de columna (en Power Query)

Cada encabezado de columna tiene un icono (ABC / 123 / calendario). Clic en el icono → elegimos el tipo:

| Columna | Tipo |
|---|---|
| `bids` | **Whole Number** |
| `budget_min`, `budget_max` | **Decimal Number** |
| `is_hourly`, `payment_verified`, `featured` | **TRUE/FALSE** |
| `country`, `country_code`, `currency`, `title`, `skills`... | **Text** (default) |
| `scraped_at` | **Date/Time** |
| `id` | **Whole Number** |

Alternativa: selecciona la(s) columna(s) y usa la pestaña **Transform** (o la sección *From Number* de Add Column) → *Data Type*.

Notas:
- Si una columna TRUE/FALSE aparece como texto, cámbiala: icono del encabezado → **TRUE/FALSE**
- Si `budget_max` viene vacía en algunas filas es normal (proyecto sin presupuesto); déjalas

## 3. Dividir las skills (clave para ordenar demanda)

La columna `skills` trae varias separadas por `"; "`:

1. Selecciona la columna `skills`
2. Pestaña **Add Column → Split Column → By Delimiter**
3. En el cuadro: Choose delimiter → **--Custom--** → escribe `; ` (punto y coma + espacio)
4. Deja "Left-most delimiter" y **OK**

Se crean columnas `skills.1`, `skills.2`... une: **Home → Close & Apply**. El power query manda todo al lienzo de Report.

## 4. Cargar y visualizar (pestaña Report)

Cierra Power Query con **Home → Close & Apply** (botón superior izquierdo del editor).

De vuelta en **Report view**, usa el panel derecho "**Visualizations**" (clic en un tipo de gráfico) y el panel "**Fields**"/"**Data**" (array con las columnas). Para armar un visual: clic en el gráfico y arrastra los campos a los huecos **X axis**, **Y axis**, **Legend**, **Values**:

| Objetivo | Visual (en Visualizations) | Campos |
|---|---|---|
| ¿De qué países son los clientes? | **Bar chart / Map** | X axis: `country` · Y axis: Count of `id` |
| Skills más pedidas | **Bar chart** | X axis: `skills.1` (o la que uses) · Y axis: Count of `id` |
| Presupuesto fijo vs por hora | **Column chart** | X axis: `is_hourly` · Y axis: Average of `budget_max` |
| Competencia por proyecto | **Scatter chart** | X: `bids` · Y: `budget_max` · Legend: `country` |
| Evolución temporal | **Line chart** | X: `scraped_at` · Y: Count of `id` |

Cuando arrastras un campo a Y axis, clic en él (desplegable) y elige *Count*, *Average*, *Sum*…

## 5. Medidas útiles

En el panel Fields, clic derecho en la tabla → **New measure**:

```dax
Projects = COUNTROWS(workana_projects)

Avg Budget = AVERAGE(workana_projects[budget_max])

Avg Bids = AVERAGE(workana_projects[bids])
```

Si dividiste skills, conviene una tabla aparte: en Power Query, clic derecho sobre la consulta → *Reference*, luego en la copia conserva solo `slug` + `skills` y divídela en filas (**Home → Split... no**, use: Transform → Unpivot no aplica aquí; mejor **Advanced Editor**). Si te complica, empieza solo con `skills.1` de la tabla principal: cubre la skill principal de cada proyecto.

## 6. Actualizar los datos

- El scraper genera el CSV → en Power BI: **Home → Refresh** (relee el archivo)
- Para histórico: guarda cada corrida con fecha (`data_2026-10-07.csv`...) y cárgalas juntas con **Get Data → Folder**

## 7. Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `Column 'X' not found` en un visual | El CSV viejo tenía columnas en español | Regenera el CSV con la versión en inglés del scraper |
| Texto con `Ã©`/`Ã±` | Encoding mal detectado | File Origin = 65001 UTF-8 (paso 1) |
| Un número llega como texto | Tipo mal detectado | Clic en icono del encabezado → Decimal Number |
| No puedo soltar campo en un visual | Elegiste un visual sin ese slot | Borra el visual y elige otro tipo |

> Si ves algo distinto a esta guía (menús reubicados, otra área), mandame el nombre de la pestaña y del botón exacto que ves y ajusto los pasos.
