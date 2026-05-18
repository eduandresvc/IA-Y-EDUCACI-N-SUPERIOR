# Guía educativa del código

Este documento explica, con propósito didáctico, **cada elemento real
del código** de los cuatro módulos del proyecto:

- `python/preparar_datos.py` — preparación de microdatos.
- `python/analisis_descriptivo.py` — Parte 1 (bivariado).
- `python/regresion_mco.py` — Parte 2 (regresión MCO).
- `python/main.py` — orquestador.

> Sólo se analiza lo que el intérprete realmente ejecuta: palabras
> reservadas, instrucciones, funciones, estructuras, librerías,
> variables, parámetros y conceptos. Los comentarios del script no se
> incluyen como objeto de análisis.

---

## Parte A — Conceptos transversales

Los cuatro módulos comparten varios elementos. Se explican una sola
vez aquí y se reutilizan en las secciones específicas.

### A.1 Cabecera y anotaciones

```python
from __future__ import annotations
```

- **`from … import …`** — importa nombres concretos de un módulo.
- **`__future__`** — módulo estándar que expone funcionalidades futuras
  del lenguaje.
- **`annotations`** — hace que las anotaciones de tipo (`: str`,
  `-> int`) se evalúen como cadenas (de forma **diferida**), sin coste
  en tiempo de ejecución.

### A.2 Librerías de la *standard library*

| Importación | Para qué se usa en el proyecto |
|---|---|
| `import os` | Rutas (`os.path.join`, `os.path.isfile`, `os.path.isdir`, `os.makedirs`). |
| `import re` | Expresiones regulares (extraer un dígito, colapsar espacios). |
| `import sys` | Detectar entorno (`"google.colab" in sys.modules`). |
| `import argparse` | Construcción de la CLI (banderas y argumentos). |
| `import unicodedata` | Descomposición de acentos (NFKD + filtro de marcas combinantes). |
| `from datetime import datetime` | Hora actual para los logs. |
| `from typing import Dict, Iterable, List, Optional, Tuple` | Anotaciones de tipo. |
| `import warnings` | Suprimir avisos durante la regresión. |

### A.3 Librerías de terceros

| Importación | Para qué se usa |
|---|---|
| `import numpy as np` | Arreglos, `np.nan`, `np.where`, `np.polyfit`. |
| `import pandas as pd` | `DataFrame`, `Series`, I/O CSV, `groupby`, `pivot_table`. |
| `from scipy import stats` | Pruebas de hipótesis (`ttest_ind`, `mannwhitneyu`, `chi2_contingency`, `shapiro`, `kstest`). |
| `import statsmodels.api as sm` | OLS de bajo nivel, `add_constant`. |
| `import statsmodels.formula.api as smf` | OLS con fórmulas tipo R (patsy). |
| `from statsmodels.stats.diagnostic import het_breuschpagan, linear_reset` | Diagnósticos de heterocedasticidad y especificación. |
| `from statsmodels.stats.outliers_influence import variance_inflation_factor` | VIF. |
| `from statsmodels.stats.stattools import durbin_watson` | Durbin-Watson. |
| `from statsmodels.stats.multitest import multipletests` | Holm y Benjamini-Hochberg. |
| `import matplotlib` y `matplotlib.pyplot as plt` | Figuras (boxplot, histograma, scatter). |

### A.4 Operadores y construcciones recurrentes

| Construcción | Significado |
|---|---|
| `:` en variables (`x: int`) | Anotación de tipo. |
| `=` | Asignación. |
| `==`, `!=`, `<`, `<=`, `>`, `>=` | Comparaciones. |
| `and`, `or`, `not` | Booleanos escalares. |
| `&`, `\|`, `~` | Booleanos vectoriales (numpy/pandas). |
| `if … else …` | Expresión condicional (ternario). |
| `for … in …` | Bucle iterativo. |
| `lambda x: …` | Función anónima. |
| `def f(...): ...` | Definición de función. |
| `return`, `raise`, `continue`, `pass` | Sentencias de control. |
| `try / except` | Manejo de excepciones. |
| `f"…"` | Cadena formateada (interpolación con `{ }`). |
| `r"…"` | *Raw string* (no interpreta `\n`, útil para regex). |
| `[a, b]`, `(a, b)`, `{k: v}` | Literales de lista, tupla y diccionario. |
| `[x for x in y if cond]` | Comprensión de lista. |
| `{k: v for k, v in z.items()}` | Comprensión de diccionario. |
| `_` | Identificador convencional "valor irrelevante". |
| `*` en `from x import *` o `[*a, *b]` | Desempaquetado / unpack. |
| `__name__` | Variable especial; vale `"__main__"` al ejecutar el archivo directamente. |
| `pd.NA`, `np.nan`, `None`, `NaT` | Representaciones de "faltante". |

