# Capítulo 8 — Glosario alfabético

> Definición de cada término técnico que aparece en el código del
> proyecto, en orden alfabético. Usa `Ctrl+F` para encontrar el término
> exacto.

---

## A

**`add_constant(X)`** — Función de `statsmodels.api` que añade una
columna de unos a la matriz `X`, necesaria para que el modelo OLS
estime el intercepto.

**`agg(["count", "mean", "std"])`** — Método de pandas para aplicar
**varias agregaciones** a una columna agrupada. Devuelve un DataFrame.

**`alpha`** — Parámetro de transparencia en matplotlib/seaborn (0 =
totalmente transparente, 1 = opaco). También se usa como umbral de
significancia estadística (`α = 0.05`).

**`annotate(texto, xy)`** — Método de matplotlib que dibuja un texto en
una posición específica de la figura, opcionalmente con flecha.

**Anotación de tipo** — Sintaxis declarativa `x: int` que indica el tipo
esperado de una variable o parámetro. Python las **ignora en runtime**
salvo que se use una herramienta como `mypy`.

**`apply(func)`** — Método de pandas que aplica una función elemento
por elemento (Series) o fila/columna (DataFrame).

**`argparse`** — Módulo de la stdlib para construir interfaces de
línea de comandos.

**`as`** — Palabra reservada para renombrar al importar: `import numpy
as np`.

**`assert`** — Sentencia que lanza `AssertionError` si la condición no
se cumple. Útil para verificaciones en desarrollo.

**`astype(tipo)`** — Convierte el tipo de una Series. Tipos comunes:
`"int64"`, `"Int64"` (nullable), `"float64"`, `"Float64"`, `"str"`,
`"object"`.

**`axes` (`ax`)** — Sistema de coordenadas dentro de una `Figure` de
matplotlib. Se crea con `fig, ax = plt.subplots(...)`.

**`axhline`, `axvline`** — Métodos de un `Axes` que dibujan líneas
horizontales / verticales.

---

## B

**`backend`** — Modo de renderizado de matplotlib. `"Agg"` es sin GUI
(válido en servidores y notebooks).

**`bbox`** — Diccionario que define una caja decorativa alrededor de un
texto en matplotlib. Argumentos: `boxstyle`, `fc` (fill color), `ec`
(edge color), `lw`, `alpha`.

**Benjamini–Hochberg (BH)** — Procedimiento para controlar la **FDR**
(False Discovery Rate) en pruebas múltiples. En `statsmodels`:
`method="fdr_bh"`.

**`between(a, b)`** — Método de pandas que devuelve una máscara
booleana: `True` si el valor está en el intervalo `[a, b]`.

**`bin`** — Intervalo en un histograma. `bins=50` divide el eje en 50.

**Bonferroni** — Corrección conservadora para pruebas múltiples:
multiplicar cada p-valor por el número de comparaciones.

**`bool`** — Tipo booleano. Valores: `True`, `False`. Soportan
operadores `and`, `or`, `not`.

**`boxplot`** — Diagrama de caja y bigotes. Muestra la mediana, el
rango intercuartílico y los outliers.

**Breusch–Pagan** — Prueba de homocedasticidad. H₀ = los residuos
tienen varianza constante. Si p < 0.05, hay evidencia de
heterocedasticidad.

---

## C

**`C(col)`** — En fórmulas de patsy (statsmodels), declara la columna
como categórica. Genera dummies automáticamente.

**`catch_warnings()`** — Context manager (`with warnings.catch_warnings():`)
que captura warnings durante un bloque.

**Categórica** — Variable que toma un número finito de niveles
(categorías). Se representa con dummies en regresión.

**`check_call(args)`** — Función de `subprocess` que ejecuta un comando
externo. Lanza `CalledProcessError` si falla.

**`Chi² (χ²) de Pearson`** — Prueba de independencia entre dos
variables categóricas. H₀ = independencia. En `scipy`:
`stats.chi2_contingency(tabla)`.

**`choices=[...]`** — Argumento de `argparse.add_argument` que
restringe los valores permitidos.

**`chi2_contingency(tabla, correction=True)`** — Función de
`scipy.stats` para χ² de tablas de contingencia. `correction=True`
aplica la corrección de Yates en tablas 2×2.

**`close(fig)`** — `plt.close(fig)` libera la memoria de la figura.
Importante al generar muchas figuras seguidas.

