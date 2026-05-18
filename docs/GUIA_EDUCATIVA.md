# Guía educativa — `preparar_datos.py`

Este documento explica, con propósito didáctico, **cada elemento real
del código** del script `python/preparar_datos.py`: palabras
reservadas, instrucciones, funciones, estructuras, librerías,
variables, parámetros y conceptos. Los comentarios del script no se
analizan; el foco está en lo que efectivamente ejecuta el intérprete.

> El orden de las secciones sigue el orden en que aparecen los
> elementos en el archivo. Si algo se repite, se explica la primera vez
> y después se mencionan solo los matices nuevos.

---

## 0. Cabecera del archivo

```python
from __future__ import annotations
```

- **`from … import …`** — importa nombres específicos de un módulo
  sin traer todo el módulo al espacio de nombres.
- **`__future__`** — módulo estándar que expone funcionalidades del
  lenguaje que pasarán a ser el comportamiento predeterminado.
- **`annotations`** — hace que las anotaciones de tipo (`: str`,
  `-> int`, etc.) se evalúen de forma **diferida**, como cadenas. Permite
  que el script funcione aunque alguna anotación referencie una clase
  declarada más abajo, sin coste en tiempo de ejecución.

### Importaciones estándar

```python
import argparse
import os
import re
import sys
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple
```

- **`argparse`** — librería estándar para construir interfaces de línea
  de comandos. Aquí define `--ruta`, `--anios`, `--sin-guardar`.
- **`os`** — utilidades del sistema operativo: unir rutas
  (`os.path.join`), comprobar existencia (`os.path.isfile`,
  `os.path.isdir`), crear carpetas (`os.makedirs`).
- **`re`** — expresiones regulares. Aquí se usa para capturar el primer
  dígito ("Estrato 3" → 3) y para colapsar espacios duplicados.
- **`sys`** — parámetros del intérprete; aquí sirve para detectar si
  `google.colab` está en `sys.modules`.
- **`unicodedata`** — normalización Unicode. `NFKD` descompone caracteres
  acentuados; `combining` identifica las marcas combinantes (tildes).
- **`from datetime import datetime`** — la clase `datetime` permite
  obtener la hora actual con `.now()` y formatearla con `.strftime`.
- **`from typing import …`** — anotaciones de tipo:
  - `Dict[K, V]` → diccionario con claves K y valores V.
  - `List[T]` → lista homogénea de tipo T.
  - `Tuple[A, B]` → tupla de longitud fija con tipos por posición.
  - `Optional[T]` → equivalente a `Union[T, None]`.
  - `Iterable[T]` → cualquier objeto que pueda recorrerse con `for`.

### Importaciones de terceros

```python
import numpy as np
import pandas as pd
```

- **`numpy`** (alias `np`) — biblioteca numérica. Aporta `np.nan`
  (centinela flotante para valores faltantes), arrays vectoriales y
  operaciones como `np.where(cond, si, no)`.
- **`pandas`** (alias `pd`) — librería de análisis tabular. Las clases
  principales son:
  - **`DataFrame`** — tabla 2D (filas × columnas) con un índice.
  - **`Series`** — columna 1D con un índice asociado.
- **`as np` / `as pd`** — alias idiomáticos para acortar el nombre.

---

## 1. Constantes (Bloque 1)

### Anotación de tipo en variables

```python
PATRON_ARCHIVO: str = "Examen_Saber_Pro_Genericas_{anio}.txt"
ANIOS: List[int] = [2021, 2022, 2023, 2024]
```

- **`: str` / `: List[int]`** — declaración de tipo. No es obligatoria
  en tiempo de ejecución pero ayuda al editor y a los linters.
- Cuando una variable se escribe en MAYÚSCULAS, la convención indica
  que es una **constante** (Python no tiene `const`).
- **Cadenas (`str`)** — secuencias de caracteres entre comillas. Aquí
  se usa el método `.format(anio=…)` para sustituir `{anio}`.
