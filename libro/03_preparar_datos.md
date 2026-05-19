# Capítulo 3 — `preparar_datos.py`

> Recorrido palabra por palabra del primer módulo del proyecto.

---

## 3.1 Propósito del archivo

Este módulo automatiza la **fase de preparación de datos**:

1. Conecta opcionalmente con Google Drive.
2. Carga los 4 archivos `Examen_Saber_Pro_Genericas_<año>.txt` (2021,
   2022, 2023, 2024) descargados de DataICFES, leyendo **sólo** las 19
   columnas que el estudio necesita.
3. Construye las 22 variables operacionalizadas en la Tabla 2 del
   documento de la investigación, eliminando cada columna cruda apenas
   se usa (*drop incremental*).
4. Limpia rangos, duplicados y faltantes.
5. Distingue dos conjuntos de variables por finalidad analítica:
   `VARIABLES_DESCRIPTIVO` (Tabla 3) y `VARIABLES_MODELO` (Tabla 2).
6. Produce un dataframe por año (`df_2021…df_2024`) y un consolidado
   final.

Es el **fundamento** sobre el que descansan los otros dos módulos
(`analisis_descriptivo.py` y `regresion_mco.py`).

---

## 3.2 Cabecera y declaraciones globales

### Docstring

El archivo abre con una cadena entre `"""…"""` que describe el módulo.
Esto es un **docstring**: una cadena que actúa como documentación. Se
accede con `preparar_datos.__doc__`.

### `from __future__ import annotations`

- **`from`** — palabra reservada para importar un nombre específico de
  un módulo.
- **`__future__`** — módulo estándar que expone funcionalidades del
  lenguaje que serán predeterminadas en futuras versiones.
- **`annotations`** — bandera que hace que **todas** las anotaciones de
  tipo se evalúen como cadenas (de forma diferida). Permite escribir
  anotaciones que refieren a clases definidas más abajo sin causar
  `NameError`.

### Imports de la stdlib

```python
import argparse
import os
import re
import sys
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple
```

| Línea | Qué importa y para qué |
|---|---|
| `import argparse` | Para construir la CLI (`--ruta`, `--anios`, etc.). |
| `import os` | Rutas, directorios, comprobaciones de existencia. |
| `import re` | Expresiones regulares (extraer dígitos, comprimir espacios). |
| `import sys` | Detectar Colab (`"google.colab" in sys.modules`) y ejecutar pip. |
| `import unicodedata` | Quitar acentos. |
| `from datetime import datetime` | Hora actual para logs. |
| `from typing import …` | Anotaciones de tipo (`Dict`, `List`, etc.). |

### Imports de terceros

```python
import numpy as np
import pandas as pd
```

- **`import numpy as np`** — `numpy` con alias `np`.
- **`import pandas as pd`** — `pandas` con alias `pd`.

---

## 3.3 Bloque 1 — Constantes

### Ruta del archivo y ruta por defecto

```python
PATRON_ARCHIVO: str = "Examen_Saber_Pro_Genericas_{anio}.txt"
RUTA_DEFECTO: str   = "/content/drive/MyDrive/IA_EDUCACION_SUPERIOR"
```

- **Anotación de tipo `: str`** — declarativa, ignorada en runtime.
- **MAYÚSCULAS** — convención: indica que es una constante.
- **`"…{anio}…"`** — plantilla; el método `.format(anio=2021)` sustituye
  `{anio}` por `2021`.
- **`/content/drive/MyDrive/...`** — ruta donde Google Drive monta
  "Mi unidad" cuando se ejecuta `drive.mount("/content/drive")`.

### Años de análisis

```python
ANIOS: List[int]        = [2021, 2022, 2023, 2024]
ANIOS_PREVIO: List[int] = [2021, 2022]
ANIOS_IA: List[int]     = [2023, 2024]
```

- **`List[int]`** — lista de enteros (anotación).
- `ANIOS_PREVIO` define la cohorte pre-IA (`periodo_ia = 0`),
  `ANIOS_IA` la cohorte post-IA (`periodo_ia = 1`).

### Separadores y codificaciones

```python
SEPARADORES_CANDIDATOS: Tuple[str, ...] = ("¦", "|", "\t", ";", ",")
CODIFICACIONES_CANDIDATAS: Tuple[str, ...] = ("utf-8", "latin-1", "cp1252")
```

- **`Tuple[str, ...]`** — tupla de longitud variable, todos `str`.
- Los archivos del ICFES han variado de separador según el año;
  estos cinco cubren los casos conocidos.
