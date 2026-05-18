# Guía educativa — `colab_pipeline.py`

Este documento describe, con propósito didáctico, **cada elemento real del
código** (palabras reservadas, instrucciones, funciones, estructuras,
librerías, variables, parámetros y conceptos). No se analizan los
comentarios del script: el foco está en lo que efectivamente ejecuta el
intérprete de Python.

> Cómo usar esta guía: cada sección corresponde a un bloque del script.
> Si un elemento aparece varias veces, se explica la primera vez y luego
> se mencionan solo los matices propios del nuevo uso.

---

## 0. Cabecera del archivo

### `from __future__ import annotations`
- **`from … import …`**: instrucción que importa un objeto específico de
  un módulo, sin traer el módulo completo al espacio de nombres.
- **`__future__`**: módulo estándar que expone *features* del lenguaje
  que serán predeterminadas en versiones futuras de Python.
- **`annotations`**: bandera que hace que **todas** las anotaciones de
  tipo se evalúen *de forma diferida* (como cadenas). Permite que el
  archivo siga siendo válido aunque algunas anotaciones referencien
  clases definidas más abajo, sin generar coste en tiempo de ejecución.

### Importaciones estándar

```python
import os
import re
import sys
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple
```

- **`import os`**: módulo estándar para interactuar con el sistema
  operativo (rutas, variables de entorno, directorios). Se usa para
  unir rutas (`os.path.join`), comprobar existencia (`os.path.isfile`,
  `os.path.isdir`, `os.path.ismount`) y crear carpetas (`os.makedirs`).
- **`import re`**: expresiones regulares. Se usa, por ejemplo, para
  capturar el primer dígito de "Estrato 3" o para encontrar el año en
  el nombre de un archivo.
- **`import sys`**: parámetros del intérprete; aquí sirve para
  detectar si el módulo `google.colab` está cargado en `sys.modules`.
- **`import unicodedata`**: librería para normalizar texto Unicode.
  Se usa para descomponer acentos (`'Ñ' → 'N'`, `'Á' → 'A'`).
- **`from datetime import datetime`**: clase para fechas y horas; el
  método `datetime.now()` devuelve la hora actual para registrar logs.
- **`from typing import …`**: módulo de anotaciones de tipo. Cada
  elemento importado describe la forma de una colección:
  - `Dict[K, V]` → diccionario con claves de tipo K y valores de tipo V.
  - `List[T]` → lista homogénea de elementos T.
  - `Tuple[A, B]` → tupla de longitud fija con tipos posicionales.
  - `Iterable[T]` → cualquier objeto recorrible (lista, generador, etc.).
  - `Optional[T]` → equivalente a `Union[T, None]`.

### Importaciones de terceros

```python
import numpy as np
import pandas as pd
```

- **`numpy`** (alias `np`): librería numérica que aporta arreglos
  multidimensionales y el centinela `np.nan` (valor flotante usado para
  representar datos faltantes).
- **`pandas`** (alias `pd`): librería de análisis tabular. Sus clases
  principales son:
  - **`DataFrame`**: tabla bidimensional (filas × columnas) con índice.
  - **`Series`**: columna unidimensional con un índice asociado.
- **`as np` / `as pd`**: alias de importación, atajo idiomático.

---

## 1. Bloque de constantes

### Anotaciones de tipo en variables

```python
RUTA_PROYECTO_DEFECTO: str = "/content/drive/MyDrive/IA_EDUCACION_SUPERIOR"
ANIOS: List[int] = [2021, 2022, 2023, 2024]
```

- **`: str` / `: List[int]`**: declaración de tipo (no obligatoria en
  tiempo de ejecución, pero útil para editores e IDEs).
- **`= "…"`**: asignación. El valor a la derecha se evalúa una sola vez
  cuando se carga el módulo, por lo que estas variables se comportan
  como **constantes** (Python no tiene `const`; la convención es
  escribirlas en MAYÚSCULAS).
- **Cadenas (str)**: secuencias de caracteres entre comillas. Soportan
  el método `.format(…)` (ver más abajo).
- **Listas (list)**: secuencias mutables ordenadas, entre `[ ]`.
- **Tuplas (tuple)**: secuencias inmutables entre `( )`. Se usan en
  `SEPARADORES_CANDIDATOS` y `CODIFICACIONES_CANDIDATAS` para señalar
  que el orden importa y el contenido no se modificará.

### Diccionarios