- **Listas (`list`)** — secuencias mutables ordenadas entre `[ ]`.
- **Tuplas (`tuple`)** — secuencias inmutables entre `( )`. Se usan en
  `SEPARADORES_CANDIDATOS` y `CODIFICACIONES_CANDIDATAS` para señalar
  que el orden importa y el contenido no se modificará.

### Diccionarios

```python
DEPARTAMENTOS: Dict[str, Tuple[int, float]] = {
    "BOGOTA": (0, 0.0),
    "AMAZONAS": (1, 1100.0),
    ...
}
```

- **Diccionario (`dict`)** — colección de pares clave→valor entre `{ }`.
- **Tupla como valor** — cada entrada agrupa dos atributos del
  departamento (código numérico y distancia oficial a Bogotá), de modo
  que se reutiliza el diccionario para generar dos columnas distintas.
- **Acceso**: `DEPARTAMENTOS["BOGOTA"]` devuelve `(0, 0.0)`. Iterar el
  diccionario produce sus claves; `.items()` produce pares
  `(clave, valor)`; `.values()` produce sólo los valores.

### Listas derivadas con suma

```python
VARIABLES_FINALES = (
    VARIABLES_DESCRIPTIVO
    + [c for c in VARIABLES_MODELO if c not in VARIABLES_DESCRIPTIVO]
)
```

- **`+` en listas** — concatena. La expresión construye la unión
  ordenada: las columnas comunes aparecen una sola vez.
- **Comprensión de lista** — `[c for c in X if cond]` genera una lista
  nueva filtrada y/o transformada en una sola línea.

---

## 2. Utilidades (Bloque 2)

### `def _normalizar_texto(valor: object) -> str:`

- **`def`** — palabra reservada para definir una función.
- **`_` inicial** — convención: la función es privada del módulo
  (no forma parte de la API pública).
- **`valor: object`** — el parámetro acepta cualquier objeto, porque
  `object` es la clase base de Python.
- **`-> str`** — anota que la función devuelve una cadena.
- **`pd.isna(valor)`** — detecta valores faltantes (`None`, `np.nan`,
  `pd.NA`, `NaT`).
- **`str(valor)`** — convierte cualquier objeto a cadena.
- **`.strip()`** — quita espacios al inicio y final.
- **`.upper()`** — pasa a mayúsculas.
- **`unicodedata.normalize("NFKD", texto)`** — descompone caracteres
  acentuados (`'á' → 'a'` + tilde combinante separada).
- **`unicodedata.combining(c)`** — devuelve > 0 si `c` es una marca
  combinante; permite filtrarlas en el `"".join(...)`.
- **`"".join(generator)`** — concatena los elementos del generador
  usando `""` como separador.
- **`re.sub(r"\s+", " ", texto)`** — sustituye una o más apariciones de
  espacios en blanco por un único espacio. El prefijo `r` indica raw
  string (no se interpretan secuencias de escape).

### `def _registrar(mensaje: str) -> None:`

- **`-> None`** — la función no retorna ningún valor explícito.
- **`datetime.now()`** — instancia con la fecha/hora actual.
- **`.strftime("%H:%M:%S")`** — formatea como `HH:MM:SS`.
- **`f"[{ahora}] {mensaje}"`** — *f-string*: literal con interpolación;
  cada expresión entre `{ }` se evalúa.
- **`print(...)`** — función incorporada que escribe en `stdout`.

### `def _a_numerico(serie: pd.Series) -> pd.Series:`

- **`serie.dtype.kind in "iuf"`** — `dtype.kind` es un carácter que
  resume el tipo: `i` entero, `u` entero sin signo, `f` flotante. El
  operador `in` busca el carácter dentro de la cadena `"iuf"`.
- **`serie.astype(str)`** — castea a cadena para usar métodos
  vectoriales de texto.