- `"\t"` representa el carácter tabulación.

### Paquetes que requiere el módulo

```python
PAQUETES_REQUERIDOS: Tuple[str, ...] = ("pandas", "numpy")
```

Lista usada por `instalar_dependencias_si_aplica()` (ver más abajo).

### Mapeo de columnas crudas

```python
COLS_REQUERIDAS: List[str] = [
    "estu_consecutivo",
    "mod_lectura_critica_punt",
    ...
    "estu_inst_municipio",
]
```

Las **19 columnas** se cargan con `usecols` en `read_csv`. Sus nombres
proceden del *Diccionario Saber Pro* del ICFES (sección 2, período
2021-2024).

### Codificación de departamentos (Tabla 1)

```python
DEPARTAMENTOS: Dict[str, Tuple[int, float]] = {
    "BOGOTA":              (0,    0.0),
    "AMAZONAS":            (1, 1100.0),
    ...
}
```

- **`Dict[str, Tuple[int, float]]`** — diccionario con claves `str` y
  valores `(int, float)`.
- Cada entrada agrupa **dos atributos** del departamento:
  - código numérico (0 = Bogotá D.C., referencia; 1..32 alfabético).
  - distancia oficial a Bogotá en km (IGAC/INVIAS).
- Se usan dos comprensiones para extraer cada atributo cuando se
  construye `departamento` y `distancia_bogota_km`.

### Capitales departamentales

```python
CAPITALES: Dict[str, str] = {
    "BOGOTA":             "BOGOTA D.C.",
    "AMAZONAS":           "LETICIA",
    ...
}
```

Se usa para clasificar `tipo_municipio` (0 = Bogotá, 1 = capital de
otro dpto, 2 = resto).

### Aliases de departamentos

```python
ALIAS_DEPARTAMENTOS: Dict[str, str] = {
    "BOGOTA D.C.":               "BOGOTA",
    "VALLE DEL CAUCA":           "VALLE",
    ...
}
```

Mapea variantes (con tildes, abreviaciones, nombres oficiales largos)
al nombre canónico. Lo usa la función `_canonizar_departamento`.

### Variables por finalidad analítica

```python
VARIABLES_DESCRIPTIVO: List[str] = [...]
VARIABLES_MODELO: List[str]      = [...]
VARIABLES_FINALES = (
    VARIABLES_DESCRIPTIVO
    + [c for c in VARIABLES_MODELO if c not in VARIABLES_DESCRIPTIVO]
)
```

- **`+` entre listas** — concatenación.
- **Comprensión de lista filtrada** — produce la unión ordenada
  (sin duplicados).
- El resultado son **25 columnas** finales que el dataframe conserva.

### Lista de módulos genéricos

```python
MODULOS_GENERICOS: List[str] = [
    "punt_lectura_critica",
    "punt_razona_cuant",
    "punt_competen_ciud",
    "punt_comuni_escrita",
    "punt_ingles",
]
```

Los cinco puntajes cuyo promedio define `puntaje_saberpro_generico`.

---

## 3.4 Bloque 2 — Utilidades

### `_normalizar_texto(valor)`

```python
def _normalizar_texto(valor: object) -> str:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto)
```

| Elemento | Significado |
|---|---|
| `_normalizar_texto` | Nombre privado (guion bajo inicial). |
| `valor: object` | Acepta cualquier tipo (`object` es la raíz). |
| `-> str` | Retorna cadena. |
| `valor is None` | Comparación de identidad con `None`. |
| `isinstance(valor, float)` | `True` si `valor` es flotante. |
| `pd.isna(valor)` | Detecta `NaN`, `None`, `pd.NA`, `NaT`. |
| `str(valor)` | Castea a cadena. |
| `.strip()` | Quita espacios al inicio/final. |
| `.upper()` | Mayúsculas. |
| `unicodedata.normalize("NFKD", t)` | Descompone acentos. |
| `unicodedata.combining(c)` | >0 si `c` es marca combinante. |
| `"".join(generator)` | Concatena con `""`. |
| `re.sub(r"\s+", " ", t)` | Reemplaza espacios duplicados por uno. |
| `r"\s+"` | *Raw string*: `\s` = espacio en blanco, `+` = uno o más. |

### `_registrar(mensaje)`

```python
def _registrar(mensaje: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")
```

