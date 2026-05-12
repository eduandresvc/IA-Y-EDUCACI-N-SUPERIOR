# Explicación línea a línea del código
## Notebook: `analisis_departamentos_colombia.ipynb`

Este documento explica en detalle qué hace cada línea de código del notebook, qué significa cada función, cada parámetro y cada decisión de programación. Está escrito para ser leído sin conocimientos previos de Python.

---

## Tabla de contenido

- [Celda 1 — Librerías](#celda-1--librerías)
- [Celda 2 — Configuración](#celda-2--configuración)
- [Celda 3 — Carga de archivos](#celda-3--carga-de-archivos)
- [Celda 4 — DataFrames individuales](#celda-4--dataframes-individuales)
- [Celda 5 — Selector de columnas](#celda-5--selector-de-columnas-widget-interactivo)
- [Celda 6 — Unión de DataFrames](#celda-6--unión-de-los-4-dataframes)
- [Celda 7 — Variables nuevas](#celda-7--creación-de-variables-nuevas)
- [Celda 8 — Exclusión de Bogotá D.C.](#celda-8--exclusión-de-bogotá-dc)
- [Celda 9 — Estadística descriptiva](#celda-9--estadística-descriptiva)
- [Celda 10 — Visualizaciones](#celda-10--visualizaciones)
- [Celda 11 — Exportar](#celda-11--exportar)

---

---

## Celda 1 — Librerías

```python
!pip install ipywidgets -q
```
El signo `!` al inicio de una línea en Colab le indica al sistema que ejecute un **comando de terminal**, no código Python. `pip install` es el instalador de paquetes de Python. `ipywidgets` es la librería que permite crear los botones y el selector interactivo de columnas. El parámetro `-q` significa *quiet* (silencioso): instala sin imprimir mensajes innecesarios en pantalla.

---

```python
import pandas as pd
```
`import` carga una librería para poder usarla. **pandas** es la herramienta central para trabajar con tablas de datos en Python (equivalente a Excel pero programático). `as pd` es un alias: en lugar de escribir `pandas.algo` cada vez, se escribe `pd.algo`, que es más corto.

---

```python
import numpy as np
```
**numpy** (abreviado `np`) provee funciones matemáticas y el valor especial `np.nan`. `NaN` significa *Not a Number* y se usa para representar datos vacíos o ausentes — en este proyecto se asigna `NaN` a Bogotá D.C. para luego poder filtrarla fácilmente.

---

```python
import matplotlib.pyplot as plt
```
**matplotlib** es la librería de gráficos de Python. `pyplot` es su módulo principal para crear figuras. Se abrevia como `plt`.

---

```python
import seaborn as sns
```
**seaborn** complementa a matplotlib con estilos más modernos y algunas funciones estadísticas visuales de alto nivel. Se abrevia `sns`.

---

```python
import ipywidgets as widgets
```
**ipywidgets** permite crear elementos interactivos dentro de Colab: botones, listas desplegables, selectores múltiples, etc. Se abrevia `widgets`.

---

```python
import io, warnings
```
Importa dos módulos en una sola línea (separados por coma). **io** permite leer archivos desde memoria en lugar de desde disco — necesario porque los archivos subidos a Colab llegan como bytes en memoria, no como archivos guardados. **warnings** controla los mensajes de advertencia que Python puede mostrar.

---

```python
from google.colab import files
```
`from ... import ...` importa solo una parte específica de una librería. **google.colab** es el módulo propio de Google Colab. `files` es el objeto que permite subir y descargar archivos desde y hacia la computadora del usuario.

---

```python
from IPython.display import display, HTML
```
**IPython** es el motor que ejecuta el código en Colab. `display` es una función que muestra objetos (tablas, widgets, imágenes) directamente en la salida de la celda. `HTML` permite renderizar código HTML si fuera necesario.

---

```python
warnings.filterwarnings('ignore')
```
Le dice a Python que no muestre advertencias durante la ejecución. Sin esta línea, pandas y otras librerías imprimirían mensajes como *"DtypeWarning: Mixed types"* que no son errores pero sí ruido visual.

---

```python
sns.set_theme(style='whitegrid', palette='muted')
```
Establece el estilo visual de todos los gráficos del notebook. `style='whitegrid'` aplica fondo blanco con líneas grises de referencia. `palette='muted'` usa una paleta de colores suaves y profesionales. Esta línea afecta a todas las figuras que se creen después.

---

```python
print('✓ Librerías cargadas')
```
`print()` muestra un mensaje en la salida de la celda. Es una confirmación visual para el usuario de que todo se cargó correctamente.

---

---

## Celda 2 — Configuración

```python
COLUMNA_DEPARTAMENTO = 'ESTU_COD_DEPTO_PRESENTACION'
```
Crea una **variable de configuración** que almacena el nombre de la columna del departamento tal como aparece en los archivos CSV. Escribirla aquí una sola vez significa que si el nombre cambia, solo hay que editarlo en este lugar y el resto del código lo usa automáticamente. Por convención, las variables de configuración se escriben en MAYÚSCULAS.

---

```python
COLUMNA_RESULTADO = 'MOD_RAZONA_CUANTITAT_PUNT'
```
Igual que la anterior, guarda el nombre de la columna que contiene el puntaje del examen. Ambas variables son el único punto de personalización obligatoria del notebook.

---

```python
print(f'Columna departamento : {COLUMNA_DEPARTAMENTO}')
print(f'Columna resultado    : {COLUMNA_RESULTADO}')
```
Las `f-strings` (cadenas que empiezan con `f` antes de las comillas) permiten incrustar el valor de una variable dentro del texto usando llaves `{}`. Esto imprime los nombres configurados para confirmar visualmente que están correctos antes de continuar.

---

---

## Celda 3 — Carga de archivos

```python
print('📂 Seleccione y suba sus 4 archivos CSV (orden: 2021, 2022, 2023, 2024)')
print('-' * 60)
```
El segundo `print` usa el operador `*` para repetir el carácter `-` 60 veces, creando una línea divisoria visual en la salida. Es solo decorativo.

---

```python
uploaded = files.upload()
```
Llama a la función `upload()` del módulo `files` de Colab. Esto **detiene la ejecución** y muestra el botón *"Elegir archivos"* en pantalla. Cuando el usuario selecciona y confirma los archivos, `upload()` devuelve un **diccionario** donde cada llave es el nombre del archivo y cada valor son los bytes del contenido de ese archivo. El resultado se guarda en la variable `uploaded`.

---

```python
archivos = list(uploaded.keys())
```
`.keys()` extrae solo las llaves del diccionario (los nombres de los archivos). `list()` convierte esas llaves en una lista ordenada. Así `archivos` queda como, por ejemplo, `['datos_2021.csv', 'datos_2022.csv', ...]`.

---

```python
for i, nombre in enumerate(archivos):
    print(f'   {i+1}. {nombre}')
```
`for ... in ...` es un **bucle** que recorre elementos uno por uno. `enumerate()` entrega a la vez el índice (posición) y el valor de cada elemento. Así `i` es el número de posición (0, 1, 2, 3) y `nombre` es el nombre del archivo. Se suma `i+1` para que la numeración empiece en 1 en lugar de 0.

---

```python
if len(archivos) < 4:
    print(f'\n⚠ Se esperaban 4 archivos, se cargaron {len(archivos)}.')
```
`if` ejecuta el bloque siguiente solo si la condición es verdadera. `len()` cuenta la cantidad de elementos de una lista. Si se subieron menos de 4 archivos, muestra una advertencia. El `\n` dentro del texto es un salto de línea.

---

---

## Celda 4 — DataFrames individuales

```python
años_orden = [2021, 2022, 2023, 2024]
```
Una **lista** que establece a qué año corresponde cada posición de carga. El primer archivo subido se asocia al año `2021`, el segundo a `2022`, y así sucesivamente.

---

```python
def leer_csv(contenido):
    for enc in ['utf-8', 'latin1', 'utf-8-sig', 'cp1252']:
        try:
            return pd.read_csv(io.BytesIO(contenido), low_memory=False, encoding=enc)
        except Exception:
            pass
    raise ValueError('No se pudo leer el archivo con ninguna codificación conocida.')
```
`def` define una función reutilizable llamada `leer_csv` que recibe el contenido de un archivo como parámetro.

- **¿Por qué el bucle de codificaciones?** Los archivos CSV colombianos pueden estar guardados en distintos sistemas de caracteres (codificaciones). `utf-8` es el estándar moderno. `latin1` y `cp1252` son comunes en sistemas Windows más antiguos. Si se usa la codificación equivocada, las tildes y la ñ se ven como símbolos extraños. El bucle prueba cada una en orden hasta que una funcione.
- `try / except` es un bloque de manejo de errores: si `pd.read_csv(...)` falla (lanza una excepción), `except Exception: pass` simplemente ignora el error y pasa a intentar la siguiente codificación.
- `io.BytesIO(contenido)` convierte los bytes del archivo cargado en memoria en un "archivo virtual" que `pd.read_csv` puede leer como si fuera un archivo real en disco.
- `low_memory=False` le indica a pandas que lea toda la columna antes de decidir su tipo de dato, evitando errores en archivos con columnas de tipo mixto.
- `raise ValueError(...)` al final: si ninguna codificación funcionó, lanza un error descriptivo en lugar de fallar silenciosamente.

---

```python
dataframes = {}
```
Crea un **diccionario vacío** que se irá llenando. La idea es almacenar cada DataFrame con el año como llave: `{2021: df_2021, 2022: df_2022, ...}`.

---

```python
for i, archivo in enumerate(archivos):
    año = años_orden[i] if i < len(años_orden) else 9000 + i
```
Bucle que recorre cada archivo cargado. La línea del año usa una **expresión condicional en línea** (ternario): si `i` es menor que la cantidad de años definidos, toma el año de la lista; si no (caso en que se subieran más de 4 archivos), asigna un número arbitrario de respaldo (9001, 9002, ...) para no romper el código.

---

```python
    df = leer_csv(uploaded[archivo])
```
Llama a la función definida arriba pasándole el contenido del archivo (`uploaded[archivo]` accede a los bytes del CSV por su nombre). El resultado, una tabla pandas, se guarda en `df`.

---

```python
    df['AÑO'] = año
```
Crea una nueva columna llamada `'AÑO'` en la tabla y la llena con el valor `año` (2021, 2022, etc.) en **todas las filas**. Así, al unir los cuatro archivos, siempre se sabrá de qué año proviene cada registro.

---

```python
    dataframes[año] = df
    print(f'✓ df_{año}: {df.shape[0]:>8,} filas × {df.shape[1]:>4} columnas  ← {archivo}')
```
Guarda el DataFrame en el diccionario con el año como llave. En el `print`, `df.shape` es una tupla `(filas, columnas)`. El formato `{valor:>8,}` significa: alinear a la derecha (`>8`) y usar separador de miles (`,`). Así los números quedan visualmente alineados en la salida.

---

```python
df_2021 = dataframes.get(2021)
df_2022 = dataframes.get(2022)
df_2023 = dataframes.get(2023)
df_2024 = dataframes.get(2024)
```
`.get(llave)` extrae el valor del diccionario para esa llave. Estas líneas crean variables individuales con nombres descriptivos (`df_2021`, etc.) para que el usuario pueda explorarlas directamente si lo necesita. Si algún año no fue cargado, `.get()` devuelve `None` en lugar de lanzar un error.

---

---

## Celda 5 — Selector de columnas (widget interactivo)

```python
df_ref = list(dataframes.values())[0]
todas_las_columnas = [c for c in df_ref.columns if c != 'AÑO']
```
`dataframes.values()` extrae todos los DataFrames del diccionario. `[0]` toma el primero como referencia para obtener la lista de columnas disponibles. La segunda línea usa una **comprensión de lista**: recorre todas las columnas del DataFrame de referencia y las incluye en la lista, excepto `'AÑO'` (que se agrega siempre automáticamente después).

---

```python
selector = widgets.SelectMultiple(
    options=todas_las_columnas,
    value=todas_las_columnas,
    description='Columnas:',
    layout=widgets.Layout(width='90%', height='280px'),
    style={'description_width': 'initial'}
)
```
Crea un **widget de selección múltiple** — una lista visual donde el usuario puede marcar varias opciones a la vez con Ctrl+Click.
- `options`: las opciones disponibles para seleccionar (todas las columnas).
- `value`: cuáles están seleccionadas al inicio (todas, por defecto).
- `description`: etiqueta que aparece a la izquierda del widget.
- `layout`: controla el tamaño visual del widget en pantalla.
- `style={'description_width': 'initial'}`: permite que la etiqueta ocupe el ancho que necesite sin truncarse.

---

```python
btn_todas   = widgets.Button(description='Conservar TODAS',  button_style='info',    icon='check')
btn_minimas = widgets.Button(description='Solo mínimas',     button_style='warning', icon='minus')
btn_ok      = widgets.Button(description='✔ Confirmar',      button_style='success')
```
Crea tres botones. `description` es el texto visible en el botón. `button_style` define el color: `'info'` es azul, `'warning'` es naranja, `'success'` es verde. `icon` agrega un ícono de Font Awesome al botón.

---

```python
output_msg = widgets.Output()
```
Crea un **área de salida** especial. Cuando se quiere imprimir algo dentro de un widget (en respuesta a un clic de botón), se usa este objeto en lugar del `print` normal, para que el mensaje aparezca en el lugar correcto de la interfaz.

---

```python
estado = {'columnas': list(todas_las_columnas)}
```
Un diccionario que actúa como **variable compartida** entre las tres funciones de botón. Como Python no permite que las funciones internas modifiquen variables externas directamente (en versiones anteriores), se usa un diccionario como intermediario. La llave `'columnas'` guarda la selección actual.

---

```python
def _btn_todas(b):
    selector.value = tuple(todas_las_columnas)
    with output_msg:
        output_msg.clear_output()
        print(f'✓ Se conservarán TODAS las {len(todas_las_columnas)} columnas')
```
Función que se ejecuta cuando el usuario hace clic en "Conservar TODAS".
- `b` es el objeto del botón (parámetro obligatorio aunque no se use).
- `selector.value = tuple(...)` selecciona todas las columnas en el widget visualmente. Usa `tuple()` porque el widget requiere que el valor sea una tupla, no una lista.
- `with output_msg:` abre el área de salida del widget para que el `print` aparezca ahí.
- `output_msg.clear_output()` borra el mensaje anterior antes de escribir el nuevo.

---

```python
def _btn_minimas(b):
    cols_min = [c for c in [COLUMNA_DEPARTAMENTO, COLUMNA_RESULTADO] if c in todas_las_columnas]
    selector.value = tuple(cols_min)
```
Función del botón "Solo mínimas". Construye una lista con solo las dos columnas esenciales (departamento y resultado) — pero solo si existen en el CSV, por eso el `if c in todas_las_columnas`. Luego las selecciona en el widget.

---

```python
def _btn_ok(b):
    sel = list(selector.value) if selector.value else list(todas_las_columnas)
    for req in [COLUMNA_DEPARTAMENTO, COLUMNA_RESULTADO]:
        if req in todas_las_columnas and req not in sel:
            sel.append(req)
    estado['columnas'] = sel
```
Función del botón "Confirmar".
- `list(selector.value)` convierte la selección actual del widget (que es una tupla) a lista. Si el usuario no seleccionó nada, se usan todas las columnas.
- El bucle `for req in [...]` garantiza que las columnas imprescindibles (departamento y resultado) siempre estén incluidas, aunque el usuario no las haya marcado.
- `estado['columnas'] = sel` guarda la selección final en el diccionario compartido para que la Celda 6 pueda leerla.

---

```python
btn_todas.on_click(_btn_todas)
btn_minimas.on_click(_btn_minimas)
btn_ok.on_click(_btn_ok)
```
**Registra** qué función debe ejecutarse cuando se hace clic en cada botón. `.on_click()` es un "escuchador de eventos": vigila el botón y, cada vez que es pulsado, llama a la función indicada.

---

```python
display(widgets.VBox([
    widgets.HBox([btn_todas, btn_minimas, btn_ok]),
    selector,
    output_msg
]))
```
`display()` renderiza el widget en la salida de la celda. `VBox` (Vertical Box) apila elementos uno encima del otro. `HBox` (Horizontal Box) los coloca uno al lado del otro. La estructura es: los tres botones en fila horizontal, debajo el selector de columnas, debajo el área de mensajes.

---

---

## Celda 6 — Unión de los 4 DataFrames

```python
cols_keep = estado['columnas'] + ['AÑO']
```
Lee la selección de columnas guardada por el widget en la Celda 5 y le agrega `'AÑO'` al final. El operador `+` entre dos listas las concatena (une).

---

```python
def filtrar(df, cols):
    return df[[c for c in cols if c in df.columns]].copy()
```
Función auxiliar que filtra un DataFrame para conservar solo las columnas deseadas. La comprensión de lista `[c for c in cols if c in df.columns]` evita un error si alguna columna de la lista no existe en ese DataFrame particular (por ejemplo, si un año tiene una columna menos). `.copy()` crea una copia independiente del DataFrame filtrado para evitar el *SettingWithCopyWarning* de pandas al modificar datos después.

---

```python
piezas = [filtrar(df, cols_keep) for df in dataframes.values()]
```
Aplica la función `filtrar` a cada uno de los cuatro DataFrames almacenados en el diccionario, produciendo una lista de cuatro DataFrames ya filtrados.

---

```python
df_total = pd.concat(piezas, ignore_index=True)
```
`pd.concat()` apila verticalmente (uno debajo del otro) todos los DataFrames de la lista `piezas`. El parámetro `ignore_index=True` reinicia el índice de fila (numeración de filas) desde 0 en el DataFrame resultante, en lugar de conservar los índices originales de cada año (lo que causaría índices duplicados).

---

```python
df_total.head(3)
```
`.head(n)` muestra las primeras `n` filas de la tabla. En Colab, cuando la última línea de una celda es un DataFrame, lo renderiza como tabla HTML estilizada de forma automática. Se usa para inspeccionar visualmente que la unión quedó correcta.

---

---

## Celda 7 — Creación de variables nuevas

### Sección 7.1 — DUMMY_POST

```python
df_total['DUMMY_POST'] = df_total['AÑO'].apply(lambda x: 0 if x in [2021, 2022] else 1)
```
Crea la columna `DUMMY_POST` operando sobre la columna `AÑO` ya existente.

- `df_total['AÑO']` accede a la columna `AÑO` del DataFrame.
- `.apply()` aplica una función a cada valor de esa columna, uno por uno.
- `lambda x: 0 if x in [2021, 2022] else 1` es una **función anónima** (lambda). Lee: "dado un valor `x`, devuelve 0 si `x` está en la lista `[2021, 2022]`, de lo contrario devuelve 1". El resultado (0 o 1) se almacena en la nueva columna `DUMMY_POST`.

---

```python
print(df_total['DUMMY_POST'].value_counts().rename(index={0: 'Pre  (2021-2022)', 1: 'Post (2023-2024)'}).to_string())
```
- `.value_counts()` cuenta cuántas veces aparece cada valor único en la columna (cuántos registros tienen `DUMMY_POST = 0` y cuántos tienen `1`).
- `.rename(index={...})` cambia las etiquetas de las filas del resultado para hacerlas más legibles.
- `.to_string()` convierte la tabla a texto plano para que `print` la muestre correctamente.

---

### Sección 7.2 — NUM_DEPTO

```python
MAPA_DANE = {
     91: 1,   #  1 Amazonas
      5: 2,   #  2 Antioquia
     ...
     11: np.nan,  # Bogotá D.C. — EXCLUIDO
}
```
Un **diccionario de traducción** que convierte el código DANE oficial de cada departamento al número 1–32 del análisis. La llave es el código DANE (número oficial del DANE) y el valor es el número asignado en este estudio. Bogotá D.C. tiene código DANE `11` y recibe `np.nan` para indicar que debe excluirse.

---

```python
MAPA_NOMBRE = {
    'AMAZONAS': 1, 'ANTIOQUIA': 2, ...
    'BOGOTA': np.nan, 'BOGOTÁ': np.nan, 'BOGOTA D.C.': np.nan, ...
}
```
El mismo diccionario de traducción pero usando los nombres en texto. Se incluyen múltiples variantes del mismo departamento (con y sin tildes, con y sin siglas) para manejar inconsistencias en los datos originales.

---

```python
col = df_total[COLUMNA_DEPARTAMENTO]
if pd.api.types.is_numeric_dtype(col):
    df_total['NUM_DEPTO'] = col.map(MAPA_DANE)
    tipo_mapa = 'código DANE numérico'
else:
    ...
    df_total['NUM_DEPTO'] = col_norm.map(MAPA_NOMBRE)
```
`pd.api.types.is_numeric_dtype()` detecta si la columna contiene números o texto. Según el resultado usa el diccionario apropiado (`MAPA_DANE` para números, `MAPA_NOMBRE` para texto). `.map(diccionario)` reemplaza cada valor de la columna por el valor correspondiente en el diccionario; si no encuentra el valor, pone `NaN`.

---

```python
col_norm = (col.astype(str).str.upper().str.strip()
               .str.replace('[ÁÀÂÄ]', 'Á', regex=True)
               ...)
```
Cadena de transformaciones para normalizar el texto antes del mapeo:
- `.astype(str)` convierte cualquier valor a texto (por si hay números mezclados).
- `.str.upper()` convierte todo a mayúsculas (`'antioquia'` → `'ANTIOQUIA'`).
- `.str.strip()` elimina espacios en blanco al inicio y al final.
- `.str.replace('[ÁÀÂÄ]', 'Á', regex=True)` usa una **expresión regular** para reemplazar cualquier variante de la letra A con acento por la forma estándar. El patrón entre `[]` es una clase de caracteres: "reemplaza cualquiera de estos caracteres".

---

### Sección 7.3 — DIST_BOGOTA_KM

```python
DIST_BOGOTA = {
     1: 1500,  #  1 Amazonas    — Leticia
     2:  415,  #  2 Antioquia   — Medellín
     ...
}
df_total['DIST_BOGOTA_KM'] = df_total['NUM_DEPTO'].map(DIST_BOGOTA)
```
Otro diccionario de traducción, ahora de número de departamento a kilómetros. `.map()` lo aplica igual que antes: busca el número del departamento en el diccionario y pone la distancia correspondiente en cada fila.

---

### Sección 7.4 — PROM_RESULTADO_DEPTO

```python
df_total['PROM_RESULTADO_DEPTO'] = (
    df_total.groupby(COLUMNA_DEPARTAMENTO)[COLUMNA_RESULTADO]
            .transform('mean')
)
```
Esta es la línea más sofisticada del notebook. Se descompone así:

- `df_total.groupby(COLUMNA_DEPARTAMENTO)` agrupa las filas del DataFrame según los valores únicos del departamento — forma internamente un grupo por cada departamento.
- `[COLUMNA_RESULTADO]` selecciona la columna de puntajes dentro de esos grupos.
- `.transform('mean')` calcula la media de cada grupo y **devuelve un valor por cada fila original** (no una fila por grupo como haría `.agg()`). Es decir, si Antioquia tiene 5 000 registros, a todos les asigna la misma media de Antioquia.

La diferencia clave entre `.transform()` y `.agg()` es que `.transform()` mantiene la misma longitud que el DataFrame original, lo que permite asignar el resultado directamente como nueva columna.

---

### Tabla de resumen de variables

```python
print(f'{"Variable":<25} {"No nulos":>12} {"Nulos":>10}')
```
Los formatos `:<25` y `:>12` controlan la alineación y el ancho del texto. `:<25` alinea el texto a la **izquierda** en un campo de 25 caracteres. `:>12` alinea a la **derecha** en 12 caracteres. Esto hace que los valores queden en columnas perfectamente alineadas.

---

```python
for v in ['DUMMY_POST', 'NUM_DEPTO', 'DIST_BOGOTA_KM', 'PROM_RESULTADO_DEPTO']:
    nn = df_total[v].notna().sum()
    nl = df_total[v].isna().sum()
```
- `.notna()` devuelve `True` por cada fila donde el valor **no** es `NaN` y `False` donde sí lo es.
- `.isna()` es lo opuesto: `True` donde el valor **es** `NaN`.
- `.sum()` suma los `True` (que Python cuenta como 1) para obtener el conteo total.

---

---

## Celda 8 — Exclusión de Bogotá D.C.

```python
n_antes = len(df_total)
```
`len()` cuenta el número de filas. Se guarda antes de la eliminación para poder calcular cuántos registros se eliminaron.

---

```python
df_total = df_total[df_total['NUM_DEPTO'].notna()].copy()
```
Este es el filtro que elimina Bogotá D.C. Se lee: "conservar solo las filas donde `NUM_DEPTO` NO es `NaN`". Como Bogotá D.C. fue mapeada a `NaN` en la Celda 7, esta línea la elimina. También elimina cualquier registro de departamento que no se haya podido mapear. `.copy()` asegura que `df_total` sea un DataFrame independiente.

---

```python
df_total['NUM_DEPTO'] = df_total['NUM_DEPTO'].astype(int)
```
Después de eliminar los `NaN`, la columna `NUM_DEPTO` puede convertirse de número decimal (`1.0`, `2.0`, ...) a entero (`1`, `2`, ...). Esto es necesario porque pandas representa columnas con `NaN` como decimales (`float64`), y al remover los nulos ya es posible usar enteros.

---

```python
NOMBRES_DEPTO = {
     1: 'Amazonas',  2: 'Antioquia', ...
}
df_total['NOMBRE_DEPTO'] = df_total['NUM_DEPTO'].map(NOMBRES_DEPTO)
```
Crea una columna auxiliar con el nombre del departamento en español, útil para etiquetar gráficos y tablas de resultados.

---

```python
ref = pd.DataFrame([
    {'Num': k, 'Departamento': NOMBRES_DEPTO[k], 'Capital': cap, 'Dist_Bogotá_km': DIST_BOGOTA[k]}
    for k, cap in [
        (1,'Leticia'),(2,'Medellín'), ...
    ]
]).set_index('Num')
display(ref)
```
Construye una tabla de referencia a partir de una **lista de diccionarios**. Cada diccionario `{...}` representa una fila con sus campos. `pd.DataFrame([...])` convierte esa lista en una tabla. `.set_index('Num')` usa la columna `Num` como índice de filas en lugar del índice numérico por defecto.

---

---

## Celda 9 — Estadística descriptiva

```python
vars_analisis = [COLUMNA_RESULTADO, 'DUMMY_POST', 'NUM_DEPTO',
                 'DIST_BOGOTA_KM', 'PROM_RESULTADO_DEPTO']
vars_ok = [v for v in vars_analisis if v in df_total.columns]
```
La segunda línea filtra la lista para conservar solo las variables que realmente existen en el DataFrame. Esto protege contra errores si alguna columna no fue creada por algún motivo.

---

```python
display(df_total[vars_ok].describe().round(3))
```
- `df_total[vars_ok]` selecciona solo las columnas de interés.
- `.describe()` calcula automáticamente ocho estadísticos para cada columna numérica: conteo (`count`), media (`mean`), desviación estándar (`std`), mínimo (`min`), percentiles 25/50/75 (`25%`, `50%`, `75%`) y máximo (`max`).
- `.round(3)` redondea todos los valores a 3 decimales.
- `display()` los muestra como tabla HTML estilizada.

---

```python
display(df_total['AÑO'].value_counts().sort_index().rename('N registros').to_frame())
```
- `.value_counts()` cuenta registros por año.
- `.sort_index()` ordena los años de menor a mayor.
- `.rename('N registros')` cambia el nombre de la serie (que por defecto sería `'AÑO'`).
- `.to_frame()` convierte la serie en DataFrame para que `display()` la muestre como tabla.

---

```python
tabla = (df_total
         .groupby(['NUM_DEPTO', 'NOMBRE_DEPTO'])[COLUMNA_RESULTADO]
         .agg(Promedio='mean', Desv_Est='std', N='count')
         .round(3)
         .reset_index()
         .sort_values('NUM_DEPTO')
         .set_index('NUM_DEPTO'))
```
Cadena de operaciones para construir la tabla de promedios por departamento:
- `.groupby(['NUM_DEPTO', 'NOMBRE_DEPTO'])` agrupa por número Y nombre de departamento simultáneamente (para que ambos aparezcan en la tabla final).
- `.agg(Promedio='mean', Desv_Est='std', N='count')` calcula tres estadísticos por grupo: media, desviación estándar y conteo. La sintaxis `nombre_columna='función'` permite nombrar cada estadístico directamente.
- `.reset_index()` convierte los niveles de agrupación en columnas normales para poder ordenar y reindexar.
- `.sort_values('NUM_DEPTO')` ordena las filas del 1 al 32.
- `.set_index('NUM_DEPTO')` usa el número de departamento como índice de la tabla.

---

---

## Celda 10 — Visualizaciones

```python
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
```
Crea una **figura** (`fig`) con una cuadrícula de 2 filas × 2 columnas de **subgráficos** (`axes`). `figsize=(16, 12)` establece el ancho y alto de la figura en pulgadas. `axes` queda como una matriz 2×2: `axes[0,0]` es el panel superior izquierdo, `axes[0,1]` el superior derecho, `axes[1,0]` el inferior izquierdo y `axes[1,1]` el inferior derecho.

---

```python
fig.suptitle('Análisis Descriptivo...', fontsize=15, fontweight='bold')
```
Agrega un título general a toda la figura (no a un panel individual). `fontsize` controla el tamaño del texto. `fontweight='bold'` lo pone en negrita.

---

```python
media_gral = df_total[COLUMNA_RESULTADO].mean()
```
Calcula la media aritmética de todos los puntajes del DataFrame completo. Se usa como línea de referencia en varios paneles.

---

### Panel 1 — Histograma

```python
ax.hist(df_total[COLUMNA_RESULTADO].dropna(), bins=60,
        color='#2196F3', edgecolor='white', alpha=0.85)
```
- `.dropna()` elimina los valores `NaN` antes de graficar (los histogramas no pueden manejarlos).
- `bins=60` divide el rango de puntajes en 60 intervalos iguales. Más bins = más detalle, menos bins = forma más suave.
- `color='#2196F3'` define el color de relleno de las barras en código hexadecimal (azul Material Design).
- `edgecolor='white'` pone un borde blanco entre barras para mejorar la legibilidad.
- `alpha=0.85` controla la transparencia (0 = invisible, 1 = opaco).

---

```python
ax.axvline(media_gral, color='red', linestyle='--', linewidth=2,
           label=f'Media general: {media_gral:.1f}')
```
`axvline` dibuja una **línea vertical** en el histograma en la posición de la media. `linestyle='--'` la hace punteada. `label=...` define el texto que aparecerá en la leyenda. El formato `:.1f` redondea la media a 1 decimal en el texto.

---

### Panel 2 — Boxplot por año

```python
grupos_año = [df_total.loc[df_total['AÑO'] == a, COLUMNA_RESULTADO].dropna().values
              for a in sorted(df_total['AÑO'].unique())]
```
Comprensión de lista que crea un grupo de puntajes por cada año:
- `df_total['AÑO'].unique()` obtiene los años únicos presentes en el DataFrame.
- `sorted(...)` los ordena cronológicamente.
- `df_total.loc[condición, columna]` selecciona los valores de `COLUMNA_RESULTADO` donde el año es `a`.
- `.values` convierte la columna pandas en un arreglo numpy (necesario para `boxplot`).

---

```python
bp = ax.boxplot(grupos_año, patch_artist=True,
                labels=sorted(df_total['AÑO'].unique()),
                medianprops=dict(color='black', linewidth=2))
```
- `patch_artist=True` permite colorear el interior de las cajas (sin esto son transparentes).
- `labels` etiqueta cada caja con el año correspondiente.
- `medianprops=dict(...)` define el estilo de la línea de la mediana (color negro, gruesa).

---

```python
for patch, color in zip(bp['boxes'], colores_bp[:len(grupos_año)]):
    patch.set_facecolor(color)
```
`zip()` empareja elemento a elemento dos listas: las cajas del boxplot y los colores. El bucle asigna el color de relleno a cada caja. `[:len(grupos_año)]` evita tomar más colores de los que hay años.

---

### Panel 3 — Barras por departamento

```python
prom_depto = (df_total.groupby(['NUM_DEPTO', 'NOMBRE_DEPTO'])[COLUMNA_RESULTADO]
              .mean().reset_index().sort_values(COLUMNA_RESULTADO))
```
Calcula el promedio por departamento y ordena de menor a mayor para que el gráfico de barras muestre una progresión visual clara.

---

```python
colores_bar = ['#EF5350' if v < media_gral else '#66BB6A'
               for v in prom_depto[COLUMNA_RESULTADO]]
```
Comprensión de lista que asigna un color a cada barra: rojo (`#EF5350`) si el promedio del departamento está por debajo de la media nacional, verde (`#66BB6A`) si está por encima.

---

```python
ax.barh(prom_depto['NOMBRE_DEPTO'], prom_depto[COLUMNA_RESULTADO], ...)
```
`barh` (horizontal bar) dibuja barras horizontales. El primer argumento es la lista de etiquetas del eje Y (nombres de departamentos) y el segundo son los valores (promedios).

---

### Panel 4 — Dispersión distancia vs promedio

```python
agg = (df_total.groupby('NUM_DEPTO')
       .agg(promedio=(COLUMNA_RESULTADO, 'mean'),
            distancia=('DIST_BOGOTA_KM', 'first'),
            nombre=('NOMBRE_DEPTO', 'first'))
       .reset_index())
```
`.agg()` con múltiples funciones en un solo llamado. Para el promedio usa `'mean'`, para la distancia usa `'first'` (toma el primer valor del grupo porque todos los registros del mismo departamento tienen la misma distancia), igual para el nombre.

---

```python
mask = agg['distancia'].notna() & agg['promedio'].notna()
if mask.sum() > 1:
    z = np.polyfit(agg.loc[mask, 'distancia'], agg.loc[mask, 'promedio'], 1)
    p = np.poly1d(z)
    xs = np.linspace(agg['distancia'].min(), agg['distancia'].max(), 200)
    ax.plot(xs, p(xs), 'r--', linewidth=1.5, label='Tendencia lineal')
```
Calcula y dibuja la **línea de tendencia lineal** (regresión de primer grado):
- `mask` es un filtro booleano que excluye filas con datos faltantes.
- `np.polyfit(..., 1)` ajusta un polinomio de grado 1 (línea recta) a los puntos. Devuelve los coeficientes `[pendiente, intercepto]`.
- `np.poly1d(z)` convierte esos coeficientes en una función evaluable `p(x)`.
- `np.linspace(min, max, 200)` genera 200 puntos equidistantes entre el mínimo y máximo de la distancia para dibujar la línea suave.
- `ax.plot(xs, p(xs), 'r--')` dibuja la línea: `'r--'` significa rojo (`r`) y punteado (`--`).

---

```python
for _, row in agg.iterrows():
    ax.annotate(str(int(row['NUM_DEPTO'])),
                (row['distancia'], row['promedio']),
                fontsize=7, ha='center', va='bottom', color='#333')
```
`iterrows()` recorre el DataFrame fila por fila (el `_` descarta el índice que no se necesita, `row` es la fila). `ax.annotate()` agrega una etiqueta de texto en las coordenadas `(distancia, promedio)` de cada punto, mostrando el número del departamento. `ha='center'` centra horizontalmente, `va='bottom'` lo posiciona encima del punto.

---

```python
plt.tight_layout()
plt.savefig('analisis_departamentos.png', dpi=150, bbox_inches='tight')
plt.show()
```
- `tight_layout()` ajusta automáticamente los márgenes y espaciados entre paneles para que no se superpongan.
- `savefig()` guarda la figura como imagen. `dpi=150` define la resolución (puntos por pulgada; 150 es buena calidad para pantalla). `bbox_inches='tight'` recorta los márgenes en blanco extras.
- `plt.show()` renderiza y muestra la figura en la salida de la celda.

---

---

## Celda 11 — Exportar

```python
nombre_salida = 'datos_analisis_departamentos.csv'
df_total.to_csv(nombre_salida, index=False, encoding='utf-8-sig')
```
- `.to_csv()` exporta el DataFrame a un archivo CSV.
- `index=False` evita que pandas escriba la columna de índice numérico (0, 1, 2, ...) como primera columna del archivo — esa columna no tiene significado analítico.
- `encoding='utf-8-sig'` usa UTF-8 con marca de orden de bytes (BOM), que hace que Excel en Windows reconozca automáticamente la codificación y muestre las tildes correctamente.

---

```python
files.download(nombre_salida)
```
Llama a la función de descarga de Colab, que envía el archivo guardado en el servidor al navegador del usuario como descarga automática.

---

```python
print(f'  Registros finales : {len(df_total):,}')
print(f'  Columnas totales  : {df_total.shape[1]}')
```
El formato `:,` en el primer print agrega separadores de miles al número (ej. `120000` → `120,000`). `df_total.shape[1]` accede al segundo elemento de la tupla `shape`, que es el número de columnas.