**Cluster** — En regresión, grupo de observaciones que comparten
componente no observada. Los errores estándar se "clusterizan"
con `cov_type="cluster"`, `cov_kwds={"groups": ...}`.

**`Colab`** — *Google Colaboratory*: entorno gratuito de notebooks
Jupyter alojados en Google con GPU/TPU opcional.

**Colorbar** — Barra de color a la derecha (o lateral) de un gráfico
que mapea valores a colores. Se crea con `fig.colorbar(scatter, ax)`.

**Comprensión de lista** — Sintaxis idiomática `[x for x in y if c]`
que produce una lista nueva.

**Comprensión de diccionario** — `{k: v for k, v in z.items()}`.

**`concat([df1, df2], axis=0)`** — Apila DataFrames verticalmente
(`axis=0`) u horizontalmente (`axis=1`).

**`config`** — Diccionario o estructura que define parámetros. En el
proyecto, `plt.rcParams` configura matplotlib.

**`continue`** — Sentencia que salta a la siguiente iteración del
bucle.

**`copy()`** — Método de pandas que crea una copia independiente.
Evita el warning `SettingWithCopyWarning`.

**`cov_type`** — Argumento de `.fit()` en statsmodels para elegir el
tipo de matriz de covarianza: `"nonrobust"`, `"HC0"-"HC3"`,
`"cluster"`, `"HAC"`.

**`crosstab(a, b)`** — Función de pandas que construye una tabla de
contingencia (frecuencias) entre dos Series.

---

## D

**`datetime`** — Clase de la stdlib para fechas y horas. `datetime.now()`
devuelve la hora actual.

**`def`** — Palabra reservada para definir una función.

**`describe()`** — Método de pandas que devuelve estadísticos
descriptivos (count, mean, std, min, max, percentiles).

**`dict`** — Diccionario: estructura clave→valor. Literal: `{k: v}`.

**`display`** — Función de `IPython.display` que renderiza un objeto
como salida de celda.

**Docstring** — Cadena de documentación al inicio de un módulo, clase
o función, entre `"""..."""`. Accesible con `obj.__doc__`.

**`dpi`** — *Dots per inch*. Resolución de imagen. DPI 200 es bueno
para web; 300 para impresión.

**`drop(columns=[...])`** — Método de pandas que elimina columnas.
Retorna copia (no inplace por defecto).

**`drop_duplicates(subset, keep)`** — Elimina filas duplicadas según
las columnas indicadas en `subset`.

**`dropna(subset)`** — Elimina filas con NaN en las columnas indicadas.

**Dummy** — Variable binaria 0/1 que indica la pertenencia a una
categoría. Las dummies de un factor con k niveles son k-1 columnas;
una categoría queda como referencia.

**Durbin–Watson** — Estadístico para detectar autocorrelación de orden
1. ≈ 2 indica no autocorrelación; < 1.5 o > 2.5 son señales de
problema.

---

## E

**`elif`** — "Else if". Rama adicional en `if/elif/else`.

**`enumerate(iterable)`** — Función incorporada que devuelve pares
`(índice, valor)` al iterar.

**`errors="coerce"`** — Argumento de `pd.to_numeric` y `pd.to_datetime`:
los valores no convertibles se vuelven `NaN`/`NaT` en lugar de lanzar
excepción.

**`except`** — Cláusula que captura excepciones en un bloque `try`.

**Expresión regular (regex)** — Patrón de búsqueda de cadenas. Módulo
`re`. Ej. `r"\d+"` matchea uno o más dígitos.

---

## F

**`factor`** — Variable categórica con niveles, generalmente codificados
con dummies en la regresión.

**`Family-Wise Error Rate (FWER)`** — Probabilidad de cometer al menos
un error tipo I (falso positivo) entre múltiples pruebas. Holm la
controla.

**`False Discovery Rate (FDR)`** — Proporción esperada de falsos
positivos entre los rechazos. Benjamini–Hochberg la controla.

**`f-string`** — Cadena formateada de Python 3.6+: `f"hola, {nombre}"`.
Permite interpolar expresiones.

**`figsize=(ancho, alto)`** — Tamaño de una figura matplotlib, en
pulgadas.

**`find_spec(nombre)`** — `importlib.util.find_spec` devuelve la
*specification* de un módulo, o `None` si no está disponible.