- **`-> None`** — no retorna nada (efecto secundario: print).
- **`datetime.now()`** — instancia con la hora actual.
- **`.strftime("%H:%M:%S")`** — formatea como `HH:MM:SS`.
- **`f"..."`** — *f-string*: interpola las expresiones entre llaves.

### `_a_numerico(serie)`

```python
def _a_numerico(serie: pd.Series) -> pd.Series:
    if serie.dtype.kind in "iuf":
        return serie
    return pd.to_numeric(
        serie.astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )
```

- **`serie.dtype.kind`** — un carácter codificando el tipo:
  - `i` = entero con signo
  - `u` = entero sin signo
  - `f` = flotante
- **`in "iuf"`** — pertenencia de carácter en cadena.
- **`serie.astype(str)`** — castea a cadena (para usar métodos `.str`).
- **`.str.replace(",", ".", regex=False)`** — sustitución literal de
  coma decimal (formato latino) por punto.
- **`pd.to_numeric(..., errors="coerce")`** — convierte a número;
  los no convertibles → `NaN`.

---

## 3.5 Bloque 3 — Soporte para Google Colab

### `en_colab()`

```python
def en_colab() -> bool:
    return "google.colab" in sys.modules or os.path.exists("/content")
```

- **`-> bool`** — retorna booleano.
- **`"google.colab" in sys.modules`** — `True` si el módulo `google.colab`
  ha sido cargado en este proceso.
- **`os.path.exists("/content")`** — `True` si existe la carpeta
  `/content` (siempre la crea Colab en su VM).
- **`or`** — basta con que una sea `True`.

### `instalar_dependencias_si_aplica(paquetes)`

```python
def instalar_dependencias_si_aplica(
    paquetes: Iterable[str] = PAQUETES_REQUERIDOS,
) -> None:
    if not en_colab():
        return
    import importlib.util
    import subprocess
    faltan = [p for p in paquetes
              if importlib.util.find_spec(p.replace("-", "_")) is None]
    if faltan:
        _registrar(f"Instalando paquetes faltantes en Colab: {faltan}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", *faltan]
        )
```

| Elemento | Significado |
|---|---|
| `paquetes: Iterable[str]` | Cualquier objeto recorrible de cadenas. |
| `= PAQUETES_REQUERIDOS` | Valor por defecto. |
| `import` dentro de la función | Lazy import: sólo se importa cuando se ejecuta la función. |
| `importlib.util.find_spec(nombre)` | Comprueba si un módulo puede importarse sin importarlo. |
| `p.replace("-", "_")` | Algunos paquetes tienen guion en pip pero guion bajo en import (raro). |
| `if … is None` | El spec es `None` si el módulo no se encuentra. |
| `subprocess.check_call(args)` | Ejecuta un comando externo; lanza excepción si falla. |
| `sys.executable` | Ruta del intérprete Python actual. |
| `["-m", "pip", "install", "-q", *faltan]` | Argumentos de pip. `-q` = quiet. `*faltan` desempaqueta. |

### `montar_drive_si_aplica(punto_montaje)`

```python
def montar_drive_si_aplica(punto_montaje: str = "/content/drive") -> bool:
    if not en_colab():
        return False
    try:
        from google.colab import drive  # type: ignore
    except ImportError:
        return False
    if not os.path.ismount(punto_montaje):
        _registrar(f"Montando Google Drive en {punto_montaje} ...")
        drive.mount(punto_montaje, force_remount=False)
    return True
```

| Elemento | Significado |
|---|---|
| `try / except ImportError` | Manejo controlado: si no se puede importar `google.colab`, retornar `False`. |
| `# type: ignore` | Suprime el aviso del verificador de tipos (mypy). |
| `os.path.ismount(p)` | `True` si la ruta es un punto de montaje. |
| `drive.mount(p, force_remount=False)` | Monta Drive; no vuelve a autenticar si ya está montado. |

### `setup_colab()`

```python
def setup_colab() -> None:
    instalar_dependencias_si_aplica()
    montar_drive_si_aplica()
```

Atajo que combina las dos funciones anteriores. Lo invoca
`ejecutar_pipeline` cuando `ruta_proyecto=None`.

---

## 3.6 Bloque 4 — Lectura robusta de archivos

### `_detectar_formato(ruta)`

```python
def _detectar_formato(ruta: str) -> Tuple[str, str]:
    for codificacion in CODIFICACIONES_CANDIDATAS:
        for separador in SEPARADORES_CANDIDATOS:
            try:
                muestra = pd.read_csv(
                    ruta, sep=separador, encoding=codificacion,
                    nrows=5, on_bad_lines="skip", engine="python",
                )
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
            if muestra.shape[1] > 1:
                return separador, codificacion
    raise ValueError(...)
```