### A.5 Logger compartido `_registrar`

Definido en `preparar_datos.py` y reutilizado por los demás módulos:

```python
def _registrar(mensaje: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")
```

- **`-> None`** — no retorna nada explícitamente.
- **`datetime.now().strftime(...)`** — formato `HH:MM:SS`.
- **`f"…{var}…"`** — interpolación.

---

## Parte B — Módulo `preparar_datos.py`

### B.1 Constantes

```python
PATRON_ARCHIVO: str = "Examen_Saber_Pro_Genericas_{anio}.txt"
ANIOS: List[int] = [2021, 2022, 2023, 2024]
```

- **`: str`, `: List[int]`** — anotaciones de tipo.
- Convención: nombres en MAYÚSCULAS marcan constantes.
- **`.format(anio=2021)`** — método de cadenas que sustituye `{anio}`.

### B.2 Diccionarios con tuplas como valor

```python
DEPARTAMENTOS: Dict[str, Tuple[int, float]] = {
    "BOGOTA": (0, 0.0),
    "AMAZONAS": (1, 1100.0),
    ...
}
```

- **`Dict[K, V]`** — anotación: claves K, valores V.
- **`Tuple[int, float]`** — tupla de dos elementos con tipos por
  posición.
- Acceso: `DEPARTAMENTOS["BOGOTA"]` devuelve la tupla.
- **`.items()`** — itera pares `(clave, valor)`.
- **`for n, (c, _) in DEPARTAMENTOS.items()`** — desempaqueta la tupla;
  `_` es el "valor que no me interesa".

### B.3 Comprensiones derivadas

```python
VARIABLES_FINALES = (
    VARIABLES_DESCRIPTIVO
    + [c for c in VARIABLES_MODELO if c not in VARIABLES_DESCRIPTIVO]
)
```

- **`+` entre listas** — concatena.
- **Comprensión de lista** — `[c for c in y if cond]` genera una lista
  filtrada. El resultado es la unión ordenada de los dos conjuntos.

### B.4 Función `_normalizar_texto(valor)`

```python
def _normalizar_texto(valor: object) -> str:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto)
```

- **`pd.isna(valor)`** — `True` para faltantes en cualquier
  representación.
- **`str(valor)`** — convierte cualquier objeto a cadena.
- **`.strip()` / `.upper()`** — quita espacios bordes / mayúsculas.
- **`unicodedata.normalize("NFKD", texto)`** — descompone caracteres
  acentuados.
- **`unicodedata.combining(c)`** — > 0 si `c` es una tilde combinante.
- **`"".join(generator)`** — concatena los elementos de un generador.
- **`re.sub(r"\s+", " ", texto)`** — sustituye uno o más blancos por uno
  solo.

### B.5 Función `_a_numerico(serie)`

- **`serie.dtype.kind`** — un carácter que codifica el tipo:
  `i` entero, `u` entero sin signo, `f` flotante.
- **`x in "iuf"`** — pertenencia de carácter en una cadena.
- **`.astype(str)`** — castea a cadena para usar `.str.*`.
- **`.str.replace(",", ".", regex=False)`** — sustitución literal.
- **`pd.to_numeric(s, errors="coerce")`** — convierte a número; los
  fallos se vuelven `NaN`.

### B.6 Conexión opcional con Google Drive

```python
def montar_drive_si_aplica(punto_montaje: str = "/content/drive") -> bool:
    if "google.colab" not in sys.modules and not os.path.exists("/content"):
        return False
    try:
        from google.colab import drive  # type: ignore
    except ImportError:
        return False
    if not os.path.ismount(punto_montaje):
        drive.mount(punto_montaje, force_remount=False)
    return True
```