**`finally`** — Bloque que se ejecuta SIEMPRE, ocurra excepción o no.

**`fit()`** — Método de un modelo statsmodels que ajusta los
parámetros.

**Forest plot** — Visualización clásica en meta-análisis: cada
coeficiente (con IC 95 %) en una fila. Permite comparar muchos
coeficientes a simple vista.

**`for`** — Bucle iterativo: `for x in iterable:`.

**`format(...)`** — Método de cadena para sustituir `{...}` por
argumentos: `"hola, {nombre}".format(nombre="Eduardo")`.

**`formula API`** — Interfaz de statsmodels con fórmulas tipo R
(`y ~ x1 + x2`). Importada como `import statsmodels.formula.api as
smf`.

**`from`** — Palabra reservada: `from módulo import nombre`.

---

## G

**Generador** — Iterador construido con `yield`. Se evalúa
perezosamente.

**`google.colab`** — Paquete específico de Colab con utilidades como
`drive.mount`.

**`groupby(col)`** — Método de pandas para agrupar. Suele seguirse de
una agregación: `df.groupby("dpto")["x"].mean()`.

---

## H

**HC0-HC3** — Familia de matrices de covarianza robustas a
heterocedasticidad (Eicker-White). HC3 es la más conservadora.

**Heatmap** — Mapa de calor: matriz coloreada según valores. En
seaborn: `sns.heatmap(matriz, annot=True)`.

**`het_breuschpagan(res, X)`** — Función de statsmodels para la prueba
de Breusch–Pagan. Devuelve `(LM, p_LM, F, p_F)`.

**`histplot(data, x, hue, kde)`** — Gráfico de seaborn: histograma
con KDE opcional.

**Holm** — Procedimiento secuencial para corregir pruebas múltiples,
más potente que Bonferroni. `method="holm"`.

**Homocedasticidad** — Propiedad de los residuos de tener varianza
constante. Su ausencia (heterocedasticidad) se corrige con errores
robustos.

**`hue`** — Argumento de seaborn que mapea una variable categórica a
colores distintos.

---

## I

**IES** — Institución de Educación Superior. En el dataset, identificada
por `cod_ies`.

**`if / elif / else`** — Estructura condicional.

**`import`** — Palabra reservada para cargar un módulo.

**`importlib.util`** — Submódulo para reflexionar sobre el sistema de
imports (sin importar realmente).

**Imputación** — Reemplazo de valores faltantes por estimaciones. En el
proyecto se prefiere **listwise deletion** (eliminar filas con NaN).

**`in`** — Operador de pertenencia. `x in [1,2,3]` → `True/False`.

**Indentación** — Espacios en blanco al inicio de la línea. Python la
usa para definir bloques. Convención: 4 espacios.

**`Index`** — Estructura de pandas que actúa como etiquetas de filas o
columnas.

**`inner` (violinplot)** — Estilo de marca interior del violín:
`"box"`, `"quart"`, `"point"`, `None`.

**`int64` / `Int64`** — Entero **no nullable** / **nullable** en
pandas. El segundo acepta `pd.NA`.

**`Iterable[T]`** — Tipo de la stdlib `typing` que designa cualquier
objeto recorrible (lista, tupla, generador, range, dict, ...).

**`iterrows()`** — Método de pandas que itera por filas devolviendo
`(índice, Series)`. Lento; usar sólo cuando se necesite.

---

## J

**`json`** — Módulo de la stdlib para serializar / deserializar JSON.
Usado para leer `.ipynb`.

**`join(sep)`** — Método de cadena: `sep.join(lista)` concatena los
elementos con `sep` entre cada par.

---

## K

**Kernel (Jupyter/Colab)** — Proceso Python persistente que ejecuta las
celdas y mantiene el estado de las variables.

**Kolmogorov–Smirnov (KS)** — Prueba no paramétrica para comparar una
muestra contra una distribución teórica. En el proyecto: contra la
normal estándar.

---

## L

**`lambda`** — Función anónima de una sola expresión: `lambda x: x**2`.

**`latin-1`** — Codificación de caracteres ISO 8859-1. Común en
archivos antiguos del ICFES.

**`linewidth`** — Grosor de línea en matplotlib.

**`linear_reset`** — Test RESET de Ramsey. Detecta misespecificación
funcional al añadir potencias de los valores ajustados.