| Elemento | Significado |
|---|---|
| Bucle anidado | Prueba **cada combinación** de encoding × separador. |
| `try / except (X, Y)` | Captura múltiples excepciones con una sola cláusula. |
| `continue` | Salta a la siguiente iteración. |
| `pd.read_csv(..., nrows=5)` | Lee sólo cinco filas (sondeo barato). |
| `on_bad_lines="skip"` | Ignora líneas mal formadas. |
| `engine="python"` | Motor más permisivo (necesario para separadores no estándar). |
| `muestra.shape[1] > 1` | Si la detección produjo >1 columna, el separador es correcto. |
| `return separador, codificacion` | Retorno múltiple via tupla implícita. |
| `raise ValueError(...)` | Lanza una excepción si ninguna combinación funcionó. |

### `_leer_columnas_disponibles(ruta, sep, enc)`

```python
def _leer_columnas_disponibles(ruta: str, sep: str, enc: str) -> List[str]:
    return list(
        pd.read_csv(ruta, sep=sep, encoding=enc,
                    nrows=0, engine="python").columns
    )
```

- **`nrows=0`** — lee CERO filas, sólo la cabecera. Truco eficiente
  para inspeccionar las columnas sin gastar memoria.
- **`list(df.columns)`** — convierte el `Index` de pandas en lista.

### `leer_archivo_anio(ruta_proyecto, anio)`

```python
def leer_archivo_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:
    nombre = PATRON_ARCHIVO.format(anio=anio)
    ruta = os.path.join(ruta_proyecto, nombre)
    if not os.path.isfile(ruta):
        raise FileNotFoundError(...)
    sep, enc = _detectar_formato(ruta)
    cols_archivo = _leer_columnas_disponibles(ruta, sep, enc)
    mapa_lower = {c.lower(): c for c in cols_archivo}
    usecols = [mapa_lower[c] for c in COLS_REQUERIDAS if c in mapa_lower]
    _registrar(f"...")
    df = pd.read_csv(
        ruta, sep=sep, encoding=enc, usecols=usecols,
        on_bad_lines="skip", engine="python",
    )
    df.columns = [c.lower() for c in df.columns]
    df["anio"] = anio
    for col in COLS_REQUERIDAS:
        if col not in df.columns:
            df[col] = np.nan
    return df
```

| Elemento | Significado |
|---|---|
| `.format(anio=anio)` | Sustituye `{anio}` por el año concreto. |
| `os.path.join(...)` | Combina partes de ruta. |
| `os.path.isfile(...)` | Comprueba existencia. |
| `raise FileNotFoundError` | Detiene el pipeline con un mensaje claro. |
| Comprensión de dict `{c.lower(): c ...}` | Mapeo "lowercase → nombre original". Permite emparejar columnas independientemente de cómo vengan rotuladas. |
| Comprensión de lista filtrada `[mapa_lower[c] for c in ... if c in mapa_lower]` | Sólo carga las columnas que el archivo trae. |
| `usecols=usecols` | Le dice a pandas que cargue **solo** esas columnas: ahorra mucha memoria con archivos grandes del ICFES. |
| `df.columns = [c.lower() for c in df.columns]` | Renombra todas las columnas a minúsculas. |
| `df["anio"] = anio` | Crea columna constante con el año. |
| Bucle final | Asegura **esquema constante**: si un año no trajo una columna, queda como `NaN`. |

---

## 3.7 Bloque 5 — Construcción de variables

Este bloque tiene 14 funciones `construir_*`, una por variable
operacionalizada en el documento.

### Patrón general

Todas siguen este patrón:

```python
def construir_X(df: pd.DataFrame) -> pd.DataFrame:
    df["nueva"] = transformacion(df["columna_cruda"])
    df = df.drop(columns=["columna_cruda"])
    return df
```

**Por qué se reasigna y retorna:** `df.drop(columns=[...])` no modifica
el dataframe original (no es *inplace*), retorna una copia sin esas
columnas. Por eso reasignamos a `df` y luego retornamos.

### `transformar_id_y_modulos(df)`

```python
renombres = {
    "estu_consecutivo":          "id_estudiante",
    "mod_lectura_critica_punt":  "punt_lectura_critica",
    ...
}
df = df.rename(columns=renombres)
for col in MODULOS_GENERICOS:
    df[col] = _a_numerico(df[col])
return df
```