```python
MAPA_COLUMNAS: Dict[str, str] = { "ESTU_CONSECUTIVO": "id_estudiante", ... }
```

- **Diccionario (`dict`)**: estructura clave→valor entre `{ }`.
- **Claves únicas**: si se repitiera una clave, sólo conserva la última.
- **Acceso**: `MAPA_COLUMNAS["ESTU_CONSECUTIVO"]` devolvería el valor.
  En el código se usa `dict.get(clave, defecto)` o **comprensiones de
  diccionario** (`{k.upper(): v for k, v in ...items()}`) para construir
  versiones derivadas.

### Diccionario con tuplas como valor

```python
DEPARTAMENTOS: Dict[str, Tuple[int, float]] = { "BOGOTA": (0, 0.0), ... }
```

- La estructura agrupa **dos atributos** por departamento: su código
  numérico (0–32) y su distancia oficial a Bogotá. Esto permite, con
  un único diccionario, generar luego dos columnas distintas mediante
  comprensiones (`{nombre: codigo for nombre, (codigo, _) in
  DEPARTAMENTOS.items()}`).
- **`_` (guion bajo)**: convención para "valor que no me interesa".
- **`DEPARTAMENTOS.items()`**: devuelve un iterador de pares
  `(clave, valor)`.

---

## 2. Utilidades generales

### `def _normalizar_texto(valor: object) -> str:`

- **`def`**: palabra reservada para definir una función.
- **`_` inicial**: convención que marca la función como "privada del
  módulo" (no forma parte de la API pública).
- **`valor: object`**: parámetro tipado como `object`, el tipo base de
  Python. Acepta literalmente cualquier cosa.
- **`-> str`**: anota que la función **retorna** una cadena.
- **`pd.isna(valor)`**: función de pandas que detecta valores faltantes
  (`None`, `np.nan`, `pd.NA`).
- **`str(valor)`**: convierte cualquier objeto a cadena.
- **`.strip()`**: elimina espacios al inicio y al final.
- **`.upper()`**: pasa a mayúsculas.
- **`unicodedata.normalize("NFKD", texto)`**: forma de normalización
  Unicode que **descompone** caracteres compuestos (p. ej. `'á'` queda
  como `'a'` + tilde combinante separada).
- **`unicodedata.combining(c)`**: devuelve un entero > 0 si `c` es una
  marca combinante (la tilde, la diéresis…). Se filtran con un
  *generator expression* dentro de `"".join(...)`.
- **`re.sub(patron, reemplazo, cadena)`**: sustituye coincidencias de
  un patrón de expresión regular. `r"\s+"` empareja uno o más espacios
  en blanco; se sustituyen por un único espacio.

### `def _registrar(mensaje: str) -> None:`

- **`-> None`**: la función no retorna ningún valor explícito.
- **`datetime.now()`**: instancia con la hora actual.
- **`.strftime("%H:%M:%S")`**: formatea la hora como `HH:MM:SS`.
- **`f"[{ahora}] {mensaje}"`**: *f-string*, literal con interpolación;
  cada expresión entre `{ }` se evalúa e inserta.
- **`print(...)`**: función incorporada que escribe en `stdout`. En
  Colab aparece debajo de la celda.

---

## 3. Conexión con Google Drive

### `def montar_drive(ruta_proyecto: str = RUTA_PROYECTO_DEFECTO) -> str:`

- **Parámetro con valor por defecto**: si no se pasa argumento, se usa
  `RUTA_PROYECTO_DEFECTO`.
- **`"google.colab" in sys.modules`**: comprueba si el módulo de Colab
  está cargado. Permite que el script funcione también fuera de Colab.
- **`os.path.exists("/content")`**: verificación adicional para
  entornos donde `google.colab` aún no se importó.
- **`from google.colab import drive`** (dentro de la función): *lazy
  import*. Sólo se intenta cuando se ejecuta la función, así que el
  módulo entero sigue siendo importable en máquinas sin Colab.
- **`drive.mount("/content/drive", force_remount=False)`**: monta el
  Drive del usuario en la ruta indicada. El parámetro
  `force_remount=False` evita re-pedir autorización si ya está montado.
- **`os.path.ismount(...)`**: indica si la ruta es un punto de montaje.
- **`raise FileNotFoundError(...)`**: lanza una excepción con un
  mensaje explicativo. Detiene la ejecución inmediatamente.

---

## 4. Lectura robusta de los `.txt`

### `def _detectar_separador_y_codificacion(ruta: str) -> Tuple[str, str]:`

