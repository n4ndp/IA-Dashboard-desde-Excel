# Ideas y Snippets — Excel AI Dashboard

Archivo de referencia personal. Ideas sueltas, fragmentos de código útiles,
decisiones técnicas y cosas a explorar durante el desarrollo.


## 🐼 Pandas para procesar el Excel

La idea principal es usar pandas como capa intermedia entre el archivo Excel crudo
y la base de datos. En vez de leer celda por celda, pandas convierte cada hoja en
un DataFrame — una estructura tabular que ya te da tipos inferidos, permite filtrar,
limpiar y serializar fácilmente.

```python
import pandas as pd
from io import BytesIO

# Leer todas las hojas de un Excel en memoria
xl = pd.ExcelFile(BytesIO(file_bytes))

# Iterar sobre cada hoja
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    print(df.dtypes)       # ver tipos inferidos por pandas
    print(df.to_dict(orient='records'))  # convertir a lista de dicts (filas)
```


## 🔍 Inferencia de tipos con pandas

Pandas ya detecta algunos tipos automáticamente. La idea es mapear esos tipos
a solo 3 categorías propias: `string`, `number`, `date`.

```python
import pandas as pd

def infer_type(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    if pd.api.types.is_numeric_dtype(series):
        return "number"
    # Intentar parsear como fecha si viene como string
    try:
        pd.to_datetime(series.dropna(), errors="raise")
        return "date"
    except:
        pass
    # Intentar parsear como número si viene como string
    try:
        pd.to_numeric(series.dropna(), errors="raise")
        return "number"
    except:
        pass
    return "string"  # fallback siempre seguro
```


## 🤖 Idea: Agente IA que genera el layout del dashboard

En vez de hardcodear qué gráficos mostrar, pasarle a Gemini la metadata
de las columnas y que él decida qué widgets renderizar y en qué posición.

## 🏗️ Idea: GridStack para layout drag-and-drop

Usar GridStack para que los widgets sean reposicionables en el dashboard.
Cada widget tiene `x`, `y`, `w`, `h` que vienen del JSON del agente.

```bash
npm install gridstack
```

```javascript
import { GridStack } from 'gridstack'

const grid = GridStack.init()

widgets.forEach(w => {
  grid.addWidget({
    x: w.x, y: w.y, w: w.w, h: w.h,
    content: `<div id="widget-${w.id}"></div>`
  })
})
```