**`Listwise deletion`** — Estrategia de manejo de faltantes: eliminar
las filas que tengan NaN en cualquier columna del modelo.

**Lollipop chart** — Gráfico tipo "piruleta": una barra fina con un
punto al extremo. Útil para coeficientes.

**`loc[fila, col]`** — Indexación de pandas por **etiqueta**.

**`low_memory=False`** — Argumento de `pd.read_csv` que desactiva el
procesamiento por bloques (no soportado con `engine="python"`).

---

## M

**`map(dict)`** — Método de pandas Series que traduce cada valor según
el diccionario. Los no encontrados → NaN.

**`Mann–Whitney U`** — Prueba no paramétrica para dos muestras
independientes. Robusta a no-normalidad. En `scipy`:
`stats.mannwhitneyu(a, b, alternative)`.

**`matplotlib`** — Librería de gráficos en Python. Submódulo
`pyplot` (`plt`) ofrece interfaz tipo MATLAB.

**`MCO` (Mínimos Cuadrados Ordinarios)** — Método de estimación que
minimiza la suma de cuadrados de los residuos.

**`mean(axis=N)`** — Media. `axis=0` por columnas; `axis=1` por filas.

**`melt(id_vars, value_vars)`** — Convierte de formato ancho a largo.

**`mkdir` (os)** — `os.makedirs(p, exist_ok=True)` crea carpetas
recursivamente.

**`Multicolinealidad`** — Cuando dos o más variables explicativas están
fuertemente correlacionadas. Se diagnostica con VIF.

**`multipletests`** — Función de
`statsmodels.stats.multitest` que aplica correcciones por pruebas
múltiples.

---

## N

**`nan` (`np.nan`)** — *Not a Number*. Centinela flotante para datos
faltantes.

**`nargs`** — Argumento de `argparse.add_argument` que define cuántos
valores acepta: `"?"`, `"*"`, `"+"`, un entero.

**`NaT`** — *Not a Time*. Faltante de fecha en pandas.

**`ndarray`** — Array N-dimensional de numpy.

**`nfkd`** — Forma de normalización Unicode. Descompone caracteres
compuestos en su base + marcas combinantes.

**`None`** — Valor especial que indica ausencia. Se compara con
`is None`.

**`notna()` / `isna()`** — Métodos de pandas que devuelven máscaras
booleanas: True si no es NaN / True si es NaN.

**`np.where(cond, si, no)`** — Equivalente vectorial del operador
ternario.

---

## O

**`object` (dtype)** — Tipo genérico de pandas. Contiene cadenas o
mezclas de tipos.

**`OLS` (Ordinary Least Squares)** — Equivalente inglés de MCO.

**`Optional[T]`** — Anotación de tipo que indica `T` o `None`.

**`order=`** — Argumento de seaborn que fija el orden de las categorías
en el eje.

---

## P

**`pandas` (`pd`)** — Librería de análisis tabular. Estructuras
principales: `DataFrame` y `Series`.

**`pd.NA`** — Faltante genérico (admisible en tipos nullable).

**`p-valor`** — Probabilidad de observar un estadístico tan extremo
como el observado bajo H₀. Si p < 0.05, se rechaza H₀ al 5 %.

**`patsy`** — Librería que parsea fórmulas `y ~ x1 + x2`, usada
internamente por `statsmodels.formula.api`.

**`pivot_table`** — Tabla cruzada en pandas: `pivot_table(values,
index, columns, aggfunc)`.

**`polyfit(x, y, deg)`** — Ajuste polinómico por MCO. Retorna
coeficientes `[a_n, ..., a_1, a_0]`.

**`polyval(coef, xs)`** — Evalúa el polinomio en `xs`.

**`pyplot` (`plt`)** — Submódulo de matplotlib con interfaz tipo
MATLAB.

---

## Q

**Cuartil** — Cada uno de los tres valores que dividen una distribución
en cuatro partes iguales. Q1 = percentil 25, Q2 = mediana, Q3 = 75.

---

## R

**R² (R-cuadrado)** — Proporción de la varianza de Y explicada por el
modelo. `modelo.rsquared` en statsmodels.

**R² ajustado** — Versión penalizada por el número de parámetros.
`modelo.rsquared_adj`.

**`raise`** — Lanza una excepción.

**`raw string`** — Cadena con prefijo `r`: `r"\n"` no interpreta `\n`
como salto de línea. Útil para regex.