- **Bucle anidado `for ... for ...`**: prueba **cada combinación** de
  codificación y separador.
- **`try / except`**: maneja errores controlados. Se capturan dos
  tipos: `UnicodeDecodeError` (codificación errada) y
  `pd.errors.ParserError` (delimitador inválido).
- **`pd.read_csv(...)`**: lectura del archivo. Parámetros:
  - `sep`: carácter delimitador.
  - `encoding`: codificación del archivo.
  - `nrows=5`: lee sólo cinco filas para sondear estructura.
  - `on_bad_lines="skip"`: ignora filas mal formadas en vez de fallar.
  - `engine="python"`: motor más flexible para detectar errores.
- **`muestra.shape[1]`**: número de columnas; `shape[0]` filas.
- **`return separador, codificacion`**: retorno múltiple usando una
  tupla implícita.

### `def leer_archivo_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:`

- **`PATRON_ARCHIVO.format(anio=anio)`**: sustituye `{anio}` en la
  plantilla por el valor concreto del año (técnica `str.format`).
- **`os.path.join(...)`**: combina partes de ruta usando el separador
  correcto del sistema operativo.
- **`os.path.isfile(...)`**: confirma que el archivo existe.
- **`pd.read_csv(...)` (lectura completa)**: igual que en la detección,
  pero sin `nrows`. Devuelve un `DataFrame` con todas las filas.
- **`df["anio"] = anio`**: añade una columna nueva con valor constante;
  en pandas, asignar a `df[...]` crea o sobrescribe una columna.
- **`f"{len(df):,}"`**: formato con miles. `len(df)` cuenta las filas.

---

## 5. Normalización de nombres de columnas

### `def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:`

- **Comprensión de diccionario**:
  ```python
  mapa_mayus = {k.upper(): v for k, v in MAPA_COLUMNAS.items()}
  ```
  Construye en una línea un diccionario nuevo con las claves en
  mayúsculas. Útil para emparejar columnas independientemente de cómo
  vengan escritas en el archivo.
- **`df.columns`**: índice con los nombres de las columnas; iterable.
- **`df.rename(columns=nuevas)`**: devuelve un `DataFrame` nuevo con
  las columnas renombradas. No modifica el original si no se pasa
  `inplace=True`.
- **Asignación a `df` localmente**: no afecta al `DataFrame` original
  del *caller* porque Python pasa **referencias por valor**: la
  reasignación cambia la variable local, no el objeto remoto.

---

## 6. Construcción de variables

### `def _a_numerico(serie: pd.Series) -> pd.Series:`

- **`serie.dtype.kind in "iuf"`**: comprueba si el `dtype` de la
  columna ya es entero (`i`), entero sin signo (`u`) o flotante
  (`f`). Si lo es, evita trabajo redundante.
- **`serie.astype(str)`**: castea a cadena para usar métodos vectoriales
  de texto.
- **`.str.replace(",", ".", regex=False)`**: reemplaza coma decimal
  (formato latino) por punto decimal (formato Python). `regex=False`
  trata los caracteres como literales.
- **`pd.to_numeric(..., errors="coerce")`**: convierte a número; los
  valores no convertibles se vuelven `NaN` en vez de provocar error.

### `def construir_periodo_ia(df: pd.DataFrame) -> pd.DataFrame:`

- **`df["anio"].apply(lambda a: ...)`**: aplica una función fila a fila.
- **`lambda a: 0 if a in ANIOS_PREVIO else (1 if a in ANIOS_IA else np.nan)`**:
  función anónima con dos expresiones condicionales anidadas.
- **`.astype("Int64")`**: tipo entero nullable (admite `pd.NA`),
  necesario para variables binarias con posibles ausentes.

### `def construir_puntaje_generico(df: pd.DataFrame) -> pd.DataFrame:`

- **Lista por comprensión**:
  ```python
  disponibles = []
  for modulo in MODULOS_GENERICOS:
      if modulo in df.columns:
          ...
          disponibles.append(modulo)
  ```
  Acumula los módulos efectivamente presentes en el archivo.
- **`df[disponibles].mean(axis=1, skipna=True)`**: promedio por fila
  (eje 1) ignorando `NaN`. Resultado: una `Series` que se asigna a
  `puntaje_saberpro_generico`.
- **Operador ternario**:
  ```python
  df[disponibles].mean(...) if disponibles else np.nan
  ```
  Si la lista está vacía, asigna `NaN` para no fallar con DataFrame
  vacío.

