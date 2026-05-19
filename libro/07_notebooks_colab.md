# Capítulo 7 — Notebooks Colab (`.ipynb`)

> Estructura interna de un notebook, mecánica de Google Colab y
> recorrido por las celdas de los tres `colab_0X_*.ipynb`.

---

## 7.1 ¿Qué es un `.ipynb`?

Un archivo `.ipynb` es un **documento JSON** que representa un
*notebook* de Jupyter / Colab. No es código Python directo; es una
estructura de datos que **un kernel** (intérprete) ejecuta celda por
celda.

### Estructura JSON básica

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": ["# Título\n", "Texto descriptivo"]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": ["print('Hola')"]
    }
  ],
  "metadata": {
    "kernelspec": {"display_name": "Python 3", "name": "python3"},
    "language_info": {"name": "python", "version": "3.10"}
  },
  "nbformat": 4,
  "nbformat_minor": 4
}
```

| Campo | Significado |
|---|---|
| `cells` | Lista de celdas. Cada celda tiene `cell_type` (`markdown` o `code`), `source` (lista de líneas) y `metadata`. |
| `execution_count` | Número de orden en que se ejecutó la celda; `null` si nunca se ejecutó. |
| `outputs` | Salida de la última ejecución (texto, tablas, imágenes). |
| `metadata` | Datos del notebook completo: kernel usado, versión de Python. |
| `nbformat`, `nbformat_minor` | Versión del formato `.ipynb`. |

---

## 7.2 Tipos de celda

| Tipo | Propósito |
|---|---|
| **`markdown`** | Texto formateado con Markdown (títulos, listas, énfasis, imágenes, fórmulas LaTeX). |
| **`code`** | Código Python ejecutable. Su salida queda guardada como `outputs`. |
| `raw` | Texto sin procesar (poco usado en el proyecto). |

---

## 7.3 Mecánica de ejecución en Colab

1. Cuando abres un `.ipynb` en Colab, Google levanta una **máquina
   virtual** con Python preinstalado.
2. La VM mantiene un **kernel** persistente: todas las variables que
   defines en una celda quedan disponibles para las siguientes.
3. Las celdas pueden ejecutarse **en cualquier orden**, no
   necesariamente de arriba abajo. Eso permite experimentar.
4. `Runtime → Run all` ejecuta todas las celdas de arriba abajo.

### Notación de Colab

| Sintaxis | Para qué sirve |
|---|---|
| `!comando` | Ejecuta `comando` en el shell del sistema. P. ej. `!pip install scipy`. |
| `%magic` | "Magic command" del notebook. P. ej. `%time fn()` mide el tiempo. |
| `%%cell_magic` | Magic que aplica a toda la celda. P. ej. `%%bash`, `%%capture`. |
| `from google.colab import drive` | Importación específica de Colab para montar Drive. |

---

## 7.4 Estructura común de los tres notebooks

Cada uno de los tres `colab_0X_*.ipynb` tiene la **misma plantilla**:

```
┌──────────────────────────────────────┐
│ Celda 1 (markdown): Título + intro   │
├──────────────────────────────────────┤
│ Celda 2 (markdown): "1. Setup"       │
├──────────────────────────────────────┤
│ Celda 3 (code): Mount Drive          │
├──────────────────────────────────────┤
│ Celda 4 (code): Instalar deps        │
├──────────────────────────────────────┤
│ Celda 5 (markdown): "2. Código"      │
├──────────────────────────────────────┤
│ Celda 6 (code): TODO el código del   │
│                 módulo (constantes + │
│                 funciones)            │
├──────────────────────────────────────┤
│ Celda 7+ (markdown+code): Ejecutar y │
│                  mostrar resultados   │
└──────────────────────────────────────┘
```

---

## 7.5 Celda 3 — Montar Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')

RUTA_PROYECTO = '/content/drive/MyDrive/IA_EDUCACION_SUPERIOR'
print('Ruta del proyecto:', RUTA_PROYECTO)
```

| Línea | Significado |
|---|---|
| `from google.colab import drive` | Importa el submódulo `drive` del paquete `google.colab`. **Sólo existe en Colab.** |
| `drive.mount('/content/drive')` | Pide autorización al usuario y, una vez concedida, hace accesible "Mi unidad" en `/content/drive/MyDrive`. |
| `'/content/drive/MyDrive/IA_EDUCACION_SUPERIOR'` | Ruta en la VM equivalente a `Mi unidad/IA_EDUCACION_SUPERIOR` en Drive. |
| `print(...)` | Confirma visualmente. |