- **`try / except ImportError`** — manejo controlado de import opcional.
- **Lazy import** — `from google.colab import drive` dentro de la
  función, no en la cabecera.
- **`os.path.ismount(...)`** — `True` si la ruta es un punto de montaje.

### B.7 Lectura robusta

```python
def _detectar_formato(ruta: str) -> Tuple[str, str]:
    for codificacion in CODIFICACIONES_CANDIDATAS:
        for separador in SEPARADORES_CANDIDATOS:
            try:
                muestra = pd.read_csv(ruta, sep=separador,
                                      encoding=codificacion,
                                      nrows=5, on_bad_lines="skip",
                                      engine="python")
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
            if muestra.shape[1] > 1:
                return separador, codificacion
    raise ValueError(...)
```

- **Bucle anidado** — prueba todas las combinaciones de encoding y
  separador.
- **`try / except (Tipo1, Tipo2):`** — captura dos tipos con una sola
  cláusula.
- **`pd.read_csv` con `nrows=5`** — lee una muestra pequeña.
- **`muestra.shape[1]`** — número de columnas; `shape[0]` filas.
- **`return a, b`** — retorno múltiple via tupla implícita.
- **`raise ValueError(...)`** — lanza excepción.

### B.8 Lectura con `usecols`

```python
mapa_lower = {c.lower(): c for c in cols_archivo}
usecols = [mapa_lower[c] for c in COLS_REQUERIDAS if c in mapa_lower]
df = pd.read_csv(ruta, sep=sep, encoding=enc, usecols=usecols, ...)
df.columns = [c.lower() for c in df.columns]
df["anio"] = anio
```

- **Comprensión de diccionario** — `{c.lower(): c for c in ...}`.
- **`usecols=[...]`** — `pd.read_csv` carga **solo** esas columnas
  (ahorro de memoria sustancial con archivos grandes).
- **Asignar lista a `df.columns`** — reemplaza los nombres si la
  longitud coincide.
- **`df["anio"] = anio`** — crea una columna nueva con valor constante
  difundido a todas las filas.

### B.9 Patrón de drop incremental

Cada función `construir_*` sigue la misma forma:

```python
def construir_X(df: pd.DataFrame) -> pd.DataFrame:
    df["nueva"] = transformacion(df["columna_cruda"])
    df = df.drop(columns=["columna_cruda"])
    return df
```

- **`df.drop(columns=[...])`** — devuelve un dataframe sin esas
  columnas. La reasignación `df = df.drop(...)` cambia la referencia
  local; el caller recibe el resultado retornado.

### B.10 `construir_edad` paso a paso

```python
fecha = pd.to_datetime(df["estu_fechanacimiento"], errors="coerce", dayfirst=True)
df["edad"] = (df["anio"] - fecha.dt.year).astype("Float64")
df.loc[(df["edad"] < 15) | (df["edad"] > 80), "edad"] = np.nan
df = df.drop(columns=["estu_fechanacimiento"])
```

- **`pd.to_datetime(..., errors="coerce", dayfirst=True)`** — convierte
  a `Timestamp`. `coerce` deja `NaT` cuando falla; `dayfirst` interpreta
  `DD/MM/AAAA`.
- **`fecha.dt.year`** — accessor `.dt` sobre fechas; extrae el año.
- **Resta vectorial** entre columnas.
- **`.astype("Float64")`** — flotante **nullable** (admite `pd.NA`).
- **`df.loc[mascara, columna] = valor`** — asignación selectiva por
  máscara booleana.
- **`|`** — OR vectorial (paréntesis obligatorios por precedencia).

### B.11 `.map(diccionario)`

```python
df["genero"] = norm.map({"F": 0, "FEMENINO": 0,
                         "M": 1, "MASCULINO": 1}).astype("Int64")
```

- **`Series.map(dict)`** — traduce cada valor; los no-encontrados
  → `NaN`.
- **`.astype("Int64")`** — entero **nullable**.

### B.12 `np.where` anidado

```python
df["jornada"] = np.where(
    norm.str.contains("DISTANCIA|VIRTUAL", regex=True), 1,
    np.where(norm.str.contains("PRESENCIAL"), 0, np.nan),
)
```