- **`.str.replace(",", ".", regex=False)`** — reemplaza coma decimal
  (formato latino) por punto. `regex=False` trata los argumentos como
  literales.
- **`pd.to_numeric(..., errors="coerce")`** — convierte a número;
  cualquier valor no convertible se vuelve `NaN`.

---

## 3. Conexión opcional con Google Drive (Bloque 3)

### `def montar_drive_si_aplica(punto_montaje: str = "/content/drive") -> bool:`

- **Parámetro con valor por defecto** — `punto_montaje` toma
  `/content/drive` si no se pasa argumento.
- **`"google.colab" not in sys.modules`** — el operador `in` aquí
  consulta si el módulo está cargado.
- **`os.path.exists(...)`** — comprueba si una ruta existe.
- **`try / except ImportError`** — manejo controlado: si el import
  falla, devuelve `False` en vez de lanzar excepción.
- **`from google.colab import drive`** dentro de la función — *lazy
  import*: sólo se intenta cuando se ejecuta, no al cargar el módulo.
- **`os.path.ismount(...)`** — devuelve `True` si la ruta es un punto de
  montaje.
- **`drive.mount(punto_montaje, force_remount=False)`** — monta el
  Drive del usuario. `force_remount=False` evita re-pedir autorización.
- **`return True / return False`** — finalizan la función y devuelven
  ese valor al *caller*.

---

## 4. Lectura (Bloque 4)

### `def _detectar_formato(ruta: str) -> Tuple[str, str]:`

- **Bucle anidado** — `for codificacion in …: for separador in …:`
  prueba cada combinación de encoding y separador.
- **`try / except (UnicodeDecodeError, pd.errors.ParserError):`** —
  captura dos tipos de error con una sola cláusula.
- **`pd.read_csv(...)`** — lectura de archivos delimitados. Parámetros
  usados aquí:
  - `sep` — carácter delimitador.
  - `encoding` — codificación del archivo.
  - `nrows=5` — sólo cinco filas para sondear estructura.
  - `on_bad_lines="skip"` — ignora filas mal formadas.
  - `engine="python"` — motor más flexible.
- **`muestra.shape[1]`** — número de columnas. `shape[0]` filas.
- **`continue`** — salta a la siguiente iteración del bucle interno.
- **`return separador, codificacion`** — retorno múltiple usando una
  tupla implícita.
- **`raise ValueError(...)`** — lanza una excepción; detiene la
  ejecución si ninguna combinación funcionó.

### `def _leer_columnas_disponibles(ruta, sep, enc) -> List[str]:`

- **`pd.read_csv(..., nrows=0)`** — lee cero filas; sólo trae la
  cabecera. Es una técnica común para inspeccionar columnas sin gasto
  de memoria.
- **`list(...)`** — convierte el objeto `Index` de pandas a lista.

### `def leer_archivo_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:`

- **`PATRON_ARCHIVO.format(anio=anio)`** — sustituye `{anio}` en la
  plantilla.
- **`os.path.join(...)`** — concatena partes de ruta con el separador
  correcto del sistema operativo.
- **`os.path.isfile(...)`** — comprueba existencia del archivo.
- **Comprensión de diccionario**
  ```python
  mapa_lower = {c.lower(): c for c in cols_archivo}
  ```
  Construye un diccionario "lowercase → nombre original".
- **`usecols = [mapa_lower[c] for c in COLS_REQUERIDAS if c in mapa_lower]`**
  Comprensión de lista filtrada: solo conserva las columnas que el
  archivo trae realmente.
- **`pd.read_csv(..., usecols=usecols)`** — carga **solo** esas
  columnas; ahorra mucha memoria con los archivos grandes del ICFES.
- **`df.columns = [c.lower() for c in df.columns]`** — reasigna el
  índice de columnas con todos los nombres en minúsculas. Pandas acepta
  asignar una lista al atributo `columns` mientras tenga la misma
  longitud.