> **Importante:** En la primera ejecución, Colab abre una ventana
> emergente solicitando permisos. Para correr "todo de un tirón" sin
> intervención manual, el usuario debe haber autorizado previamente.

---

## 7.6 Celda 4 — Instalar dependencias

```python
import importlib.util, subprocess, sys
for pkg in ['pandas', 'numpy', 'scipy', 'statsmodels', 'matplotlib', 'seaborn']:
    if importlib.util.find_spec(pkg) is None:
        print(f'Instalando {pkg}...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])
print('Dependencias OK.')
```

| Elemento | Significado |
|---|---|
| `importlib.util.find_spec(pkg)` | Comprueba si `pkg` puede importarse, devolviendo `None` si no. |
| `subprocess.check_call(args)` | Ejecuta un proceso externo. Lanza excepción si falla. |
| `sys.executable` | Ruta del intérprete Python actual. |
| `["-m", "pip", "install", "-q", pkg]` | Invocación de pip: `-m pip` ejecuta el módulo pip; `install -q` modo silencioso. |
| `for pkg in [...]` | Itera sobre la lista de paquetes requeridos. |

> En la práctica Colab ya trae todos estos paquetes; el bloque es
> defensivo.

---

## 7.7 Celda 6 — Código del módulo embebido

Esta celda contiene **el contenido completo** del archivo `.py`
correspondiente, salvo el bloque `if __name__ == "__main__":` y el
`from __future__ import annotations`. Para ahorrar espacio, el código
se inyecta como una sola gran celda.

Lo único que se le agrega es un **preludio** con las constantes y
helpers que normalmente se importarían de `preparar_datos.py`:

```python
# Constantes mínimas embebidas
MODULOS_GENERICOS = [
    'punt_lectura_critica', 'punt_razona_cuant',
    'punt_competen_ciud', 'punt_comuni_escrita', 'punt_ingles',
]
RUTA_DEFECTO = '/content/drive/MyDrive/IA_EDUCACION_SUPERIOR'

def _registrar(msg):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def montar_drive_si_aplica(p='/content/drive'):
    try:
        from google.colab import drive
        import os
        if not os.path.ismount(p):
            drive.mount(p, force_remount=False)
        return True
    except ImportError:
        return False
```

| Razón del preludio | Explicación |
|---|---|
| Notebooks autocontenidos | No dependen de que `preparar_datos.py` esté en `sys.path`. |
| Mismas constantes que el `.py` | Garantizan resultados idénticos. |
| `_registrar` reimplementado | Igual que en `preparar_datos.py` (Cap. 3, §3.4). |

---

## 7.8 Celdas 7+ — Ejecutar y mostrar

### Patrón general

```python
# Ejecutar
resultado = ejecutar_funcion()

# Mostrar tablas
resultado["tabla3"]      # se renderiza como tabla bonita en Colab

# Mostrar figuras
from IPython.display import Image, display
import os
dir_figs = os.path.join(RUTA_PROYECTO, 'procesados', 'figuras')
for f in ['fig_01_...', 'fig_02_...']:
    ruta = os.path.join(dir_figs, f)
    if os.path.exists(ruta):
        display(Image(ruta))
```

| Elemento | Significado |
|---|---|
| Última línea sin `print` | Colab renderiza automáticamente el último valor de la celda. Para DataFrames muestra una tabla con scroll y filtro. |
| `from IPython.display import Image, display` | Utilidades de IPython para mostrar imágenes inline. |
| `Image(ruta)` | Construye un objeto imagen. |
| `display(...)` | Lo renderiza como salida de la celda. |
| `os.path.exists(ruta)` | Defensivo: sólo muestra si la figura existe. |

---

## 7.9 Recorrido por `colab_01_preparar_datos.ipynb`

| Celda | Contenido | Detalle |
|---|---|---|
| 1 | md título | "Parte 0 — Preparación de datos Saber Pro 2021-2024" |
| 2 | md "## 1. Setup" | Sección |
| 3 | code | `drive.mount(...)` |
| 4 | code | Instalación defensiva de deps |
| 5 | md "## 2. Código del pipeline" | Sección |
| 6 | code | **Todo `preparar_datos.py`** embebido |
| 7 | md "## 3. Ejecutar el pipeline" | Sección |
| 8 | code | `dfs_anio, df_consolidado = ejecutar_pipeline()` |
| 9 | md "## 4. Resumen rápido" | Sección |
| 10 | code | `df_consolidado.groupby('periodo_ia')[...]` |
| 11 | code | `df_consolidado['departamento_nombre'].value_counts()` |