- **`df.rename(columns=dict)`** — renombra columnas según el dict.
- Convierte los 5 módulos a numérico antes de seguir.

### `construir_periodo_ia(df)`

```python
df["periodo_ia"] = df["anio"].apply(
    lambda a: 0 if a in ANIOS_PREVIO else (1 if a in ANIOS_IA else np.nan)
).astype("Int64")
return df
```

| Elemento | Significado |
|---|---|
| `.apply(func)` | Aplica `func` elemento por elemento de la Series. |
| `lambda a: …` | Función anónima de un argumento. |
| Ternario anidado | `0` si pre-IA, `1` si post-IA, `NaN` en cualquier otro caso. |
| `.astype("Int64")` | Entero **nullable** (admite `pd.NA`). |

### `construir_puntaje_generico(df)`

```python
df["puntaje_saberpro_generico"] = (
    df[MODULOS_GENERICOS].mean(axis=1, skipna=True)
)
return df
```

- **`df[lista]`** — selecciona las cinco columnas como sub-DataFrame.
- **`.mean(axis=1)`** — promedio **por fila** (eje 1, no por columna).
- **`skipna=True`** — ignora NaNs en el promedio.

### `construir_edad(df)`

```python
fecha = pd.to_datetime(
    df["estu_fechanacimiento"], errors="coerce", dayfirst=True,
)
df["edad"] = (df["anio"] - fecha.dt.year).astype("Float64")
df.loc[(df["edad"] < 15) | (df["edad"] > 80), "edad"] = np.nan
df = df.drop(columns=["estu_fechanacimiento"])
return df
```

| Elemento | Significado |
|---|---|
| `pd.to_datetime(..., errors="coerce", dayfirst=True)` | Parsea fechas; las no parseables → `NaT`. `dayfirst=True` interpreta `DD/MM/AAAA`. |
| `fecha.dt.year` | Accessor `.dt` para fechas; extrae el año. |
| Resta vectorial `df["anio"] - fecha.dt.year` | Operación elemento a elemento. |
| `.astype("Float64")` | Flotante **nullable**. |
| Indexación `df.loc[mascara, "edad"] = np.nan` | Asignación selectiva. `mascara` es booleana. |
| `\|` | OR vectorial. **Paréntesis obligatorios** por precedencia. |
| `df.drop(columns=["estu_fechanacimiento"])` | **¡Aquí ocurre el drop incremental!** La fuente desaparece tan pronto se usa. |

### Funciones basadas en `.map(dict)`

`construir_genero`, `construir_estrato`, `construir_nivel_educ_padre`,
`construir_estu_trabaja`, `construir_cabeza_familia`,
`construir_internet` siguen este patrón:

```python
norm = df["columna_raw"].apply(_normalizar_texto)
df["nueva"] = norm.map({clave: valor, ...}).astype(...)
df = df.drop(columns=["columna_raw"])
return df
```

- **`.map(dict)`** — traduce cada valor según el dict. Los no
  encontrados → `NaN`. Es lo que silenciosamente convierte `"No sabe"`
  en `NaN` para `nivel_educ_padre`.

### `construir_estrato(df)` — extracción con regex

```python
extraido = (
    df["fami_estratovivienda"].astype(str)
    .str.extract(r"(\d)", expand=False).astype("Float64")
)
extraido = extraido.where(extraido.between(1, 6))
df["estrato"] = extraido
df = df.drop(columns=["fami_estratovivienda"])
```

| Elemento | Significado |
|---|---|
| `.str.extract(r"(\d)", expand=False)` | Extrae el primer dígito. `expand=False` retorna Series (no DataFrame). |
| `.where(cond)` | Conserva los valores donde la condición es True; los demás → `NaN`. |
| `.between(1, 6)` | Máscara True si valor ∈ [1, 6]. |

### `construir_jornada(df)` y `construir_area_residencia(df)` — `np.where` anidado

```python
df["jornada"] = np.where(
    norm.str.contains("DISTANCIA|VIRTUAL", regex=True), 1,
    np.where(norm.str.contains("PRESENCIAL"), 0, np.nan),
)
df["jornada"] = pd.array(df["jornada"], dtype="Float64").astype("Int64")
```

