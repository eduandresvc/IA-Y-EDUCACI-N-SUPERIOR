# Capítulo 2 — Librerías clave

> Cada librería que aparece en `import` dentro del proyecto, qué hace y
> cómo se usa.

---

## 2.1 Mapa de librerías por archivo

| Librería | preparar_datos | analisis_descriptivo | regresion_mco | main |
|---|:-:|:-:|:-:|:-:|
| `os` | ✓ | ✓ | ✓ | — |
| `re` | ✓ | — | — | — |
| `sys` | ✓ | — | — | — |
| `argparse` | ✓ | ✓ | ✓ | ✓ |
| `unicodedata` | ✓ | — | — | — |
| `datetime` | ✓ | (vía `_registrar`) | (vía `_registrar`) | (vía `_registrar`) |
| `typing` | ✓ | ✓ | ✓ | ✓ |
| `warnings` | — | — | ✓ | — |
| `importlib.util`, `subprocess` | ✓ | (heredado) | (heredado) | (heredado) |
| `numpy` | ✓ | ✓ | ✓ | — |
| `pandas` | ✓ | ✓ | ✓ | — |
| `scipy.stats` | — | ✓ | ✓ | — |
| `statsmodels` | — | — | ✓ | — |
| `matplotlib` | — | ✓ | ✓ | — |
| `seaborn` | — | ✓ | ✓ | — |
| `google.colab` | (opcional) | (opcional) | (opcional) | (opcional) |

---

## 2.2 Librerías de la *standard library*

### 2.2.1 `os` — Interacción con el sistema operativo

Funciones usadas en el proyecto:

| Función | Qué hace |
|---|---|
| `os.path.join(a, b, ...)` | Une partes de ruta con el separador correcto del SO. |
| `os.path.isfile(p)` | `True` si `p` es un archivo existente. |
| `os.path.isdir(p)` | `True` si `p` es un directorio existente. |
| `os.path.exists(p)` | `True` si la ruta existe (archivo o directorio). |
| `os.path.ismount(p)` | `True` si la ruta es un punto de montaje (Drive, USB, etc.). |
| `os.path.basename(p)` | Devuelve el último componente de la ruta. |
| `os.path.getsize(p)` | Tamaño en bytes. |
| `os.makedirs(p, exist_ok=True)` | Crea carpetas recursivamente. |
| `os.listdir(p)` | Lista los contenidos de la carpeta. |
| `os.walk(p)` | Itera recursivamente por carpetas y archivos. |
| `os.environ.get("VAR", default)` | Lee una variable de entorno. |

### 2.2.2 `sys` — Parámetros del intérprete

| Atributo / función | Qué hace |
|---|---|
| `sys.argv` | Lista de argumentos pasados al script. `sys.argv[0]` es el nombre del script. |
| `sys.modules` | Diccionario con los módulos ya importados. Usado para detectar Colab: `"google.colab" in sys.modules`. |
| `sys.executable` | Ruta del intérprete Python en uso (útil para `pip install`). |
| `sys.path` | Lista de carpetas donde Python busca módulos al importar. |
| `sys.exit(code)` | Termina el script con un código de salida. |

### 2.2.3 `re` — Expresiones regulares

| Función | Qué hace |
|---|---|
| `re.search(pat, s)` | Busca el primer match en `s`. |
| `re.match(pat, s)` | Como `search`, pero anclado al inicio. |
| `re.findall(pat, s)` | Devuelve TODOS los matches como lista. |
| `re.sub(pat, repl, s)` | Sustituye matches por `repl`. |
| `re.compile(pat)` | Compila el patrón (útil si se reutiliza). |

**Sintaxis regex que aparece en el proyecto:**

| Pieza | Significado |
|---|---|
| `\d` | Un dígito (0-9). |
| `\s` | Un espacio en blanco. |
| `\w` | Un carácter alfanumérico. |
| `.` | Cualquier carácter (no salto de línea). |
| `*` | Cero o más repeticiones del átomo anterior. |
| `+` | Una o más repeticiones. |
| `?` | Cero o una repetición. |
| `[...]` | Conjunto de caracteres. |
| `[^...]` | Negación del conjunto. |
| `(...)` | Grupo de captura. |
| `\|` | Alternativa OR. |
| `^`, `$` | Inicio / fin de línea. |
| `r"..."` | *Raw string*: no interpreta `\n`. |

**Banderas:**