- **`np.where(cond, si, no)`** — equivalente vectorial del ternario.
- **Anidado** — modela tres estados (1 / 0 / NaN).
- **`serie.str.contains(patron, regex=True)`** — máscara booleana con
  regex.

### B.13 `_canonizar_departamento`

Tres niveles de coincidencia:

```python
if texto in ALIAS_DEPARTAMENTOS: return ALIAS_DEPARTAMENTOS[texto]
if texto in DEPARTAMENTOS: return texto
for canon in DEPARTAMENTOS:
    if texto.startswith(canon) or canon in texto:
        return canon
return None
```

- **`for canon in DEPARTAMENTOS:`** — iterar un dict produce sus claves
  (en orden de inserción desde Python 3.7).
- **`startswith`, `in`** — pruebas de subcadenas.

### B.14 Limpieza

```python
fuera = ~df[col].between(0, 300)
df.loc[fuera & df[col].notna(), col] = np.nan
df = df[df["puntaje_saberpro_generico"].notna()].copy()
df = df.drop_duplicates(subset=["id_estudiante", "anio"], keep="first")
df = df.reset_index(drop=True)
```

- **`~` (tilde)** — NOT vectorial.
- **`.between(a, b)`** — máscara `True` si valor ∈ [a, b].
- **`mask1 & mask2`** — AND vectorial.
- **`.notna()`** — máscara de no-faltantes.
- **`.copy()`** — evita avisos de vista (`SettingWithCopyWarning`).
- **`drop_duplicates(subset=[...], keep="first")`** — elimina filas
  duplicadas según las columnas indicadas, conservando la primera.
- **`reset_index(drop=True)`** — reinicia el índice tras filtrar.

### B.15 `pd.concat` y persistencia

```python
df = pd.concat(dfs.values(), axis=0, ignore_index=True)
df.to_csv(ruta, index=False, encoding="utf-8-sig")
```

- **`pd.concat([...], axis=0)`** — apila verticalmente.
- **`ignore_index=True`** — reindexa 0..n-1.
- **`utf-8-sig`** — UTF-8 con BOM (compatible con Excel).

### B.16 CLI con `argparse`

```python
parser.add_argument("--ruta", "-r", required=True, help=...)
parser.add_argument("--anios", "-a", nargs="+", type=int, default=ANIOS)
parser.add_argument("--sin-guardar", action="store_true")
```

- **`--ruta`** / **`-r`** — nombre largo y alias corto.
- **`required=True`** — obligatorio.
- **`nargs="+"`** — uno o más valores.
- **`type=int`** — convierte cada valor.
- **`action="store_true"`** — flag booleano (`True` si está presente).
- **`__name__ == "__main__"`** — punto de entrada CLI.
- **`args = parser.parse_args()`** — devuelve un `Namespace` con los
  atributos.

---

## Parte C — Módulo `analisis_descriptivo.py`

### C.1 Importaciones específicas

```python
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from preparar_datos import MODULOS_GENERICOS, _registrar, ANIOS_PREVIO, ANIOS_IA
```

- **`from scipy import stats`** — accede a `stats.ttest_ind`,
  `stats.mannwhitneyu`, `stats.chi2_contingency`, `stats.shapiro`,
  `stats.kstest`.
- **`matplotlib.use("Agg")`** — selecciona el backend "Agg" (sin GUI),
  necesario en servidores o entornos sin pantalla.
- **`import matplotlib.pyplot as plt`** — interfaz pyplot (estado
  global, similar a MATLAB).
- **`from preparar_datos import …`** — reutiliza constantes y el
  logger del módulo 1.

### C.2 Anotación de retorno con genéricos

```python
def ejecutar_analisis_descriptivo(ruta_proyecto: str) -> Dict[str, object]:
```

- **`Dict[str, object]`** — diccionario con claves `str` y valores de
  cualquier tipo (`object` es la raíz de la jerarquía).

### C.3 `_resumen_continua` — t de Welch + Mann-Whitney

```python
t, p_t = stats.ttest_ind(s0, s1, equal_var=False, nan_policy="omit")
u, p_mw = stats.mannwhitneyu(s0, s1, alternative="two-sided")
```

- **`stats.ttest_ind(a, b, equal_var=False)`** — t de **Welch**
  (no asume varianzas iguales). Retorna `(estadístico, p)`.