- **`df["anio"] = anio`** — crea una columna nueva con valor constante.
- **`for col in COLS_REQUERIDAS: if col not in df.columns: df[col] = np.nan`**
  Garantiza esquema constante entre años (si una columna falta, queda
  como `NaN`).
- **`f"{len(df):,}"`** — formato con separador de miles.

---

## 5. Construcción de variables (Bloque 5)

### Patrón general

```python
def construir_X(df: pd.DataFrame) -> pd.DataFrame:
    ... # construir df["nueva_variable"]
    df = df.drop(columns=["columna_cruda"])
    return df
```

- **`df.drop(columns=[...])`** — devuelve un dataframe sin esas
  columnas. La reasignación `df = df.drop(...)` reemplaza la referencia
  local pero **no** modifica el original del *caller*: cuando la
  función retorna `df`, el caller debe asignar el resultado para
  conservarlo.

### `def transformar_id_y_modulos(df) -> df:`

- **`df.rename(columns=renombres)`** — devuelve un dataframe con las
  columnas renombradas según el diccionario `renombres`.
- **Bucle `for col in MODULOS_GENERICOS: df[col] = _a_numerico(df[col])`** —
  convierte los puntajes a numérico.

### `def construir_periodo_ia(df) -> df:`

- **`df["anio"].apply(func)`** — aplica `func` elemento a elemento de la
  `Series`.
- **`lambda a: 0 if a in ANIOS_PREVIO else (1 if a in ANIOS_IA else np.nan)`**
  — función anónima con dos expresiones condicionales anidadas.
- **`.astype("Int64")`** — tipo entero **nullable** (admite `pd.NA`).
  Útil para variables binarias con posibles ausentes.

### `def construir_puntaje_generico(df) -> df:`

- **`df[MODULOS_GENERICOS].mean(axis=1, skipna=True)`** — promedio
  por **fila** (`axis=1`) ignorando `NaN`.

### `def construir_edad(df) -> df:`  (calcular edad + drop fuente)

- **`pd.to_datetime(serie, errors="coerce", dayfirst=True)`** —
  convierte a fecha (`Timestamp`); valores no parseables → `NaT`.
  `dayfirst=True` interpreta `DD/MM/AAAA`.
- **`fecha.dt.year`** — accessor `dt` para operaciones de fecha;
  extrae el año.
- **`df["anio"] - fecha.dt.year`** — resta vectorial elemento a
  elemento; el resultado es una `Series`.
- **`.astype("Float64")`** — flotante nullable.
- **Indexación booleana con `df.loc`**
  ```python
  df.loc[(df["edad"] < 15) | (df["edad"] > 80), "edad"] = np.nan
  ```
  - `df.loc[filas, columna]` permite asignación selectiva.
  - **`|`** es OR booleano **vectorial**; los paréntesis son obligatorios
    por precedencia (el operador `|` tiene menos precedencia que `<`/`>`).
- **`df.drop(columns=["estu_fechanacimiento"])`** — al terminar, la
  columna fuente desaparece del dataframe.

### Funciones `construir_*` basadas en `.map(diccionario)`

- **`serie.apply(_normalizar_texto)`** — normaliza cada celda (mayúsculas,
  sin acentos, espacios simples).
- **`serie.map({clave: valor, ...})`** — traduce cada valor según el
  diccionario; los valores no encontrados quedan `NaN`. Es el patrón
  usado en `construir_genero`, `construir_nivel_educ_padre`,
  `construir_estu_trabaja`, `construir_cabeza_familia`,
  `construir_internet`.

### `def construir_estrato(df) -> df:`

- **`serie.str.extract(r"(\d)", expand=False)`** — aplica una expresión
  regular con un grupo de captura. Devuelve la primera coincidencia.
  `expand=False` retorna una `Series`; con `expand=True` daría un
  `DataFrame`.
- **`extraido.where(extraido.between(1, 6))`** — conserva los valores
  donde la condición es verdadera; los demás pasan a `NaN`.