| Elemento | Significado |
|---|---|
| `np.where(cond, si, no)` | Equivalente vectorial del ternario. |
| **`np.where` anidado** | Modela tres estados (`1` / `0` / `NaN`). |
| `serie.str.contains("PAT", regex=True)` | Máscara con regex. El `\|` dentro del patrón es OR de regex (no booleano). |
| `pd.array(..., dtype="Float64")` | Crea un array nullable. Hace falta el paso intermedio Float→Int para conservar los NaN. |

### `construir_naturaleza_ies(df)`

```python
df["naturaleza_ies"] = np.where(
    norm.str.startswith("NO OFICIAL"), 1,
    np.where(norm.str.startswith("OFICIAL") | norm.str.contains("REGIMEN ESPECIAL"),
             0, np.nan),
)
```

- **`norm.str.startswith("NO OFICIAL")`** — máscara `True` si empieza
  con "NO OFICIAL" (categorías "NO OFICIAL - CORPORACIÓN", etc.).
- **`mask1 | mask2`** — OR booleano vectorial entre dos máscaras.

### `_canonizar_departamento(valor)`

```python
def _canonizar_departamento(valor: object) -> Optional[str]:
    texto = _normalizar_texto(valor)
    if not texto:
        return None
    if texto in ALIAS_DEPARTAMENTOS:
        return ALIAS_DEPARTAMENTOS[texto]
    if texto in DEPARTAMENTOS:
        return texto
    for canon in DEPARTAMENTOS:
        if texto.startswith(canon) or canon in texto:
            return canon
    return None
```

| Estrategia | Línea | Qué hace |
|---|---|---|
| 1 | `if texto in ALIAS_DEPARTAMENTOS` | Mapea variantes oficiales largas o con tildes. |
| 2 | `if texto in DEPARTAMENTOS` | Coincidencia exacta con clave canónica. |
| 3 | Bucle `for canon in DEPARTAMENTOS` | Coincidencia parcial (prefijo o subcadena). |
| 4 | `return None` | Si nada matchea. |

- **`for canon in DEPARTAMENTOS`** — iterar un dict produce sus **claves**
  en orden de inserción (garantizado desde Python 3.7).
- **`texto.startswith(canon)`** — `True` si `texto` comienza con `canon`.
- **`canon in texto`** — `True` si `canon` es subcadena de `texto`.

### `construir_departamento_y_distancia(df)`

```python
canon = df["estu_inst_departamento"].apply(_canonizar_departamento)
df["departamento_nombre"] = canon
df["departamento"] = canon.map(
    {n: c for n, (c, _) in DEPARTAMENTOS.items()}
).astype("Int64")
df["distancia_bogota_km"] = canon.map(
    {n: d for n, (_, d) in DEPARTAMENTOS.items()}
).astype("Float64")
df = df.drop(columns=["estu_inst_departamento"])
```

| Elemento | Significado |
|---|---|
| `canon.map({n: c for n, (c, _) in DEPARTAMENTOS.items()})` | Combinación de `.map()` con comprensión de dict que **desempaqueta** la tupla `(c, d)` y conserva sólo el código. |
| `(c, _)` | Desempaquetado: `_` = "valor que no me interesa". |
| Una columna por atributo | Aprovecha el mismo `DEPARTAMENTOS` para producir dos columnas distintas. |

### `construir_identificadores_fe(df)` y `construir_tipo_municipio(df)`

```python
df = df.rename(columns={
    "inst_cod_institucion": "cod_ies",
    "estu_inst_municipio":  "municipio_ies",
})
df["cod_ies"] = pd.to_numeric(df["cod_ies"], errors="coerce").astype("Int64")
```

```python
mun_norm = df["municipio_ies"].apply(_normalizar_texto)
capital_esperada = df["departamento_nombre"].map(
    {n: _normalizar_texto(c) for n, c in CAPITALES.items()}
)
es_bogota = df["departamento_nombre"].eq("BOGOTA")
es_capital_otro = (~es_bogota) & (mun_norm == capital_esperada)
df["tipo_municipio"] = np.where(
    es_bogota, 0,
    np.where(es_capital_otro, 1, 2),
)
```

| Elemento | Significado |
|---|---|
| `df["x"].eq("BOGOTA")` | Equivalente a `df["x"] == "BOGOTA"` pero más explícito. |
| `~es_bogota` | Negación booleana vectorial. |
| `(~es_bogota) & (mun_norm == capital_esperada)` | Es capital de otro dpto: no es Bogotá Y el municipio coincide con la capital esperada. |
| `np.where(es_bogota, 0, np.where(es_capital_otro, 1, 2))` | 0 / 1 / 2 según la jerarquía. |