- **`nan_policy="omit"`** — ignora `NaN`.
- **`stats.mannwhitneyu(a, b, alternative="two-sided")`** — prueba no
  paramétrica para dos muestras independientes. Bilateral.
- **Desempaquetado `t, p_t = …`** — la función retorna una tupla con
  nombre que se desempaqueta en dos variables.

### C.4 `_resumen_dicotomica` — χ² con corrección de Yates

```python
tabla = pd.crosstab(
    pd.concat([pd.Series(0, index=s0.index), pd.Series(1, index=s1.index)]),
    pd.concat([s0, s1]),
)
chi2, p, *_ = stats.chi2_contingency(tabla, correction=True)
```

- **`pd.crosstab(fila, columna)`** — tabla de contingencia (frecuencias).
- **`pd.Series(0, index=...)`** — Series rellena de ceros con un índice
  dado.
- **`pd.concat([…])`** — apila Series.
- **`stats.chi2_contingency(tabla, correction=True)`** — χ² de Pearson;
  `correction=True` aplica la corrección de Yates a tablas 2×2.
- **`a, b, *_`** — desempaqueta los dos primeros valores; `*_` recoge
  el resto en una lista anónima.

### C.5 `tabla3_descriptivo` y `to_string`

- **`for var in VARS_CONTINUAS:`** — bucle sobre la lista de variables
  continuas.
- **`if var not in df.columns: continue`** — defensivo: salta si la
  variable no está en este dataframe.
- **`filas.append({...})`** — diccionarios añadidos a una lista; al
  final `pd.DataFrame(filas)` construye el dataframe.
- **`.to_string(index=False)`** — convierte el dataframe a una cadena
  formateada (útil para imprimir tablas en consola sin truncar).

### C.6 `tabla_por_departamento` — `groupby` + `pivot_table`

```python
grupo = (df.groupby(["departamento", "departamento_nombre", "periodo_ia"])
           [cols_valor].mean().round(2).reset_index())
pivot = grupo.pivot_table(
    index=["departamento", "departamento_nombre"],
    columns="periodo_ia", values=cols_valor,
)
pivot.columns = [f"{var}__periodo_{p}" for var, p in pivot.columns]
```

- **`.groupby([cols])`** — agrupa por las columnas indicadas.
- **`[cols_valor]`** — selecciona las columnas a agregar.
- **`.mean()`** — agregación.
- **`.round(2)`** — redondeo en todo el dataframe.
- **`.reset_index()`** — vuelve el índice agrupado a columnas.
- **`pivot_table(index=..., columns=..., values=...)`** — reordena en
  formato ancho.
- **`pivot.columns`** es un `MultiIndex` con tuplas `(variable, periodo)`;
  la comprensión `[f"{var}__periodo_{p}" for var, p in pivot.columns]`
  aplana esas tuplas en nombres simples.

### C.7 Figuras matplotlib

```python
fig, ax = plt.subplots(figsize=(7, 5))
ax.boxplot(datos, labels=[...])
ax.set_ylabel("...")
ax.set_title("...")
ax.grid(True, axis="y", linestyle=":", alpha=0.5)
fig.tight_layout()
fig.savefig(ruta_out, dpi=150, bbox_inches="tight")
plt.close(fig)
```

- **`plt.subplots(figsize=(ancho, alto))`** — retorna una tupla
  `(Figure, Axes)`. La figura es el lienzo; el axes es el gráfico.
- **`ax.boxplot(lista_de_arrays, labels=[...])`** — boxplot por grupo.
- **`ax.hist(array, bins=N, alpha=α, label=...)`** — histograma.
- **`ax.scatter(x, y, s=tamaño, alpha=α)`** — dispersión.
- **`ax.plot(x, y, linestyle="--", linewidth=1.2, label=...)`** —
  línea.
- **`ax.annotate(texto, (x, y), fontsize=…)`** — anotación.
- **`ax.set_xlabel / set_ylabel / set_title / legend / grid`** —
  configuración estética.
- **`fig.tight_layout()`** — ajusta márgenes automáticamente.
- **`fig.savefig(ruta, dpi=150, bbox_inches="tight")`** — guarda como
  imagen.
- **`plt.close(fig)`** — libera memoria; importante al generar muchas
  figuras.