### `def construir_edad(df: pd.DataFrame) -> pd.DataFrame:`

- **`pd.to_datetime(serie, errors="coerce", dayfirst=True, infer_datetime_format=True)`**:
  convierte cadenas a fechas (`Timestamp`). Los formatos incorrectos
  pasan a `NaT`.
- **`fecha.dt.year`**: accessor `dt` para operaciones de fecha; extrae
  el componente año.
- **`df["anio"] - fecha.dt.year`**: resta vectorial entre dos columnas
  (numpy difunde la operación).
- **`.astype("Float64")`**: flotante nullable (admite `NA`).
- **Indexación booleana**:
  ```python
  df.loc[(df["edad"] < 15) | (df["edad"] > 80), "edad"] = np.nan
  ```
  `df.loc[filas, columna]` permite asignar selectivamente. El operador
  `|` es OR booleano vectorial; cada paréntesis es obligatorio por
  precedencia.

### Funciones `construir_*` basadas en mapeo

Muchas funciones (`construir_estrato`, `construir_genero`,
`construir_nivel_educ_padre`, `construir_estu_trabaja`,
`construir_cabeza_familia`, `construir_internet`,
`construir_area_residencia`) siguen el mismo patrón:

```python
serie = df["columna_raw"].apply(_normalizar_texto)
df["nueva"] = serie.map({clave: valor, ...}).astype("Int64")
```

- **`.apply(func)`**: aplica `func` elemento a elemento de la `Series`.
- **`.map(diccionario)`**: traduce cada valor según el diccionario;
  los valores no encontrados se convierten en `NaN`.
- **`.str.extract(r"(\d)", expand=False)`**: aplica una regex con un
  grupo de captura. Devuelve la primera coincidencia; `expand=False`
  retorna una `Series` (no un `DataFrame`).

### `def construir_jornada(df: pd.DataFrame) -> pd.DataFrame:`

- **List comprehension `candidatas = [c for c in (...) if c in df.columns]`**:
  filtra qué columnas de horario/metodología están disponibles.
- **`df[candidatas].astype(str).agg(" ".join, axis=1)`**: concatena
  columna a columna por fila (`axis=1`) con `" "` entre cada par.
- **`np.where(condicion, valor_si, valor_no)`**: equivalente vectorial
  del operador ternario. Aquí está **anidado**: dos niveles para
  manejar tres estados (1 / 0 / NaN).
- **`pd.array(..., dtype="Float64")`**: crea un array de pandas con
  tipo nullable explícito.

### `def _canonizar_departamento(valor: object) -> Optional[str]:`

- Devuelve **el nombre canónico** o `None` si no se reconoce.
- Estrategia en tres pasos:
  1. Coincidencia exacta con `ALIAS_DEPARTAMENTOS`.
  2. Coincidencia con la clave canónica de `DEPARTAMENTOS`.
  3. Coincidencia parcial (`startswith` o `in`) para tolerar variantes
     como `'BOGOTA DC, COLOMBIA'`.
- **`for canon in DEPARTAMENTOS:`**: iterar un `dict` produce sus
  claves (en orden de inserción desde Python 3.7+).

### `def construir_departamento(df: pd.DataFrame) -> pd.DataFrame:`

- **`canonico.map({nombre: codigo for nombre, (codigo, _) in DEPARTAMENTOS.items()})`**:
  combinación de `.map(...)` con una comprensión de diccionario que
  desempaqueta la tupla `(codigo, distancia)` y conserva sólo el
  código.
- **Tupla desempaquetada `(codigo, _)`**: se ignora la distancia con
  el guion bajo.

### `def construir_distancia_bogota(df: pd.DataFrame) -> pd.DataFrame:`

- Estructura análoga, pero conservando la distancia en lugar del
  código.

### `def construir_variables(df: pd.DataFrame) -> pd.DataFrame:`

- Orquesta las 14 funciones anteriores **en orden**. Cada paso
  modifica `df` y lo devuelve; la siguiente función opera sobre el
  resultado de la anterior.

---

## 7. Limpieza

### `def seleccionar_variables_finales(df: pd.DataFrame) -> pd.DataFrame:`

- **`for col in VARIABLES_FINALES`**: garantiza el esquema constante:
  si una columna no se construyó (porque su fuente no existía), se
  crea como `NaN`.