**`read_csv(ruta, sep, encoding, ...)`** — Lectura de CSV en pandas.

**`reindex(labels)`** — Reordena un DataFrame/Series según las
etiquetas dadas.

**`rename(columns=dict)`** — Renombra columnas.

**`reset_index(drop)`** — Convierte el índice en columna (`drop=False`)
o lo descarta (`drop=True`).

**RESET de Ramsey** — Prueba de misespecificación funcional. H₀ =
forma lineal correcta.

**`return`** — Devuelve un valor desde una función.

**`re.search(pat, s)`** — Busca el primer match de `pat` en `s`.

**`re.sub(pat, repl, s)`** — Sustituye matches.

---

## S

**`scatter(x, y, s, c, cmap)`** — Diagrama de dispersión.

**`scipy`** — Librería científica. Submódulo `stats` para inferencia.

**`seaborn` (`sns`)** — Librería estadística sobre matplotlib.

**`Series`** — Estructura 1D de pandas con índice.

**`set_theme(style, context)`** — Función de seaborn que aplica un
tema global.

**Shapiro–Wilk** — Prueba de normalidad. Más potente que KS en muestras
< 5000.

**`shape`** — Atributo de DataFrame/array: tupla `(filas, columnas)`.

**`smf.ols(formula, data).fit(...)`** — Patrón para ajustar OLS con
fórmula.

**`sns`** — Alias convencional de seaborn.

**`split=True`** — En `sns.violinplot`, dibuja violines partidos
(comparación de dos grupos en el mismo violín).

**`statsmodels`** — Librería de modelos estadísticos y econometría.

**`std(ddof=1)`** — Desviación estándar. `ddof=1` = muestral.

**`str.contains(pat, regex)`** — Método vectorial de pandas: máscara
booleana True si la cadena contiene `pat`.

**`str.extract(pat, expand=False)`** — Extrae con regex.

**`subprocess`** — Módulo para ejecutar procesos externos.

**`subset=[...]`** — En `drop_duplicates` y `dropna`, lista de columnas
relevantes.

**`sys`** — Parámetros del intérprete.

---

## T

**`t de Welch`** — Versión de la t-Student que no asume varianzas
iguales entre grupos. `stats.ttest_ind(a, b, equal_var=False)`.

**`Tabla 1, 2, 3, 4`** — Tablas del documento de investigación:
- **Tabla 1:** Mapeo de departamentos y distancias.
- **Tabla 2:** Variables del modelo MCO.
- **Tabla 3:** Comparación bivariada entre cohortes.
- **Tabla 4:** Resultados de la regresión.

**Ternario** — `valor_si if cond else valor_no`.

**`tight_layout()`** — Ajusta automáticamente los márgenes de la
figura.

**`to_csv(ruta, index, encoding)`** — Exporta DataFrame a CSV.

**`to_datetime(serie, errors, dayfirst)`** — Parsea fechas.

**`to_numeric(serie, errors)`** — Convierte a número.

**`Treatment(reference=N)`** — En patsy, fija el nivel `N` como
categoría de referencia.

**`Tuple[A, B]`** — Anotación: tupla de longitud fija con tipos
posicionales.

**`try / except`** — Manejo de excepciones.

**`type hints`** — Sinónimo de anotaciones de tipo.

**`typing`** — Módulo con tipos genéricos (`Dict`, `List`, `Optional`,
etc.).

---

## U

**`Unicode`** — Estándar internacional de codificación de caracteres.
Python 3 usa strings Unicode por defecto.

**`unicodedata.combining(c)`** — Devuelve > 0 si `c` es una marca
combinante (tilde, diéresis).

**`unicodedata.normalize("NFKD", s)`** — Descompone caracteres
acentuados.

**`usecols=[...]`** — Argumento de `pd.read_csv` que limita las
columnas cargadas. Ahorra memoria.

**`utf-8`** — Codificación Unicode universal.

**`utf-8-sig`** — UTF-8 con BOM (Byte Order Mark). Compatible con Excel.

---

## V

**`value_counts()`** — Cuenta apariciones de cada valor único.

**Variable de control** — En regresión, covariable cuya inclusión
"controla" su efecto al estimar el coeficiente de interés.

**Variable de interés** — En este proyecto, `periodo_ia`. Su
coeficiente es el `β_IA`.