### Resultado al finalizar

En `Mi unidad/IA_EDUCACION_SUPERIOR/procesados/` aparecen:
- `df_2021.csv`, `df_2022.csv`, `df_2023.csv`, `df_2024.csv`
- `df_consolidado.csv`

---

## 7.10 Recorrido por `colab_02_analisis_descriptivo.ipynb`

| Celda | Contenido |
|---|---|
| 1 | md título + intro |
| 2 | md "## 1. Setup" |
| 3 | code: `drive.mount` |
| 4 | code: instalación de deps |
| 5 | md "## 2. Código del análisis descriptivo" |
| 6 | code: **todo `analisis_descriptivo.py`** embebido + preludio |
| 7 | md "## 3. Ejecutar el análisis" |
| 8 | code: `resultado = ejecutar_analisis_descriptivo()` |
| 9 | md "## 4. Tabla 3 — Comparación entre cohortes" |
| 10 | code: `tabla3` (se renderiza como tabla bonita) |
| 11 | md "## 5. Tabla descriptiva por departamento" |
| 12 | code: `tabla_dpto` |
| 13 | md "## 6. Figuras" |
| 14 | code: bucle que muestra las 6 figuras inline |

---

## 7.11 Recorrido por `colab_03_regresion_mco.ipynb`

| Celda | Contenido |
|---|---|
| 1 | md título + intro |
| 2 | md "## 1. Setup" |
| 3 | code: mount Drive |
| 4 | code: instalación deps |
| 5 | md "## 2. Código de la regresión" |
| 6 | code: **todo `regresion_mco.py`** + preludio con `DEPARTAMENTOS` y helpers |
| 7 | md "## 3. Ejecutar la regresión" |
| 8 | code: `res = ejecutar_regresion()` |
| 9 | md "## 4. β_IA con corrección por pruebas múltiples" |
| 10 | code: `beta_ia` |
| 11 | md "## 5. Triángulo de colinealidad geográfica" |
| 12 | code: `colin` |
| 13 | md "## 6. Diagnósticos por modelo" |
| 14 | code: `diag` |
| 15 | md "## 7. Tabla 4 — coeficientes (vista filtrada a β_IA)" |
| 16 | code: `tabla4[tabla4['termino'] == 'periodo_ia']` |
| 17 | md "## 8. Figuras de la regresión" |
| 18 | code: muestra `fig_07_forest_beta_ia.png` y `fig_08_coef_departamento.png` |

---

## 7.12 Cómo se conectan los tres notebooks

```
       ┌─────────────────────────────┐
       │ colab_01_preparar_datos     │
       │ (genera df_consolidado.csv) │
       └──────────────┬──────────────┘
                      │ escribe en
                      ▼
       /…/procesados/df_consolidado.csv
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌──────────────────┐   ┌──────────────────────┐
│ colab_02_descrip │   │ colab_03_regresion   │
│ (Parte 1)        │   │ (Parte 2)            │
└──────────────────┘   └──────────────────────┘
```

Los tres notebooks comparten estado **a través del disco**: el primero
escribe `df_consolidado.csv` en Drive y los otros dos lo leen. Esto los
hace **independientes**: puedes correr el 2 y el 3 sin volver a correr
el 1 (mientras el `df_consolidado.csv` siga en su sitio).

---

## 7.13 Trucos prácticos en Colab

### Ver una sola celda de salida grande

```python
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 50)
tabla4
```

### Descargar un archivo generado a tu computador

```python
from google.colab import files
files.download('/content/drive/MyDrive/IA_EDUCACION_SUPERIOR/procesados/df_consolidado.csv')
```

### Subir un archivo desde tu computador

```python
from google.colab import files
uploaded = files.upload()    # abre un selector de archivos
```

### Reiniciar el kernel

`Runtime → Restart runtime`. Vuelve a importar y re-ejecutar todo.

### Liberar memoria

```python
import gc
del df_grande
gc.collect()
```

---

## 7.14 Recapitulación

Al terminar este capítulo deberías poder:

1. Explicar la **estructura JSON** de un `.ipynb`.
2. Distinguir celdas **markdown** y **code**.
3. Saber cómo se **monta Google Drive** desde Colab.
4. Recorrer los tres notebooks del proyecto sabiendo qué hace cada
   celda.
5. Conectar las salidas del primer notebook con los inputs de los
   otros dos.

Pasa al [Capítulo 8 — Glosario alfabético](./08_glosario.md) para
encontrar definiciones de cualquier término del proyecto.