### C.8 Línea de tendencia con `np.polyfit`

```python
coef = np.polyfit(x, y, deg=1)
xs = np.linspace(x.min(), x.max(), 100)
ax.plot(xs, np.polyval(coef, xs), ...)
```

- **`np.polyfit(x, y, deg=1)`** — ajuste polinómico por MCO; con
  `deg=1` es una recta. Retorna `[pendiente, intercepto]`.
- **`np.linspace(a, b, 100)`** — genera 100 puntos equiespaciados.
- **`np.polyval(coef, xs)`** — evalúa el polinomio en `xs`.

---

## Parte D — Módulo `regresion_mco.py`

### D.1 Importaciones específicas de statsmodels

| Import | Para qué se usa |
|---|---|
| `import statsmodels.api as sm` | `sm.add_constant`, tipos base. |
| `import statsmodels.formula.api as smf` | `smf.ols(formula, data=df).fit(...)`. |
| `from statsmodels.stats.diagnostic import het_breuschpagan, linear_reset` | BP y RESET de Ramsey. |
| `from statsmodels.stats.outliers_influence import variance_inflation_factor` | VIF por variable. |
| `from statsmodels.stats.stattools import durbin_watson` | DW. |
| `from statsmodels.stats.multitest import multipletests` | Holm, Benjamini-Hochberg, Bonferroni. |
| `from scipy import stats` | Shapiro-Wilk, Kolmogorov-Smirnov. |

### D.2 Constantes

```python
DEPENDIENTES = ["puntaje_saberpro_generico", *MODULOS_GENERICOS]
CONTROLES = ["estrato", "genero", "edad", ...]
ESPECIFICACIONES = ("base", "ef_ies", "ef_mun")
ALPHA = 0.05
```

- **`[*lista]`** — desempaqueta una lista dentro de otra.
- **`("a", "b", "c")`** — tupla (más adecuada para constantes que no
  cambian).

### D.3 `cargar_y_preparar` — listwise y casting

```python
df = df.dropna(subset=columnas_modelo).copy()
for col in ["departamento", "tipo_municipio", "cod_ies", "periodo_ia"]:
    df[col] = df[col].astype("int64")
```

- **`df.dropna(subset=cols)`** — elimina filas con `NaN` en las
  columnas indicadas (**listwise deletion**, el criterio estándar
  para MCO).
- **`.astype("int64")`** — entero **no nullable**. Necesario porque
  `smf.ols` con `C(...)` no acepta `Int64` (nullable).

### D.4 Fórmulas patsy

```python
return (
    f"{dependiente} ~ periodo_ia "
    f"+ C(departamento, Treatment(reference=0)) "
    f"+ distancia_bogota_km + {controles_str}"
)
```

- **Fórmula tipo R** — `Y ~ X1 + X2 + ...`.
- **`C(col)`** — declara la columna como categórica; patsy genera las
  dummies automáticamente.
- **`Treatment(reference=0)`** — fija el nivel `0` como categoría de
  referencia (Bogotá en `departamento`, Bogotá en `tipo_municipio`).
- **`f"…{var}…"`** — interpolación para inyectar variables al texto.

### D.5 Ajuste con errores clusterizados

```python
modelo = smf.ols(formula, data=df).fit(
    cov_type="cluster",
    cov_kwds={"groups": df["cod_ies"].values},
)
```

- **`smf.ols(formula, data=df)`** — crea el modelo (no ajusta aún).
- **`.fit(...)`** — estima los coeficientes.
- **`cov_type="cluster"`** — matriz de covarianza clusterizada
  (robusta a heterocedasticidad y a correlación dentro de cluster).
- **`cov_kwds={"groups": array}`** — identificador del cluster (IES).
- **`with warnings.catch_warnings(): warnings.simplefilter("ignore")`** —
  suprime los avisos benignos de statsmodels.

### D.6 Diagnósticos

```python
# Normalidad
n = len(residuos)
if n < 5000:
    st, p = stats.shapiro(residuos)         # Shapiro-Wilk
else:
    residuos_z = (residuos - residuos.mean()) / residuos.std(ddof=1)
    st, p = stats.kstest(residuos_z, "norm") # KS contra N(0,1)
```