**Variable dependiente** — Y en `Y ~ X1 + X2 + ...`. En este proyecto:
puntaje genérico + los 5 módulos.

**Variable explicativa / regresora** — Las X de la regresión.

**`variance_inflation_factor`** — Función de statsmodels que calcula
el VIF.

**Vectorial** — En numpy/pandas, una operación que se aplica a
**todos** los elementos sin escribir un bucle.

**VIF (Variance Inflation Factor)** — Diagnóstico de
multicolinealidad. Regla común: VIF > 10 indica problema.

**`violinplot`** — Combinación de boxplot + densidad. Muestra la forma
de la distribución.

---

## W

**`warnings`** — Módulo para emitir y filtrar avisos no fatales.

**`Welch`** — Ver "t de Welch".

**`where(cond)`** — Método de pandas: conserva los valores donde
`cond` es True; los demás → NaN.

**`with`** — Palabra reservada para context managers (`with open(...) as f:`).

---

## X

**`X` (matriz de diseño)** — Matriz de regresores en la regresión.
Tiene una fila por observación y una columna por variable + intercepto.

**`xerr`** — Argumento de `ax.errorbar`: arrays de errores horizontales.

---

## Y

**Yates (corrección de)** — Ajuste para la prueba χ² en tablas 2×2 que
mejora la precisión cuando los conteos son pequeños.

**`yield`** — Palabra reservada para generadores. No se usa mucho en el
proyecto.

---

## Z

**`zip(a, b)`** — Empareja elemento por elemento de dos (o más)
iterables.

**`zorder`** — En matplotlib, controla el orden de dibujo: valores
mayores se dibujan encima.

---

## Glosario de constantes y funciones del proyecto

### Constantes globales

| Nombre | Definido en | Valor / descripción |
|---|---|---|
| `RUTA_DEFECTO` | `preparar_datos.py` | `"/content/drive/MyDrive/IA_EDUCACION_SUPERIOR"` |
| `PATRON_ARCHIVO` | `preparar_datos.py` | `"Examen_Saber_Pro_Genericas_{anio}.txt"` |
| `ANIOS` | `preparar_datos.py` | `[2021, 2022, 2023, 2024]` |
| `ANIOS_PREVIO` | `preparar_datos.py` | `[2021, 2022]` |
| `ANIOS_IA` | `preparar_datos.py` | `[2023, 2024]` |
| `SEPARADORES_CANDIDATOS` | `preparar_datos.py` | `("¦", "\|", "\t", ";", ",")` |
| `CODIFICACIONES_CANDIDATAS` | `preparar_datos.py` | `("utf-8", "latin-1", "cp1252")` |
| `COLS_REQUERIDAS` | `preparar_datos.py` | Las 19 columnas crudas del ICFES. |
| `DEPARTAMENTOS` | `preparar_datos.py` | 33 entradas `nombre → (cod, distancia_km)`. |
| `CAPITALES` | `preparar_datos.py` | 33 entradas `nombre → capital`. |
| `ALIAS_DEPARTAMENTOS` | `preparar_datos.py` | Aliases (variantes oficiales). |
| `VARIABLES_DESCRIPTIVO` | `preparar_datos.py` | 14 columnas para análisis bivariado (Tabla 3). |
| `VARIABLES_MODELO` | `preparar_datos.py` | 25 columnas para regresión (Tabla 2). |
| `VARIABLES_FINALES` | `preparar_datos.py` | Unión de las dos anteriores. |
| `MODULOS_GENERICOS` | `preparar_datos.py` | Las 5 puntuaciones de módulos. |
| `PAQUETES_REQUERIDOS` | `preparar_datos.py` | Paquetes para `instalar_dependencias`. |
| `VARS_CONTINUAS` | `analisis_descriptivo.py` | 10 variables para t-Welch + Mann–Whitney. |
| `VARS_DICOTOMICAS` | `analisis_descriptivo.py` | 7 variables para χ². |
| `ALPHA` | `analisis_descriptivo.py`, `regresion_mco.py` | `0.05`. |
| `PALETA_COHORTES` | `analisis_descriptivo.py` | Dict color por cohorte. |
| `NOTA_FUENTE` | `analisis_descriptivo.py` | Pie de figura. |
| `DEPENDIENTES` | `regresion_mco.py` | Las 6 variables dependientes. |
| `CONTROLES` | `regresion_mco.py` | Los 10 controles del modelo. |
| `ESPECIFICACIONES` | `regresion_mco.py` | `("base", "ef_ies", "ef_mun")`. |