- **`df[VARIABLES_FINALES].copy()`**: indexa por lista de columnas
  (selecciona y reordena en una sola operación). `.copy()` evita
  vistas que generen `SettingWithCopyWarning` posteriormente.

### `def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:`

- **`n_inicial = len(df)`**: guarda el tamaño original para el reporte.
- **`for col in MODULOS_GENERICOS + [...]`**: concatena listas con `+`;
  resulta en una lista nueva con ambas.
- **`df[col].between(0, 300)`**: máscara booleana, `True` si el valor
  está dentro del intervalo inclusivo.
- **`~` (tilde)**: NOT lógico vectorial. `~df[col].between(0, 300)` es
  la máscara complementaria (valores fuera de rango).
- **`& ` (ampersand)**: AND lógico vectorial.
- **`df.loc[mascara, col] = valor`**: asignación condicional.
- **`df = df[mascara].copy()`**: filtra filas conservando una nueva copia.
- **`df.drop_duplicates(subset=[...], keep="first")`**: elimina
  duplicados. `subset` define qué columnas usar para identificar
  duplicados; `keep="first"` conserva la primera aparición.
- **`df.reset_index(drop=True)`**: reinicia el índice numérico tras el
  filtrado. `drop=True` descarta el índice anterior.

---

## 8. Procesamiento y consolidación

### `def procesar_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:`

- Composición funcional: cada llamada recibe el resultado de la
  anterior. Estilo "pipeline" sin necesidad de variables intermedias
  globales.

### `def consolidar(dfs: Dict[int, pd.DataFrame]) -> pd.DataFrame:`

- **`pd.concat([...], axis=0, ignore_index=True)`**:
  - `axis=0` → apila por filas (verticalmente).
  - `ignore_index=True` → genera índice nuevo 0..n-1.
- **`dfs.values()`**: vista sobre los `DataFrame` del diccionario
  (en orden de inserción).

### `def persistir(...):`

- **`os.makedirs(salida, exist_ok=True)`**: crea recursivamente. Con
  `exist_ok=True` no falla si ya existe.
- **`df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")`**:
  exporta CSV.
  - `index=False` → no escribe la columna de índice.
  - `utf-8-sig` → UTF-8 con BOM (compatible con Excel).
- **`df.to_parquet(ruta_parquet, index=False)`**: formato binario
  columnar. Requiere `pyarrow` o `fastparquet`.
- **`try / except Exception as exc:`**: captura cualquier error de
  guardado en parquet (p. ej. dependencia ausente) y permite que el
  pipeline continúe.
- **`# noqa: BLE001`**: silencia el aviso del linter sobre captura
  amplia de excepciones (es deliberada).

---

## 9. Orquestador

### `def ejecutar_pipeline(...) -> Tuple[Dict[int, pd.DataFrame], pd.DataFrame]:`

- Parámetros nombrados con valores por defecto:
  - `ruta_proyecto` permite redirigir a otra carpeta.
  - `anios` acepta cualquier iterable (lista, tupla, generador).
  - `persistir_disco=True` se puede poner en `False` para análisis
    rápido en memoria.
- **`Tuple[Dict[int, pd.DataFrame], pd.DataFrame]`**: anotación del
  retorno: una tupla con dos elementos.
- **`for anio in anios:`**: bucle estándar; cada año genera una
  entrada nueva en `dfs`.
- **`dfs[anio] = procesar_anio(ruta, anio)`**: inserción dinámica
  clave→valor.

---

## 10. Ejecución directa

```python
if __name__ == "__main__":
    dfs_anio, df_total = ejecutar_pipeline()
```

- **`__name__`**: variable especial que vale `"__main__"` cuando el
  archivo se ejecuta directamente, y el nombre del módulo cuando se
  importa.
- **`dfs_anio, df_total = ejecutar_pipeline()`**: **desempaquetado**
  de la tupla devuelta; cada elemento se asigna a una variable.
- **`dfs_anio.get(2021)`**: igual que `dfs_anio[2021]` pero devuelve
  `None` (en vez de lanzar `KeyError`) si la clave no existe.
- **`df_consolidado.describe(include="all").T.head(20)`**:
  - `.describe(include="all")` → resumen estadístico de todas las
    columnas (numéricas y categóricas).
  - `.T` → transpone (filas ↔ columnas) para visualización compacta.
  - `.head(20)` → primeras 20 filas.

---

## Apéndice A — Glosario de operadores y sintaxis usados