### `construir_todas_las_variables(df)`

```python
def construir_todas_las_variables(df):
    df = transformar_id_y_modulos(df)
    df = construir_periodo_ia(df)
    df = construir_puntaje_generico(df)
    df = construir_edad(df)                 # drop estu_fechanacimiento
    df = construir_genero(df)               # drop estu_genero
    df = construir_estrato(df)              # drop fami_estratovivienda
    df = construir_nivel_educ_padre(df)     # drop fami_educacionpadre
    df = construir_estu_trabaja(df)         # drop estu_horassemanatrabaja
    df = construir_cabeza_familia(df)       # drop estu_pagomatriculapadres
    df = construir_jornada(df)              # drop estu_metodo_prgm
    df = construir_internet(df)             # drop fami_tieneinternet
    df = construir_area_residencia(df)      # drop estu_areareside
    df = construir_naturaleza_ies(df)       # drop inst_origen
    df = construir_departamento_y_distancia(df)  # drop estu_inst_departamento
    df = construir_identificadores_fe(df)   # rename
    df = construir_tipo_municipio(df)
    return df
```

Orquesta las 16 transformaciones **en orden**. Al terminar, ninguna
columna cruda original sobrevive (excepto las renombradas
`id_estudiante`, los puntajes, `cod_ies` y `municipio_ies`).

---

## 3.8 Bloque 6 — Limpieza

### `limpiar(df)`

```python
def limpiar(df):
    n_inicial = len(df)

    # 1) Rango Saber Pro
    for col in MODULOS_GENERICOS + ["puntaje_saberpro_generico"]:
        fuera = ~df[col].between(0, 300)
        df.loc[fuera & df[col].notna(), col] = np.nan

    # 2) Sin variable dependiente
    df = df[df["puntaje_saberpro_generico"].notna()].copy()

    # 3) Sin departamento
    df = df[df["departamento"].notna()].copy()

    # 4) Duplicados
    df = df.drop_duplicates(subset=["id_estudiante", "anio"], keep="first")

    # 5) Reindexar
    df = df.reset_index(drop=True)

    _registrar(f"Limpieza: {n_inicial:,} → {len(df):,} filas (...)")
    return df
```

| Operación | Detalle |
|---|---|
| `~df[col].between(0, 300)` | `~` es NOT vectorial. Marca los valores fuera del rango oficial. |
| `mask1 & mask2` | AND vectorial. |
| `df.loc[m, col] = np.nan` | Asignación condicional: NaN en celdas fuera de rango. |
| `df[df["x"].notna()]` | Filtra filas con valor no faltante. |
| `.copy()` | Evita `SettingWithCopyWarning`. |
| `.drop_duplicates(subset=[...], keep="first")` | Elimina duplicados. |
| `.reset_index(drop=True)` | Reinicia el índice. |
| `len(df):,` | Formatea con separador de miles. |

### `seleccionar_variables_finales(df)`

```python
def seleccionar_variables_finales(df):
    return df[VARIABLES_FINALES].copy()
```

- **`df[lista]`** — indexa por lista de columnas: selecciona y
  reordena en una sola operación.
- **`.copy()`** — copia independiente.

---

## 3.9 Bloque 7 — Procesamiento y consolidación

### `procesar_anio(ruta_proyecto, anio)`

```python
def procesar_anio(ruta_proyecto, anio):
    crudo = leer_archivo_anio(ruta_proyecto, anio)
    construido = construir_todas_las_variables(crudo)
    final = seleccionar_variables_finales(construido)
    final = limpiar(final)
    _registrar(f"df_{anio} listo: ...")
    return final
```

Pipeline secuencial: cada función recibe el resultado de la anterior.

### `consolidar(dfs)`

```python
def consolidar(dfs):
    df = pd.concat(dfs.values(), axis=0, ignore_index=True)
    df = df[VARIABLES_FINALES].copy()
    _registrar(f"df_consolidado: ...")
    return df
```

| Elemento | Significado |
|---|---|
| `dfs.values()` | Vista de los valores del dict (los dataframes anuales). |
| `pd.concat([...], axis=0)` | Apila **verticalmente** (filas). |
| `ignore_index=True` | Reindexa 0..n-1. |
| `df[VARIABLES_FINALES]` | Reordena las columnas. |

### `persistir(ruta_proyecto, dfs, df_consolidado)`