### `def construir_jornada(df) -> df:`

- **`np.where(condicion, valor_si, valor_no)`** — equivalente vectorial
  del operador ternario.
- **`np.where` anidado** — para manejar tres estados (1 / 0 / NaN).
- **`serie.str.contains("PATRON|OTRO", regex=True)`** — máscara booleana
  con regex. El carácter `|` dentro del patrón es OR de regex (no el OR
  booleano de pandas).
- **`pd.array(..., dtype="Float64").astype("Int64")`** — pasa por un
  flotante nullable para luego convertirlo a entero nullable, evitando
  errores al castear `NaN` a `int`.

### `def construir_area_residencia(df) -> df:`

- Misma técnica que `construir_jornada`. Reconoce "CABECERA" o "URBAN"
  como urbano y "RURAL" como rural.

### `def construir_naturaleza_ies(df) -> df:`

- **`norm.str.startswith("NO OFICIAL")`** — máscara booleana que
  identifica IES privadas (las categorías "NO OFICIAL - …" del
  diccionario DataICFES).
- **`mask1 | mask2`** — OR booleano vectorial entre dos máscaras.

### `def _canonizar_departamento(valor) -> Optional[str]:`

- **`return None`** — sale de la función con `None` (Python sin
  retorno explícito devolvería también `None`).
- Tres niveles de coincidencia: alias directo, igualdad con clave
  canónica y coincidencia parcial (`startswith` o `in`).
- **`for canon in DEPARTAMENTOS:`** — iterar un `dict` produce sus
  claves en orden de inserción (Python 3.7+).

### `def construir_departamento_y_distancia(df) -> df:`

- **`canon.map({n: c for n, (c, _) in DEPARTAMENTOS.items()})`** —
  combinación de `.map(...)` con comprensión de diccionario que
  desempaqueta la tupla `(c, d)` y conserva sólo el código.
- **`_` (guion bajo)** — convención: "valor que no me interesa".

### `def construir_todas_las_variables(df) -> df:`

- Aplica las 14 funciones en orden. Cada llamada modifica `df`
  (renombrando, añadiendo columnas y eliminando fuentes), y se
  reasigna a `df` para que la siguiente función opere sobre el estado
  actualizado.

---

## 6. Limpieza (Bloque 6)

### `def limpiar(df) -> df:`

- **`n_inicial = len(df)`** — guarda el tamaño original.
- **`for col in MODULOS_GENERICOS + ["puntaje_saberpro_generico"]:`** —
  el `+` concatena listas para iterar sobre la unión.
- **`~df[col].between(0, 300)`** — **`~`** es NOT booleano vectorial;
  la máscara identifica valores fuera del intervalo inclusivo.
- **`mask1 & mask2`** — AND vectorial.
- **`df = df[df["X"].notna()].copy()`** — filtra filas. El método
  `.notna()` devuelve una máscara booleana. `.copy()` evita avisos
  `SettingWithCopyWarning` posteriores.
- **`df.drop_duplicates(subset=["id_estudiante", "anio"], keep="first")`** —
  elimina filas duplicadas según las columnas indicadas; conserva la
  primera ocurrencia.
- **`df.reset_index(drop=True)`** — reinicia el índice numérico tras el
  filtrado. `drop=True` descarta el índice anterior.

### `def seleccionar_variables_finales(df) -> df:`

- **`df[VARIABLES_FINALES].copy()`** — selecciona y reordena columnas
  en una sola operación; `.copy()` garantiza un objeto independiente.

---

## 7. Procesamiento y consolidación (Bloque 7)

### `def procesar_anio(ruta_proyecto, anio) -> df:`

- Estilo "pipeline": cada función recibe el resultado de la anterior.

### `def consolidar(dfs: Dict[int, pd.DataFrame]) -> df:`

- **`pd.concat([...], axis=0, ignore_index=True)`** — apila los
  dataframes verticalmente y reindexa.