| Bandera | Efecto |
|---|---|
| `re.MULTILINE` | `^` y `$` matchean en cada línea. |
| `re.DOTALL` | `.` matchea también saltos de línea. |
| `re.IGNORECASE` | Ignora mayúsculas/minúsculas. |

### 2.2.4 `argparse` — Interfaz de línea de comandos

```python
import argparse
p = argparse.ArgumentParser(description="...")
p.add_argument("--ruta", "-r", required=True, help="...")
p.add_argument("--anios", nargs="+", type=int, default=[2021, 2022])
p.add_argument("--debug", action="store_true")
args = p.parse_args()
print(args.ruta, args.anios, args.debug)
```

| Argumento de `add_argument` | Significado |
|---|---|
| Primer nombre `"--ruta"` | Nombre largo (`--ruta /path`). |
| Alias `"-r"` | Nombre corto (`-r /path`). |
| `required=True` | Hace obligatorio el argumento. |
| `default=...` | Valor por defecto. |
| `type=int` | Convierte el string a int al recibirlo. |
| `nargs="+"` | Acepta uno o más valores. `nargs="?"` opcional. |
| `action="store_true"` | Flag booleano: `True` si está presente. |
| `choices=[...]` | Restringe a un conjunto de valores. |
| `help="..."` | Mensaje de ayuda (visible con `--help`). |

### 2.2.5 `unicodedata` — Manipulación Unicode

| Función | Qué hace |
|---|---|
| `unicodedata.normalize("NFKD", s)` | Descompone caracteres compuestos. `'á'` → `'a' + ' ́'`. |
| `unicodedata.combining(c)` | Devuelve >0 si `c` es una marca combinante (tilde, diéresis, etc.). |

Patrón usado para quitar acentos:

```python
texto = unicodedata.normalize("NFKD", texto)
texto = "".join(c for c in texto if not unicodedata.combining(c))
```

### 2.2.6 `datetime` — Fechas y horas

```python
from datetime import datetime
ahora = datetime.now()          # objeto datetime con la fecha/hora actual
ahora.year, ahora.month, ahora.day
hora_fmt = ahora.strftime("%H:%M:%S")    # "13:45:22"
```

| Código de formato | Significado |
|---|---|
| `%Y` | Año con 4 dígitos. |
| `%m` | Mes (01-12). |
| `%d` | Día (01-31). |
| `%H`, `%M`, `%S` | Hora, minutos, segundos. |

### 2.2.7 `typing` — Anotaciones de tipo

Ya cubiertas en el Capítulo 1, sección 1.10.

### 2.2.8 `warnings` — Avisos no fatales

```python
import warnings
warnings.filterwarnings("ignore")          # silencia TODOS los avisos
# o, selectivamente:
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    codigo_que_genera_avisos()
```

Útil cuando una librería emite *deprecation warnings* benignos.

### 2.2.9 `subprocess` — Ejecutar comandos externos

Usado en `instalar_dependencias_si_aplica` para invocar `pip`:

```python
subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "-q", "scipy"]
)
```

- Pasa el comando como **lista** (más seguro que como cadena).
- `check_call` lanza `CalledProcessError` si el código de salida no es 0.

### 2.2.10 `importlib.util` — Reflexión sobre imports

```python
import importlib.util
spec = importlib.util.find_spec("scipy")   # None si no está instalado
if spec is None:
    print("scipy no está disponible")
```

### 2.2.11 `json` — Lectura/escritura de JSON

Usado para los `.ipynb` (que son JSON):

```python
import json
with open("notebook.ipynb") as f:
    nb = json.load(f)
nb["cells"]                # lista de celdas
```

---

## 2.3 NumPy (`np`)

`numpy` es la librería numérica fundamental. Proporciona el tipo
`ndarray` (arreglo n-dimensional) y operaciones vectorizadas.

### Crear arrays

```python
import numpy as np
np.array([1, 2, 3])
np.zeros(5)
np.ones((3, 4))
np.arange(0, 10, 2)        # [0, 2, 4, 6, 8]
np.linspace(0, 1, 11)      # 11 valores entre 0 y 1, incluidos
```

### Generador aleatorio

```python
rng = np.random.default_rng(42)     # semilla para reproducibilidad
rng.normal(loc=150, scale=25, n)    # n muestras N(150, 25²)
rng.choice(opciones, n)             # n elementos aleatorios
rng.integers(low, high, n)          # n enteros [low, high)
rng.binomial(1, 0.5, n)             # n Bernoulli(0.5)
```