- **`stats.shapiro(arr)`** — prueba de Shapiro-Wilk. Recomendada para
  n < 5 000 por motivos de potencia.
- **`stats.kstest(arr_z, "norm")`** — Kolmogorov-Smirnov contra una
  distribución de referencia (aquí la normal estándar).

```python
# Breusch-Pagan
bp_lm, bp_p, *_ = het_breuschpagan(res, modelo.model.exog)
```

- **`het_breuschpagan(residuos, X)`** — retorna varios valores; sólo
  guardamos el estadístico LM y el p-valor.

```python
dw = durbin_watson(res)               # Durbin-Watson
reset = linear_reset(modelo, power=2, use_f=True)
```

- **`durbin_watson(residuos)`** — entre 0 y 4; ~2 = no autocorrelación.
- **`linear_reset(modelo, power=2, use_f=True)`** — RESET de Ramsey.
  Añade potencias de los valores ajustados; prueba si esos términos
  son significativos.

```python
# VIF
X = sm.add_constant(df[cols].astype(float).values)
vifs = [variance_inflation_factor(X, i + 1) for i in range(len(cols))]
```

- **`sm.add_constant(X)`** — añade columna de unos para el intercepto.
- **`variance_inflation_factor(X, i)`** — VIF de la columna `i`.
- **Comprensión de lista** — calcula el VIF de cada variable.

### D.7 Triángulo de colinealidad

Tres modelos OLS independientes que difieren en qué variables
geográficas incluyen. La misma técnica que en `estimar_modelo`,
recolectando `params["periodo_ia"]`, `bse["periodo_ia"]` y
`pvalues["periodo_ia"]`.

### D.8 Tabla 4

```python
tabla = pd.DataFrame({
    "termino":   coef.index,
    "coef":      coef.values.round(4),
    "estadistico_t": (coef.values / se.values).round(3),
    "p_valor":   pvals.values.round(5),
})
```

- **`modelo.params`** / **`modelo.bse`** / **`modelo.pvalues`** —
  `Series` con coeficientes, errores estándar y p-valores indexados
  por nombre de variable.
- **`.values`** — array de numpy subyacente.
- **`.round(n)`** — redondeo.

### D.9 Corrección por pruebas múltiples

```python
_, p_holm, _, _ = multipletests(sub["p_IA"].values, alpha=ALPHA, method="holm")
_, p_bh,   _, _ = multipletests(sub["p_IA"].values, alpha=ALPHA, method="fdr_bh")
```

- **`multipletests(pvals, alpha, method)`** — retorna 4 elementos:
  - rechazos (booleano),
  - p-valores ajustados,
  - alfa corregido por Sidak,
  - alfa corregido por Bonferroni.
- **`_, x, _, _`** — desempaquetado: solo nos interesa el segundo
  (los p-valores ajustados).
- **`method="holm"`** — controla la **FWER** (probabilidad de un solo
  falso positivo).
- **`method="fdr_bh"`** — Benjamini-Hochberg; controla la **FDR**
  (proporción esperada de falsos positivos entre los rechazos).

### D.10 Comparaciones booleanas a la salida

```python
sub["sig_5pct_holm"] = sub["p_IA_holm"] < ALPHA
```

- Genera una columna booleana vectorial: `True` si el p ajustado es
  inferior al umbral.

---

## Parte E — Módulo `main.py`

### E.1 Orquestación

```python
def ejecutar_todo(ruta_proyecto, anios=ANIOS,
                  correr_preparar=True, correr_descriptivo=True,
                  correr_regresion=True) -> None:
    if correr_preparar:
        ejecutar_pipeline(...)
    if correr_descriptivo:
        ejecutar_analisis_descriptivo(...)
    if correr_regresion:
        ejecutar_regresion(...)
```

- **Parámetros con valores por defecto** — permiten invocar la función
  sin argumentos.
- **`-> None`** — no retorna; sólo produce efectos secundarios
  (archivos).

### E.2 CLI con elección selectiva

```python
parser.add_argument("--solo", choices=["preparar", "descriptivo", "regresion"], default=None)
parser.add_argument("--saltar-preparar", action="store_true")
```

- **`choices=[...]`** — restringe los valores permitidos. Si el usuario
  pasa otra cosa, `argparse` aborta con un mensaje claro.