| Símbolo / construcción | Significado |
|---|---|
| `=` | Asignación. |
| `==`, `!=` | Comparación de igualdad / desigualdad. |
| `<`, `<=`, `>`, `>=` | Comparaciones numéricas. |
| `and`, `or`, `not` | Operadores booleanos escalares. |
| `&`, `\|`, `~` | Operadores booleanos vectoriales (numpy/pandas). |
| `if … else …` | Expresión condicional ternaria. |
| `for … in …` | Bucle iterativo. |
| `lambda x: …` | Función anónima. |
| `def f(...): ...` | Definición de función. |
| `return` | Devuelve un valor desde una función. |
| `raise` | Lanza una excepción. |
| `try / except` | Maneja excepciones. |
| `from … import …` | Importa nombres específicos. |
| `f"…"` | Cadena formateada (interpolación). |
| `[a, b, c]` | Literal de lista. |
| `(a, b, c)` | Literal de tupla. |
| `{k: v}` | Literal de diccionario. |
| `[x for x in y]` | Comprensión de lista. |
| `{k: v for k, v in z}` | Comprensión de diccionario. |
| `_` | Convención: identificador "irrelevante". |
| `__name__` | Variable especial del intérprete. |
| `pd.NA`, `np.nan`, `None` | Distintas representaciones de "faltante". |

---

## Apéndice B — Tabla resumen de funciones definidas

| Función | Entradas | Retorno | Propósito |
|---|---|---|---|
| `_normalizar_texto` | `object` | `str` | Mayúsculas, sin acentos, espacios simples. |
| `_registrar` | `str` | `None` | Log con timestamp. |
| `montar_drive` | `str` | `str` | Monta Drive (en Colab) y devuelve ruta. |
| `_detectar_separador_y_codificacion` | `str` | `(str, str)` | Detecta delim. + encoding. |
| `leer_archivo_anio` | `str, int` | `DataFrame` | Carga el `.txt` anual. |
| `normalizar_columnas` | `DataFrame` | `DataFrame` | Renombra según `MAPA_COLUMNAS`. |
| `_a_numerico` | `Series` | `Series` | Convierte a numérico tolerando coma. |
| `construir_periodo_ia` | `DataFrame` | `DataFrame` | Dummy 0/1 por cohorte temporal. |
| `construir_puntaje_generico` | `DataFrame` | `DataFrame` | Promedio simple de 5 módulos. |
| `construir_edad` | `DataFrame` | `DataFrame` | Edad en años cumplidos. |
| `construir_estrato` | `DataFrame` | `DataFrame` | Escala 1–6. |
| `construir_genero` | `DataFrame` | `DataFrame` | Dummy F=0 / M=1. |
| `construir_nivel_educ_padre` | `DataFrame` | `DataFrame` | Escala ordinal 1–7. |
| `construir_estu_trabaja` | `DataFrame` | `DataFrame` | Dummy 0/1. |
| `construir_cabeza_familia` | `DataFrame` | `DataFrame` | Proxy via pago de matrícula. |
| `construir_jornada` | `DataFrame` | `DataFrame` | Dummy 1=nocturna/virtual. |
| `construir_internet` | `DataFrame` | `DataFrame` | Dummy 1=tiene. |
| `construir_area_residencia` | `DataFrame` | `DataFrame` | Dummy 1=urbana. |
| `construir_naturaleza_ies` | `DataFrame` | `DataFrame` | Dummy 1=privada. |
| `_canonizar_departamento` | `object` | `Optional[str]` | Nombre canónico o `None`. |
| `construir_departamento` | `DataFrame` | `DataFrame` | Código 0–32 + nombre. |
| `construir_distancia_bogota` | `DataFrame` | `DataFrame` | km vía terrestre a Bogotá. |
| `construir_variables` | `DataFrame` | `DataFrame` | Orquesta las 14 construcciones. |
| `seleccionar_variables_finales` | `DataFrame` | `DataFrame` | Conserva sólo VARIABLES_FINALES. |
| `limpiar_dataframe` | `DataFrame` | `DataFrame` | Saneamiento final. |
| `procesar_anio` | `str, int` | `DataFrame` | Pipeline completo para un año. |
| `consolidar` | `Dict[int, DataFrame]` | `DataFrame` | Concatena los df anuales. |
| `persistir` | `str, dict, DataFrame` | `str` | Guarda CSV (y parquet si puede). |
| `ejecutar_pipeline` | `str, Iterable[int], bool` | `(dict, DataFrame)` | Punto de entrada del módulo. |