### Centinelas y constantes

| Constante | Significado |
|---|---|
| `np.nan` | Not-a-Number (faltante en flotantes). |
| `np.inf` | Infinito. |
| `np.pi` | π. |

### Funciones útiles

| Función | Qué hace |
|---|---|
| `np.where(cond, si, no)` | Equivalente vectorial de `if-else`. |
| `np.polyfit(x, y, deg=1)` | Ajuste polinómico por MCO; retorna coeficientes. |
| `np.polyval(coef, xs)` | Evalúa el polinomio en `xs`. |
| `np.arange(n)` | Igual que `range` pero produce un array. |
| `np.asarray(x)` | Convierte a array (sin copiar si ya lo es). |
| `np.sqrt(x)`, `np.log(x)`, `np.exp(x)` | Funciones matemáticas. |

---

## 2.4 pandas (`pd`)

### 2.4.1 Estructuras principales

- **`DataFrame`** — tabla 2D (filas × columnas) con un índice.
- **`Series`** — columna 1D con un índice asociado.
- **`Index`** — etiquetas de filas o columnas.

### 2.4.2 Crear / leer

| Función | Qué hace |
|---|---|
| `pd.read_csv(ruta, sep, encoding, nrows, usecols, ...)` | Lee CSV. |
| `pd.read_excel(ruta)` | Lee Excel. |
| `df.to_csv(ruta, index=False)` | Escribe CSV. |
| `pd.DataFrame({"a": [1,2], "b": [3,4]})` | Crea DataFrame a partir de un dict. |
| `pd.Series([1,2,3], name="x")` | Crea Series. |

### 2.4.3 Inspeccionar

| Atributo / método | Qué hace |
|---|---|
| `df.shape` | `(filas, columnas)`. |
| `df.columns` | Index con los nombres de columnas. |
| `df.index` | Index de filas. |
| `df.head(n)` | Primeras `n` filas. |
| `df.tail(n)` | Últimas `n` filas. |
| `df.info()` | Resumen de tipos y faltantes. |
| `df.describe()` | Estadísticos descriptivos de las columnas numéricas. |
| `df.dtypes` | Tipo de cada columna. |
| `len(df)` | Número de filas. |

### 2.4.4 Selección y filtrado

```python
df["col"]               # una columna (Series)
df[["col1", "col2"]]    # varias columnas (DataFrame)
df.loc[fila, col]       # selección por etiqueta
df.iloc[i, j]           # selección por posición
df[df["x"] > 0]         # filtrado booleano
df.loc[mascara, "col"] = valor   # asignación selectiva
```

### 2.4.5 Operaciones por columna

| Método | Qué hace |
|---|---|
| `df["x"].mean()`, `.sum()`, `.std()`, `.median()` | Estadísticos. |
| `df["x"].astype(tipo)` | Conversión de tipo. |
| `df["x"].notna()` / `.isna()` | Máscara booleana. |
| `df["x"].between(a, b)` | Máscara `True` si valor ∈ [a,b]. |
| `df["x"].map(diccionario)` | Traduce según el dict (los no encontrados → NaN). |
| `df["x"].apply(func)` | Aplica `func` a cada elemento. |
| `df["x"].value_counts()` | Frecuencia de cada valor. |
| `df["x"].unique()` | Valores únicos. |
| `df["x"].sort_values()` | Ordena. |

### 2.4.6 Operaciones de cadena (`.str`)

```python
df["nombre"].str.upper()
df["nombre"].str.contains("FOO", regex=True)
df["nombre"].str.startswith("X")
df["nombre"].str.extract(r"(\d+)", expand=False)
df["nombre"].str.replace(",", ".", regex=False)
```

### 2.4.7 Fechas (`.dt`)

```python
serie = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
serie.dt.year
serie.dt.month
serie.dt.day
```

### 2.4.8 Manipulación

| Método | Qué hace |
|---|---|
| `df.rename(columns={"a": "b"})` | Renombra columnas. |
| `df.drop(columns=["x"])` | Elimina columnas. |
| `df.drop_duplicates(subset=[...])` | Elimina filas duplicadas. |
| `df.reset_index(drop=True)` | Reinicia el índice. |
| `df.copy()` | Copia profunda. |
| `df.dropna(subset=[...])` | Elimina filas con NaN en las columnas indicadas. |