- **`default=None`** — si no se pasa `--solo`, se ejecutan los tres.

```python
if args.solo == "preparar":
    correr_desc = correr_reg = False
elif args.solo == "descriptivo":
    correr_prep = correr_reg = False
elif args.solo == "regresion":
    correr_prep = correr_desc = False
if args.saltar_preparar:
    correr_prep = False
```

- **Asignación múltiple `a = b = False`** — asigna `False` a ambas
  variables.
- **Cascada `if / elif`** — sólo una rama se ejecuta.

---

## Apéndice — Tabla resumen de TODAS las funciones del proyecto

### `preparar_datos.py`

| Función | Retorno | Propósito |
|---|---|---|
| `_normalizar_texto` | `str` | Mayúsculas sin tildes. |
| `_registrar` | `None` | Log con timestamp. |
| `_a_numerico` | `Series` | Conversión numérica defensiva. |
| `montar_drive_si_aplica` | `bool` | Monta Drive si está en Colab. |
| `_detectar_formato` | `(str, str)` | Detecta separador + encoding. |
| `_leer_columnas_disponibles` | `list[str]` | Nombres de columnas del .txt. |
| `leer_archivo_anio` | `DataFrame` | Carga sólo las 19 columnas requeridas. |
| `transformar_id_y_modulos` | `DataFrame` | Rename de ID y módulos. |
| `construir_periodo_ia` … `construir_tipo_municipio` | `DataFrame` | 14 funciones, una por variable. |
| `construir_todas_las_variables` | `DataFrame` | Orquesta las 14. |
| `limpiar` | `DataFrame` | Rangos, faltantes, duplicados. |
| `seleccionar_variables_finales` | `DataFrame` | 25 columnas finales. |
| `procesar_anio` | `DataFrame` | Pipeline para un año. |
| `consolidar` | `DataFrame` | Apila los 4 años. |
| `persistir` | `str` | Escribe CSV en disco. |
| `ejecutar_pipeline` | `(dict, DataFrame)` | Punto de entrada. |

### `analisis_descriptivo.py`

| Función | Retorno | Propósito |
|---|---|---|
| `cargar_consolidado` | `DataFrame` | Lee `df_consolidado.csv`. |
| `_fmt_p` | `str` | Formatea p-valores. |
| `_resumen_continua` | `dict` | t-Welch + Mann-Whitney. |
| `_resumen_dicotomica` | `dict` | χ² con Yates. |
| `tabla3_descriptivo` | `DataFrame` | Tabla 3 completa. |
| `tabla_por_departamento` | `DataFrame` | Medias por (dpto × cohorte). |
| `figura_boxplot_periodo` | `None` | Boxplot por cohorte. |
| `figura_boxplot_departamento` | `None` | Boxplot por dpto. |
| `figura_histograma_cohortes` | `None` | Histograma comparativo. |
| `figura_dispersion_distancia` | `None` | Scatter dist↔puntaje. |
| `ejecutar_analisis_descriptivo` | `dict` | Punto de entrada. |

### `regresion_mco.py`

| Función | Retorno | Propósito |
|---|---|---|
| `cargar_y_preparar` | `DataFrame` | Listwise + casting. |
| `_formula` | `str` | Fórmula patsy según especificación. |
| `estimar_modelo` | `RegressionResults` | OLS con cluster por IES. |
| `_normalidad` | `(str, float, float)` | Shapiro o KS según n. |
| `_vif_variables_continuas` | `DataFrame` | VIF por variable. |
| `diagnosticos` | `dict` | Las 5 pruebas + R². |
| `colinealidad_geografica` | `DataFrame` | Versiones (a)/(b)/(c). |
| `tabla4_un_modelo` | `DataFrame` | Coeficientes + SE + p. |
| `estimar_18_modelos` | `(DataFrame, DataFrame, DataFrame)` | Loop por (dep × spec). |
| `aplicar_correcciones` | `DataFrame` | Holm + BH. |
| `ejecutar_regresion` | `dict` | Punto de entrada. |

### `main.py`

| Función | Retorno | Propósito |
|---|---|---|
| `ejecutar_todo` | `None` | Encadena los tres módulos. |
| `_parser` | `ArgumentParser` | CLI con `--solo`, `--saltar-preparar`. |