```python
def persistir(ruta_proyecto, dfs, df_consolidado):
    salida = os.path.join(ruta_proyecto, "procesados")
    os.makedirs(salida, exist_ok=True)
    for anio, df in dfs.items():
        df.to_csv(os.path.join(salida, f"df_{anio}.csv"),
                  index=False, encoding="utf-8-sig")
    df_consolidado.to_csv(os.path.join(salida, "df_consolidado.csv"),
                          index=False, encoding="utf-8-sig")
    return salida
```

| Elemento | Significado |
|---|---|
| `os.makedirs(p, exist_ok=True)` | Crea recursivamente; no falla si ya existe. |
| `df.to_csv(ruta, index=False, encoding="utf-8-sig")` | Exporta CSV. `utf-8-sig` = UTF-8 con BOM, compatible con Excel. |

---

## 3.10 Bloque 8 — Orquestador

### `ejecutar_pipeline(ruta_proyecto, anios, persistir_disco)`

```python
def ejecutar_pipeline(
    ruta_proyecto: Optional[str] = None,
    anios: Iterable[int] = ANIOS,
    persistir_disco: bool = True,
) -> Tuple[Dict[int, pd.DataFrame], pd.DataFrame]:
    _registrar("== INICIO DEL PIPELINE ==")
    if ruta_proyecto is None:
        setup_colab()
        ruta_proyecto = RUTA_DEFECTO
    if not os.path.isdir(ruta_proyecto):
        raise FileNotFoundError(...)
    dfs: Dict[int, pd.DataFrame] = {}
    for anio in anios:
        _registrar(f"-- Procesando año {anio} --")
        dfs[anio] = procesar_anio(ruta_proyecto, anio)
    df_consolidado = consolidar(dfs)
    if persistir_disco:
        persistir(ruta_proyecto, dfs, df_consolidado)
    _registrar("== FIN DEL PIPELINE ==")
    return dfs, df_consolidado
```

| Elemento | Significado |
|---|---|
| `Optional[str] = None` | Si `None`, usa el comportamiento Colab. |
| `if ruta_proyecto is None:` | Comparación de identidad con `None` (idiomático). |
| `setup_colab()` | Monta Drive e instala deps si aplica. |
| `Tuple[Dict[int, DataFrame], DataFrame]` | Anotación de retorno: tupla con dict y DataFrame. |
| `return dfs, df_consolidado` | Retorno múltiple como tupla. |

---

## 3.11 Bloque 9 — CLI con `argparse`

### `_construir_parser()`

```python
def _construir_parser():
    parser = argparse.ArgumentParser(
        description="Pipeline de preparación de datos Saber Pro 2021-2024.",
    )
    parser.add_argument("--ruta", "-r", default=None, help="...")
    parser.add_argument("--anios", "-a", nargs="+", type=int, default=ANIOS,
                        help="...")
    parser.add_argument("--sin-guardar", action="store_true", help="...")
    return parser
```

Cubierto en el [Capítulo 2, §2.2.4](./02_librerias_clave.md#224-argparse).

### Bloque `if __name__ == "__main__"`

```python
if __name__ == "__main__":
    args = _construir_parser().parse_args()
    dfs_anio, df_consolidado = ejecutar_pipeline(
        ruta_proyecto=args.ruta,
        anios=args.anios,
        persistir_disco=not args.sin_guardar,
    )
    print("\n== Resumen ==")
    print(df_consolidado.groupby("periodo_ia")["puntaje_saberpro_generico"]
          .agg(["count", "mean", "std"]).round(2))
```

| Elemento | Significado |
|---|---|
| `__name__ == "__main__"` | `True` sólo cuando se ejecuta directamente. |
| `parser.parse_args()` | Lee `sys.argv` y devuelve un `Namespace`. |
| `not args.sin_guardar` | Invierte el flag: si se pidió "sin guardar", `persistir_disco = False`. |
| Encadenamiento `.groupby(...)[col].agg([...]).round(2)` | Agrupa por `periodo_ia`, agrega tres estadísticos sobre el puntaje, redondea. |

---

## 3.12 Recapitulación

Después de leer este capítulo deberías poder:

1. Explicar qué hace **cada función** del módulo.
2. Justificar **por qué** cada columna cruda se elimina cuando se hace.
3. Identificar qué **parámetro** o **operador** se usa en cada línea.
4. Modificar el código para añadir un control nuevo siguiendo el patrón
   `construir_*` + agregar a `VARIABLES_MODELO`.

Pasa al [Capítulo 4 — `analisis_descriptivo.py`](./04_analisis_descriptivo.md)
para entender el análisis bivariado.