### Funciones (orden alfabético)

| Función | Módulo | Propósito |
|---|---|---|
| `_a_numerico(serie)` | preparar_datos | Conversión defensiva a número. |
| `_anotar_fuente(fig)` | analisis_descriptivo | Pie de figura. |
| `_aplicar_estilo()` | analisis_descriptivo | Tema seaborn global. |
| `_canonizar_departamento(v)` | preparar_datos | Nombre canónico desde alias. |
| `_construir_parser()` | preparar_datos | CLI argparse. |
| `_detectar_formato(ruta)` | preparar_datos | Separador + encoding. |
| `_estilo_pub()` | regresion_mco | Tema seaborn global. |
| `_fmt_p(p)` | analisis_descriptivo | Formatea p-valor. |
| `_formula(dep, spec)` | regresion_mco | Construye fórmula patsy. |
| `_leer_columnas_disponibles(r,s,e)` | preparar_datos | Sólo cabecera. |
| `_normalidad(res)` | regresion_mco | Shapiro o KS. |
| `_normalizar_texto(v)` | preparar_datos | Mayúsculas sin tildes. |
| `_parser()` | analisis_descriptivo, regresion_mco, main | CLI. |
| `_registrar(msg)` | preparar_datos | Log con timestamp. |
| `_resumen_continua(s0, s1)` | analisis_descriptivo | t-Welch + MW. |
| `_resumen_dicotomica(s0, s1)` | analisis_descriptivo | χ². |
| `_setup_colab()` / `setup_colab()` | preparar_datos | Helpers Colab. |
| `_vif_variables_continuas(df)` | regresion_mco | VIF. |
| `aplicar_correcciones(df)` | regresion_mco | Holm + BH. |
| `cargar_consolidado(r)` | analisis_descriptivo | Lee CSV. |
| `cargar_y_preparar(r)` | regresion_mco | Lee + listwise. |
| `colinealidad_geografica(df)` | regresion_mco | Triángulo (a)/(b)/(c). |
| `consolidar(dfs)` | preparar_datos | Apila los 4 años. |
| `construir_*` (14 funciones) | preparar_datos | Construyen variables. |
| `construir_todas_las_variables(df)` | preparar_datos | Orquesta las 14. |
| `diagnosticos(modelo, df, spec)` | regresion_mco | 5 pruebas + R². |
| `ejecutar_pipeline(ruta)` | preparar_datos | Punto de entrada Parte 0. |
| `ejecutar_analisis_descriptivo(ruta)` | analisis_descriptivo | Punto entrada Parte 1. |
| `ejecutar_regresion(ruta)` | regresion_mco | Punto entrada Parte 2. |
| `ejecutar_todo(ruta)` | main | Orquestador completo. |
| `en_colab()` | preparar_datos | Detecta Colab. |
| `estimar_18_modelos(df)` | regresion_mco | Loop 6×3. |
| `estimar_modelo(df,dep,spec)` | regresion_mco | OLS con cluster. |
| `figura_*` (6+2 funciones) | analisis_descriptivo, regresion_mco | Generan PNG. |
| `instalar_dependencias_si_aplica` | preparar_datos | pip auto en Colab. |
| `leer_archivo_anio(r, anio)` | preparar_datos | Carga 19 cols. |
| `limpiar(df)` | preparar_datos | Rangos + duplicados. |
| `montar_drive_si_aplica` | preparar_datos | Mount Drive. |
| `persistir(r, dfs, df)` | preparar_datos | Escribe CSV. |
| `procesar_anio(r, anio)` | preparar_datos | Pipeline por año. |
| `seleccionar_variables_finales(df)` | preparar_datos | 25 cols finales. |
| `tabla3_descriptivo(df)` | analisis_descriptivo | Tabla 3. |
| `tabla4_un_modelo(modelo,dep,spec)` | regresion_mco | Fila de tabla 4. |
| `tabla_por_departamento(df)` | analisis_descriptivo | Pivot dpto × cohorte. |

---

¡Has terminado el libro! 🎓

Para profundizar, vuelve a los capítulos específicos o consulta los
documentos técnicos en `docs/`.