- **`dfs.values()`** — vista de los `DataFrame` del diccionario, en
  orden de inserción.

### `def persistir(ruta_proyecto, dfs, df_consolidado) -> str:`

- **`os.makedirs(salida, exist_ok=True)`** — crea recursivamente; con
  `exist_ok=True` no falla si la carpeta ya existe.
- **`df.to_csv(ruta, index=False, encoding="utf-8-sig")`** — exporta
  CSV. `index=False` evita escribir la columna de índice;
  `utf-8-sig` es UTF-8 con BOM (compatible con Excel).

---

## 8. Orquestador (Bloque 8)

### `def ejecutar_pipeline(ruta_proyecto, anios=ANIOS, persistir_disco=True) -> tuple:`

- **Parámetros con valores por defecto** — permite invocar la función
  sin pasar `anios` ni `persistir_disco`.
- **`Iterable[int]`** — el parámetro `anios` acepta cualquier objeto
  recorrible: lista, tupla, generador, `range`.
- **`raise FileNotFoundError(...)`** — lanza una excepción concreta.
- **`for anio in anios: dfs[anio] = procesar_anio(...)`** — bucle que
  va llenando el diccionario.
- **Tupla de retorno** — `return dfs, df_consolidado` devuelve dos
  valores empaquetados en una tupla.

---

## 9. CLI (Bloque 9)

### `def _construir_parser() -> argparse.ArgumentParser:`

- **`argparse.ArgumentParser(description=...)`** — crea el parser
  principal.
- **`parser.add_argument("--ruta", "-r", required=True, help=...)`** —
  registra un argumento con su nombre largo, alias corto, obligación y
  ayuda.
- **`nargs="+"`** — acepta uno o más valores (`--anios 2021 2022 2023`).
- **`type=int`** — convierte cada valor a entero al recibirlo.
- **`default=ANIOS`** — valor por defecto si no se pasa el argumento.
- **`action="store_true"`** — convierte el flag en booleano: `True` si
  está presente, `False` si no.

### Bloque `if __name__ == "__main__":`

- **`__name__`** — variable especial: vale `"__main__"` cuando el
  archivo se ejecuta directamente, y el nombre del módulo cuando se
  importa. Permite que el código sólo corra cuando se invoca desde la
  CLI.
- **`args = _construir_parser().parse_args()`** — encadena: crea el
  parser y parsea `sys.argv`. `args` es un `Namespace` con atributos
  `args.ruta`, `args.anios`, `args.sin_guardar`.
- **`not args.sin_guardar`** — invierte el flag: si el usuario pidió
  *no* guardar, `persistir_disco = False`.
- **Desempaquetado** — `dfs_anio, df_consolidado = ejecutar_pipeline(...)`
  asigna cada elemento de la tupla retornada a una variable distinta.
- **`df_consolidado.groupby("periodo_ia")["puntaje_saberpro_generico"].agg(["count","mean","std"]).round(2)`** —
  cadena de métodos:
  - `.groupby("col")` agrupa por una columna.
  - `["columna"]` selecciona la columna numérica a resumir.
  - `.agg([...])` aplica múltiples agregaciones.
  - `.round(2)` redondea a dos decimales.

---

## Apéndice A — Glosario de operadores y construcciones

| Símbolo / construcción | Significado |
|---|---|
| `=` | Asignación. |
| `==`, `!=` | Igualdad / desigualdad. |
| `<`, `<=`, `>`, `>=` | Comparaciones. |
| `and`, `or`, `not` | Booleanos escalares. |
| `&`, `\|`, `~` | Booleanos vectoriales (numpy/pandas). |
| `if … else …` | Expresión condicional ternaria. |
| `for … in …` | Bucle iterativo. |
| `lambda x: …` | Función anónima. |
| `def f(...): ...` | Definición de función. |
| `return` | Devuelve un valor. |
| `raise` | Lanza una excepción. |
| `try / except` | Maneja excepciones. |
| `continue` | Salta a la siguiente iteración. |
| `from … import …` | Importa nombres específicos. |
| `f"…"` | Cadena formateada. |
| `r"…"` | Raw string (no interpreta `\n` etc.). |
| `[a, b]` | Literal de lista. |
| `(a, b)` | Literal de tupla. |
| `{k: v}` | Literal de diccionario. |
| `[x for x in y]` | Comprensión de lista. |
| `{k: v for k, v in z}` | Comprensión de diccionario. |
| `_` | Identificador convencional "irrelevante". |
| `__name__` | Variable especial del intérprete. |