### 2.4.9 Agregaciones

```python
# groupby + agregación
df.groupby("dpto")["puntaje"].mean()
df.groupby(["dpto", "anio"])["puntaje"].agg(["count", "mean", "std"])

# pivot_table
df.pivot_table(values="puntaje", index="dpto", columns="anio", aggfunc="mean")

# concatenación
pd.concat([df1, df2], axis=0, ignore_index=True)
```

### 2.4.10 Conversión numérica defensiva

```python
pd.to_numeric(serie, errors="coerce")   # 'NaN' donde no se pueda convertir
```

### 2.4.11 Tipos nullable

| Tipo | Significa |
|---|---|
| `"int64"` | Entero NO nullable (no admite NaN). |
| `"Int64"` | Entero nullable (admite `pd.NA`). |
| `"float64"` | Flotante (admite NaN). |
| `"Float64"` | Flotante nullable. |
| `"bool"` | Booleano. |
| `"object"` | Cualquier objeto (cadenas, mezclas). |

### 2.4.12 Constantes

- `pd.NA` — faltante genérico.
- `pd.NaT` — faltante de fecha (Not-a-Time).
- `pd.isna(x)` — detecta cualquier faltante.

---

## 2.5 scipy.stats

Pruebas estadísticas usadas en el proyecto:

| Función | Qué hace |
|---|---|
| `stats.ttest_ind(a, b, equal_var=False)` | **t de Welch** (dos muestras, varianzas diferentes). Retorna `(t, p)`. |
| `stats.mannwhitneyu(a, b, alternative="two-sided")` | **Mann–Whitney U**, prueba no paramétrica. Retorna `(U, p)`. |
| `stats.chi2_contingency(tabla, correction=True)` | **χ² de Pearson** con corrección de Yates en 2×2. Retorna `(χ², p, gl, esperadas)`. |
| `stats.shapiro(arr)` | **Shapiro–Wilk** de normalidad. Retorna `(W, p)`. |
| `stats.kstest(arr, "norm")` | **Kolmogorov–Smirnov** contra una distribución. Retorna `(D, p)`. |

---

## 2.6 statsmodels

### 2.6.1 Ajuste de OLS con fórmulas

```python
import statsmodels.formula.api as smf

modelo = smf.ols(
    "y ~ x1 + C(grupo, Treatment(reference=0)) + x2",
    data=df,
).fit(
    cov_type="cluster",
    cov_kwds={"groups": df["cluster_id"].values},
)
modelo.params           # coeficientes
modelo.bse              # errores estándar
modelo.pvalues          # p-valores
modelo.rsquared, modelo.rsquared_adj
modelo.resid            # residuos
modelo.fittedvalues     # valores predichos
modelo.summary()        # informe textual completo
```

| Elemento de la fórmula | Significado |
|---|---|
| `y ~ x` | y como función de x. |
| `x1 + x2` | Múltiples variables. |
| `C(col)` | Trata `col` como categórica (genera dummies). |
| `Treatment(reference=0)` | Fija el nivel 0 como categoría base. |
| `x1 * x2` | Interacción + efectos principales. |
| `x1:x2` | Sólo interacción. |
| `-1` | Quitar el intercepto. |

### 2.6.2 Errores estándar robustos

| `cov_type` | Significado |
|---|---|
| `"nonrobust"` | Por defecto, asume homocedasticidad. |
| `"HC0"`, `"HC1"`, `"HC2"`, `"HC3"` | Errores robustos a heterocedasticidad. |
| `"cluster"` | Clusterizados (necesita `groups=`). |
| `"HAC"` | Heterocedasticidad + autocorrelación. |

### 2.6.3 Diagnósticos

```python
from statsmodels.stats.diagnostic import het_breuschpagan, linear_reset
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson

# Breusch-Pagan (heterocedasticidad)
bp_lm, bp_p, _, _ = het_breuschpagan(modelo.resid, modelo.model.exog)

# RESET de Ramsey (especificación)
reset = linear_reset(modelo, power=2, use_f=True)
reset.fvalue, reset.pvalue

# Durbin-Watson (autocorrelación)
dw = durbin_watson(modelo.resid)   # ≈ 2 indica no autocorrelación

# VIF (multicolinealidad)
X = sm.add_constant(df[cols].values)
vifs = [variance_inflation_factor(X, i+1) for i in range(len(cols))]
```