---

## Apéndice B — Tabla resumen de funciones definidas

| Función | Entradas | Retorno | Propósito |
|---|---|---|---|
| `_normalizar_texto` | `object` | `str` | Mayúsculas, sin tildes, espacios simples. |
| `_registrar` | `str` | `None` | Log con timestamp. |
| `_a_numerico` | `Series` | `Series` | Convierte a número tolerando coma. |
| `montar_drive_si_aplica` | `str` | `bool` | Monta Drive si se está en Colab. |
| `_detectar_formato` | `str` | `(str, str)` | Detecta separador y encoding. |
| `_leer_columnas_disponibles` | `str, str, str` | `list[str]` | Devuelve nombres de columnas del archivo. |
| `leer_archivo_anio` | `str, int` | `DataFrame` | Carga sólo las 17 columnas requeridas. |
| `transformar_id_y_modulos` | `DataFrame` | `DataFrame` | Rename de ID y módulos. |
| `construir_periodo_ia` | `DataFrame` | `DataFrame` | Dummy 0/1 por cohorte. |
| `construir_puntaje_generico` | `DataFrame` | `DataFrame` | Promedio de los 5 módulos. |
| `construir_edad` | `DataFrame` | `DataFrame` | Calcula edad y elimina fecha. |
| `construir_genero` | `DataFrame` | `DataFrame` | F=0/M=1, elimina fuente. |
| `construir_estrato` | `DataFrame` | `DataFrame` | Escala 1-6, elimina fuente. |
| `construir_nivel_educ_padre` | `DataFrame` | `DataFrame` | Ordinal 1-7, elimina fuente. |
| `construir_estu_trabaja` | `DataFrame` | `DataFrame` | Dummy, elimina fuente. |
| `construir_cabeza_familia` | `DataFrame` | `DataFrame` | Proxy, elimina fuente. |
| `construir_jornada` | `DataFrame` | `DataFrame` | Aproximada con metodología. |
| `construir_internet` | `DataFrame` | `DataFrame` | Dummy, elimina fuente. |
| `construir_area_residencia` | `DataFrame` | `DataFrame` | Urbano=1, elimina fuente. |
| `construir_naturaleza_ies` | `DataFrame` | `DataFrame` | Privada=1, elimina fuente. |
| `_canonizar_departamento` | `object` | `Optional[str]` | Nombre canónico. |
| `construir_departamento_y_distancia` | `DataFrame` | `DataFrame` | Código 0-32 + km. |
| `construir_todas_las_variables` | `DataFrame` | `DataFrame` | Orquesta las 14 construcciones. |
| `limpiar` | `DataFrame` | `DataFrame` | Rangos, filtros, duplicados. |
| `seleccionar_variables_finales` | `DataFrame` | `DataFrame` | Reordena a las 22 finales. |
| `procesar_anio` | `str, int` | `DataFrame` | Pipeline para un año. |
| `consolidar` | `Dict[int, DataFrame]` | `DataFrame` | Concatena los anuales. |
| `persistir` | `str, dict, DataFrame` | `str` | Escribe CSV en disco. |
| `ejecutar_pipeline` | `str, Iterable[int], bool` | `(dict, DataFrame)` | Punto de entrada. |
| `_construir_parser` | — | `ArgumentParser` | Define la CLI con `argparse`. |