### 2.6.4 Corrección por pruebas múltiples

```python
from statsmodels.stats.multitest import multipletests
_, p_holm, _, _ = multipletests(pvalores, alpha=0.05, method="holm")
_, p_bh,   _, _ = multipletests(pvalores, alpha=0.05, method="fdr_bh")
```

| `method` | Controla |
|---|---|
| `"bonferroni"` | FWER (conservador). |
| `"holm"` | FWER (más potente que Bonferroni). |
| `"fdr_bh"` | FDR (Benjamini-Hochberg). |
| `"fdr_by"` | FDR (Benjamini-Yekutieli). |

### 2.6.5 Otros utilidades

```python
import statsmodels.api as sm
X = sm.add_constant(df[["x1", "x2"]].values)   # añade columna de 1s
sm.OLS(y, X).fit()                              # OLS de bajo nivel
```

---

## 2.7 matplotlib

### 2.7.1 Estructura

```python
import matplotlib
matplotlib.use("Agg")               # backend sin GUI (servidor)
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, y)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Mi figura")
fig.tight_layout()
fig.savefig("mi_figura.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

| Objeto | Qué es |
|---|---|
| `Figure` (`fig`) | El lienzo completo. |
| `Axes` (`ax`) | Un sistema de coordenadas dentro de la figura. |

### 2.7.2 Tipos de gráfico usados

| Método | Qué dibuja |
|---|---|
| `ax.plot(x, y)` | Línea. |
| `ax.scatter(x, y, s, c, alpha)` | Dispersión. |
| `ax.hist(arr, bins, alpha)` | Histograma. |
| `ax.bar(x, alturas)` | Barras. |
| `ax.boxplot(lista_de_arrays, labels)` | Caja y bigotes. |
| `ax.errorbar(x, y, yerr, xerr)` | Línea con barras de error. |
| `ax.axvline(x)`, `ax.axhline(y)` | Líneas verticales/horizontales. |
| `ax.annotate(texto, xy, xytext)` | Anotación con texto y posición. |
| `ax.legend(loc, framealpha)` | Leyenda. |
| `ax.grid(True, linestyle, alpha)` | Cuadrícula. |
| `ax.tick_params(axis, rotation, labelsize)` | Configura ejes. |

### 2.7.3 Estilo global

```python
plt.rcParams.update({
    "axes.facecolor": "white",
    "axes.titleweight": "bold",
    "figure.dpi": 100,
})
```

---

## 2.8 seaborn (`sns`)

Construido sobre matplotlib, ofrece gráficos estadísticos atractivos
con menos código.

### 2.8.1 Tema global

```python
import seaborn as sns
sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
```

### 2.8.2 Gráficos usados

| Función | Qué dibuja |
|---|---|
| `sns.boxplot(data, x, y, hue, palette)` | Boxplot agrupado. |
| `sns.violinplot(data, x, y, hue, split, inner)` | Violín, opcional partido en dos cohortes. |
| `sns.histplot(data, x, hue, kde, bins)` | Histograma + KDE. |
| `sns.heatmap(matriz, annot, cmap)` | Mapa de calor. |
| `sns.scatterplot(data, x, y, size, hue)` | Dispersión. |
| `sns.color_palette(nombre, n_colors)` | Paleta de colores. |

### 2.8.3 Paletas comunes

- `"Set2"`, `"Set1"`, `"husl"` — categóricas.
- `"viridis"`, `"viridis_r"`, `"magma"` — secuenciales.
- `"RdBu"`, `"RdYlBu"`, `"coolwarm"` — divergentes (útiles para
  diferencias en torno a 0).

---

## 2.9 google.colab (Colab solamente)

```python
from google.colab import drive
drive.mount("/content/drive")
```

- **`drive.mount(punto)`** — pide autorización al usuario y monta
  Google Drive. Después se accede a "Mi unidad" como
  `/content/drive/MyDrive/`.
- **`force_remount=False`** — no vuelve a pedir autorización si ya está
  montado.

Otras utilidades (no usadas en el proyecto pero comunes):

| Importación | Para qué sirve |
|---|---|
| `from google.colab import files` | Subir/descargar archivos. |
| `from google.colab import auth` | Autenticación. |
| `from google.colab import widgets` | Widgets interactivos. |

---

¡Pasa al [Capítulo 3 — `preparar_datos.py`](./03_preparar_datos.md)
para empezar el recorrido por los archivos del proyecto.
