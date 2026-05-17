# Explicación línea a línea del código — Versión R
## Notebook: `analisis_departamentos_colombia_R.ipynb`

Este documento explica en detalle qué hace cada línea de código del notebook en lenguaje **R**, qué significa cada función, cada parámetro y cada decisión de programación. Es la contraparte exacta de `../EXPLICACION_CODIGO.md` (versión Python) y conserva la misma estructura de celdas y la misma lógica.

---

## Tabla de contenido

- [Celda 1 — Librerías](#celda-1--librerías)
- [Celda 2 — Configuración](#celda-2--configuración)
- [Celda 3 — Detección de archivos](#celda-3--detección-de-archivos)
- [Celda 4 — DataFrames individuales](#celda-4--dataframes-individuales)
- [Celda 5 — Selección de columnas](#celda-5--selección-de-columnas)
- [Celda 6 — Unión de DataFrames](#celda-6--unión-de-los-4-dataframes)
- [Celda 7 — Variables nuevas](#celda-7--creación-de-variables-nuevas)
- [Celda 8 — Exclusión de Bogotá D.C.](#celda-8--exclusión-de-bogotá-dc)
- [Celda 9 — Estadística descriptiva](#celda-9--estadística-descriptiva)
- [Celda 10 — Visualizaciones](#celda-10--visualizaciones)
- [Celda 11 — Exportar](#celda-11--exportar)

---

## Celda 1 — Librerías

```r
pkgs <- c("dplyr", "readr", "tidyr", "ggplot2", "stringi", "scales", "patchwork")
```
`c(...)` es la función básica de R para construir un **vector** (equivalente a una lista en Python). Aquí se construye un vector de caracteres con los nombres de los paquetes que el notebook necesita. La operación `<-` es la asignación estándar en R (equivalente a `=` en Python).

---

```r
faltan <- setdiff(pkgs, rownames(installed.packages()))
```
`installed.packages()` devuelve una matriz con todos los paquetes ya instalados en el entorno. `rownames(...)` extrae los nombres de las filas (que son los nombres de los paquetes). `setdiff(A, B)` calcula la **diferencia de conjuntos** A − B: devuelve los elementos de `pkgs` que **no** están instalados.

---

```r
if (length(faltan) > 0) install.packages(faltan, quiet = TRUE)
```
Si el vector `faltan` no está vacío (es decir, falta al menos un paquete), se instalan con `install.packages()`. El parámetro `quiet = TRUE` suprime los mensajes verbosos durante la instalación.

---

```r
suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  ...
})
```
`library(pkg)` carga un paquete (equivalente a `import pkg` en Python). `suppressPackageStartupMessages({...})` envuelve un bloque de llamadas para que **no** se impriman los mensajes de bienvenida de cada paquete. Las llaves `{}` agrupan varias expresiones en un solo bloque, como en C o JavaScript.

| Paquete | Para qué se usa |
|---------|-----------------|
| `dplyr` | Manipulación de datos (`group_by`, `mutate`, `summarise`, `bind_rows`). Equivalente a `pandas`. |
| `readr` | Lectura/escritura rápida de CSV con detección de codificación. Equivalente a `pd.read_csv()`. |
| `tidyr` | Pivot y transformaciones (`pivot_wider`, `pivot_longer`). |
| `ggplot2` | Gráficos. Equivalente a `matplotlib` + `seaborn`. |
| `stringi` | Operaciones avanzadas con cadenas. Aquí se usa `stri_trans_general` para quitar tildes. |
| `scales` | Formato de ejes en gráficos. |
| `patchwork` | Composición de varios gráficos `ggplot2` en una sola figura. Equivalente a `plt.subplots()`. |

---

```r
options(scipen = 999, dplyr.summarise.inform = FALSE)
```
`options()` cambia opciones globales. `scipen = 999` desactiva la notación científica para imprimir números grandes con todos sus dígitos. `dplyr.summarise.inform = FALSE` silencia el mensaje que `dplyr` imprime cuando agrupa.

---

```r
theme_set(theme_minimal(base_size = 11))
```
`ggplot2` aplica un **tema** global a todos los gráficos producidos. `theme_minimal()` es un tema limpio con fondo blanco. `base_size = 11` fija el tamaño base de la fuente.

---

## Celda 2 — Configuración

```r
COLUMNA_DEPARTAMENTO <- "ESTU_COD_DEPTO_PRESENTACION"
COLUMNA_RESULTADO    <- "MOD_RAZONA_CUANTITAT_PUNT"
```
Dos variables de texto que el usuario edita para indicar qué columnas de su CSV contienen el departamento y el resultado del examen. En R las cadenas usan **comillas dobles** preferentemente. La convención de nombre en MAYÚSCULAS indica que son **constantes** de configuración (no es obligatorio en R, pero es buena práctica).

---

```r
cat(sprintf("Columna departamento : %s\n", COLUMNA_DEPARTAMENTO))
```
`sprintf()` construye una cadena con marcadores de posición (`%s` = string, `%d` = integer, `%f` = float), igual que en C. `\n` es el salto de línea. `cat()` imprime cadenas sin comillas ni numeración (a diferencia de `print()`, que es más estructurado). Aquí se usa `cat` para imprimir un mensaje simple al usuario.

---

## Celda 3 — Detección de archivos

```r
carpeta <- "/content"
if (!dir.exists(carpeta)) carpeta <- getwd()
```
En Google Colab, los archivos subidos por el usuario quedan en `/content/`. `dir.exists()` verifica si esa ruta existe (existe en Colab pero no en otros entornos). Si no existe, se cae al directorio de trabajo actual con `getwd()` (útil para pruebas locales).

---

```r
archivos <- list.files(carpeta, pattern = "\\.csv$", full.names = TRUE,
                       ignore.case = TRUE)
```
`list.files()` lista archivos en una carpeta. Los parámetros:

- `pattern = "\\.csv$"`: expresión regular que filtra archivos con extensión `.csv`. El `\\` escapa el punto (en regex `.` significa "cualquier carácter"). El `$` ancla al final del nombre.
- `full.names = TRUE`: devuelve la ruta completa, no solo el nombre.
- `ignore.case = TRUE`: trata `.CSV` y `.csv` como equivalentes.

---

```r
info <- file.info(archivos)
archivos <- archivos[order(info$mtime)]
```
`file.info()` devuelve un `data.frame` con metadatos de cada archivo (tamaño, fecha de modificación, permisos). `info$mtime` es la columna de fecha de modificación. `order()` devuelve los índices que ordenan el vector ascendentemente. Aquí se reordenan los archivos por **fecha de carga** (el primero subido va primero), asumiendo que el usuario los subió en orden cronológico 2021 → 2024.

---

```r
if (length(archivos) == 0) {
  stop("No hay archivos CSV en /content. ...")
}
```
`stop()` lanza un error y detiene la ejecución (equivalente a `raise` en Python). Si no se encontró ningún CSV el notebook se interrumpe con un mensaje claro.

---

## Celda 4 — DataFrames individuales

```r
anios_orden <- c(2021, 2022, 2023, 2024)
```
Vector de enteros con los años correspondientes a cada archivo, en el orden esperado.

---

```r
leer_csv <- function(ruta) {
  encs <- c("UTF-8", "latin1", "UTF-8-BOM", "CP1252")
  for (enc in encs) {
    df <- try(suppressWarnings(
      readr::read_csv(ruta, locale = readr::locale(encoding = enc),
                      show_col_types = FALSE, progress = FALSE)
    ), silent = TRUE)
    if (!inherits(df, "try-error") && ncol(df) > 1) return(as.data.frame(df))
  }
  stop(sprintf("No se pudo leer %s con ninguna codificación conocida.", ruta))
}
```

Función auxiliar que intenta leer un CSV probando varias codificaciones. Análisis línea a línea:

- `function(ruta) { ... }` declara una función con un único parámetro `ruta` (en R, las funciones son objetos, igual que en Python).
- `try(..., silent = TRUE)` ejecuta la expresión y captura cualquier error sin imprimirlo, devolviendo un objeto especial de clase `"try-error"` si falla.
- `readr::read_csv()` lee el CSV. El doble dos puntos `::` accede a una función específica de un paquete sin haberlo cargado (útil para evitar conflictos). Parámetros:
  - `locale = readr::locale(encoding = enc)`: fija la codificación del archivo.
  - `show_col_types = FALSE`: silencia el resumen de tipos de cada columna.
  - `progress = FALSE`: silencia la barra de progreso.
- `inherits(df, "try-error")` comprueba si el objeto `df` es resultado de un error.
- `ncol(df) > 1` es una salvaguarda: si la codificación equivocada hace que todo el archivo se lea como una sola columna, se considera fallida y se prueba la siguiente.
- `return(as.data.frame(df))` devuelve el DataFrame convertido a `data.frame` base de R (en lugar del `tibble` que `readr` produce por defecto), para mayor compatibilidad con código clásico.

---

```r
dataframes <- list()
for (i in seq_along(archivos)) {
  anio <- if (i <= length(anios_orden)) anios_orden[i] else 9000L + i
  df   <- leer_csv(archivos[i])
  df$AÑO <- anio
  dataframes[[as.character(anio)]] <- df
  cat(sprintf(...))
}
```

- `list()` crea una lista vacía (equivalente a un `dict` de Python con claves de texto).
- `seq_along(archivos)` genera la secuencia `1, 2, ..., length(archivos)` (equivalente a `range(len(archivos))` en Python pero con base 1).
- `9000L + i`: el sufijo `L` declara enteros literales en R. Es un fallback por si el usuario subió más archivos que años.
- `df$AÑO <- anio` agrega una columna nueva al `data.frame`. El operador `$` accede a columnas por nombre.
- `dataframes[[as.character(anio)]] <- df` guarda cada DataFrame en la lista, indexado por el año como texto. `[[ ]]` es el acceso por nombre/posición en listas (extrae el elemento), a diferencia de `[ ]` que devuelve una sublista.

---

```r
df_2021 <- dataframes[["2021"]]
df_2022 <- dataframes[["2022"]]
df_2023 <- dataframes[["2023"]]
df_2024 <- dataframes[["2024"]]
```
Variables individuales para acceso directo desde otras celdas si se desea inspeccionar un año en particular.

---

## Celda 5 — Selección de columnas

```r
df_ref <- dataframes[[1]]
todas_las_columnas <- setdiff(colnames(df_ref), "AÑO")
```
Toma el primer DataFrame como referencia (asumiendo que los cuatro tienen el mismo esquema). `colnames()` devuelve los nombres de las columnas (equivalente a `df.columns` de pandas). `setdiff(A, "AÑO")` quita la columna `AÑO` de la lista, porque esa la agregamos nosotros y siempre se conserva.

---

```r
for (i in seq_along(todas_las_columnas)) {
  cat(sprintf("  %4d. %s\n", i - 1L, todas_las_columnas[i]))
}
```
Imprime las columnas numeradas. `i - 1L` empieza la numeración en 0 para que coincida con la indexación del notebook de Python. `%4d` reserva 4 espacios de ancho para el número.

---

```r
columnas_a_conservar <- "TODAS"
```
Variable que el usuario edita. Acepta tres valores: la cadena `"TODAS"`, la cadena `"MINIMAS"` o un vector de nombres de columnas.

---

```r
if (identical(columnas_a_conservar, "TODAS")) {
  columnas_sel <- todas_las_columnas
} else if (identical(columnas_a_conservar, "MINIMAS")) {
  columnas_sel <- intersect(c(COLUMNA_DEPARTAMENTO, COLUMNA_RESULTADO), todas_las_columnas)
} else {
  columnas_sel <- intersect(columnas_a_conservar, todas_las_columnas)
}
```
`identical(a, b)` compara dos objetos por igualdad estricta (más seguro que `==` para cadenas). `intersect()` calcula la intersección de conjuntos: solo conserva columnas que **existen** en los datos, evitando errores si el usuario escribe mal un nombre.

---

```r
for (req in c(COLUMNA_DEPARTAMENTO, COLUMNA_RESULTADO)) {
  if (req %in% todas_las_columnas && !(req %in% columnas_sel)) {
    columnas_sel <- c(columnas_sel, req)
  }
}
```
Garantiza que las dos columnas esenciales (departamento y resultado) siempre estén en la selección, incluso si el usuario las olvidó. `%in%` es el operador "pertenencia" (equivalente a `in` en Python).

---

## Celda 6 — Unión de los 4 DataFrames

```r
cols_keep <- c(columnas_sel, "AÑO")
```
Lista final de columnas a conservar, incluyendo `AÑO`.

---

```r
filtrar <- function(df, cols) {
  cols_existentes <- intersect(cols, colnames(df))
  df[, cols_existentes, drop = FALSE]
}
```
Función auxiliar que extrae sólo las columnas que existen en cada DataFrame individual (algunos años pueden tener columnas faltantes). `df[, cols, drop = FALSE]` selecciona columnas; `drop = FALSE` evita que R degrade el resultado a un vector cuando hay una sola columna.

---

```r
piezas <- lapply(dataframes, filtrar, cols = cols_keep)
df_total <- dplyr::bind_rows(piezas)
```
`lapply(lista, fn, ...)` aplica una función a cada elemento de la lista y devuelve una lista (equivalente a una comprensión de lista en Python). Aquí filtra cada DataFrame año por año.

`dplyr::bind_rows()` concatena los DataFrames verticalmente, igual que `pd.concat()` con `axis=0`. Si una columna existe en unos DataFrames y no en otros, las celdas faltantes se rellenan con `NA`.

---

## Celda 7 — Creación de variables nuevas

### 7.1 — DUMMY_POST

```r
df_total$DUMMY_POST <- ifelse(df_total$AÑO %in% c(2021, 2022), 0L, 1L)
```
`ifelse(condicion, valor_si_TRUE, valor_si_FALSE)` es vectorizado: aplica la condición a cada elemento. Si el año es 2021 o 2022 asigna 0, en caso contrario 1. El sufijo `L` fuerza que el resultado sea entero (no doble), para ahorrar memoria.

Equivale al `df_total['DUMMY_POST'] = df_total['AÑO'].apply(lambda x: 0 if x in [2021, 2022] else 1)` del notebook de Python.

---

```r
tab_dummy <- table(factor(df_total$DUMMY_POST, levels = c(0, 1),
                          labels = c("Pre  (2021-2022)", "Post (2023-2024)")))
print(tab_dummy)
```
`factor()` convierte un vector numérico en una variable categórica con etiquetas legibles. `table()` cuenta frecuencias por categoría. Es el equivalente de `value_counts()` en pandas.

---

### 7.2 — NUM_DEPTO

```r
MAPA_DANE <- c(
  "91" = 1L,
  "5"  = 2L,
  ...
  "11" = NA_integer_   # Bogotá D.C. — EXCLUIDO
)
```
**Vector nombrado** de R: cada elemento tiene un nombre. Esto funciona como un diccionario en Python: `MAPA_DANE["91"]` devuelve `1L`. La clave es texto porque los códigos DANE se manipulan como caracteres.

`NA_integer_` es el valor faltante tipado como entero. Es importante usar la variante tipada (no el `NA` genérico) porque el vector entero debe mantener su tipo homogéneo; mezclar tipos forzaría la conversión a `numeric` o `character`.

---

```r
MAPA_NOMBRE <- c("AMAZONAS" = 1L, "ANTIOQUIA" = 2L, ...)
```
Análogo al `MAPA_DANE` pero por nombre de departamento. Los nombres están en mayúsculas y sin tildes (normalización canónica).

---

```r
col <- df_total[[COLUMNA_DEPARTAMENTO]]
if (is.numeric(col)) {
  df_total$NUM_DEPTO <- MAPA_DANE[as.character(col)]
  tipo_mapa <- "código DANE numérico"
} else {
  col_norm <- toupper(stringi::stri_trans_general(as.character(col), "Latin-ASCII"))
  col_norm <- trimws(col_norm)
  df_total$NUM_DEPTO <- MAPA_NOMBRE[col_norm]
  tipo_mapa <- "nombre de departamento"
}
df_total$NUM_DEPTO <- unname(df_total$NUM_DEPTO)
```

- `df_total[[COL]]` (doble corchete) extrae una columna como vector. Es equivalente a `df_total$COL` pero permite usar una variable como nombre de columna.
- `is.numeric(col)` detecta si la columna es numérica.
- **Caso numérico**: convierte cada valor a texto (`as.character`) y lo busca en `MAPA_DANE`. R hace búsqueda por nombre en vectores nombrados, igual que `dict.get()` en Python.
- **Caso texto**:
  - `stringi::stri_trans_general(x, "Latin-ASCII")` translitera quitando tildes y diacríticos. `"Antioquía"` → `"Antioquia"`, `"Bogotá"` → `"Bogota"`. Es el equivalente a las cuatro líneas de `str.replace('[ÁÀÂÄ]', ...)` del notebook de Python pero **una sola llamada y exhaustiva** (cubre todos los acentos europeos).
  - `toupper()` pone en mayúsculas.
  - `trimws()` quita espacios al inicio y final.
- `unname()` quita los nombres del vector resultante (eran los códigos DANE), para dejar sólo los valores enteros 1–32.

---

### 7.3 — DIST_BOGOTA_KM

```r
DIST_BOGOTA <- c(
  "1" = 1500,
  "2" =  415,
  ...
)
df_total$DIST_BOGOTA_KM <- unname(DIST_BOGOTA[as.character(df_total$NUM_DEPTO)])
```
Vector nombrado con la distancia en kilómetros desde la capital de cada departamento hasta Bogotá. Se indexa con `as.character(NUM_DEPTO)` porque los nombres del vector son cadenas. `unname()` limpia los nombres del resultado.

Equivale al `df_total['DIST_BOGOTA_KM'] = df_total['NUM_DEPTO'].map(DIST_BOGOTA)` del notebook de Python.

---

### 7.4 — PROM_RESULTADO_DEPTO

```r
df_total <- df_total %>%
  dplyr::group_by(.data[[COLUMNA_DEPARTAMENTO]]) %>%
  dplyr::mutate(PROM_RESULTADO_DEPTO = mean(.data[[COLUMNA_RESULTADO]], na.rm = TRUE)) %>%
  dplyr::ungroup() %>%
  as.data.frame()
```

El operador **pipe** `%>%` pasa el resultado de la expresión izquierda como primer argumento de la siguiente. Es equivalente a encadenar métodos con `.` en pandas: `df.groupby().transform()`.

- `group_by(g)` define grupos. `.data[[var]]` es una sintaxis tidy-eval para referirse a una columna usando una variable que contiene el nombre.
- `mutate(nueva = ...)` crea o modifica una columna. Como hay agrupación previa, `mean(...)` se calcula **por grupo** y el valor se asigna a todas las filas del mismo grupo (equivalente a `transform('mean')` de pandas).
- `na.rm = TRUE`: ignora valores faltantes al calcular la media (por defecto, `mean(c(1, NA, 3))` devuelve `NA` si no se especifica).
- `ungroup()` quita la agrupación.
- `as.data.frame()` convierte el `tibble` resultante a `data.frame` clásico.

---

## Celda 8 — Exclusión de Bogotá D.C.

```r
n_antes <- nrow(df_total)
df_total <- df_total[!is.na(df_total$NUM_DEPTO), , drop = FALSE]
df_total$NUM_DEPTO <- as.integer(df_total$NUM_DEPTO)
n_despues <- nrow(df_total)
```

`nrow()` cuenta filas (equivalente a `len(df)` o `df.shape[0]` en pandas).

`df[filas, columnas, drop = FALSE]` es la sintaxis de subsetting clásica de R. Aquí:
- `!is.na(df_total$NUM_DEPTO)` es un vector lógico que es `TRUE` cuando la fila tiene departamento válido (es decir, no es Bogotá D.C. ni quedó sin mapeo).
- El segundo argumento (columnas) queda vacío → conserva todas las columnas.
- `drop = FALSE` mantiene el resultado como `data.frame` incluso si quedara una sola columna.

`as.integer()` fuerza el tipo entero después del filtro, ya que `NA` previo había forzado el tipo a `double`.

---

```r
NOMBRES_DEPTO <- c(
  "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bolívar", "Boyacá",
  ...
)
df_total$NOMBRE_DEPTO <- NOMBRES_DEPTO[df_total$NUM_DEPTO]
```

Vector ordinal: `NOMBRES_DEPTO[1]` = `"Amazonas"`, `NOMBRES_DEPTO[2]` = `"Antioquia"`, ..., `NOMBRES_DEPTO[32]` = `"Vichada"`. La indexación con un vector de enteros (`df_total$NUM_DEPTO`) hace una **búsqueda vectorizada** y devuelve un vector del mismo tamaño con los nombres correspondientes.

---

## Celda 9 — Estadística descriptiva

```r
print(summary(df_total[, vars_ok, drop = FALSE]))
```

`summary()` aplicado a un `data.frame` produce un resumen estadístico **por columna**:
- Para variables numéricas: mínimo, primer cuartil, mediana, media, tercer cuartil, máximo, NA's.
- Para factores: conteo por nivel.

Es el equivalente directo de `df.describe()` de pandas.

---

```r
tab_anio <- as.data.frame(table(AÑO = df_total$AÑO))
names(tab_anio)[2] <- "N_registros"
print(tab_anio, row.names = FALSE)
```

`table()` cuenta frecuencias y devuelve un objeto `table`. `as.data.frame()` lo convierte en un `data.frame` con columnas `AÑO` y `Freq`. Renombramos `Freq` → `N_registros` para que sea más explícito.

---

```r
tabla <- df_total %>%
  dplyr::group_by(NUM_DEPTO, NOMBRE_DEPTO) %>%
  dplyr::summarise(
    Promedio = round(mean(.data[[COLUMNA_RESULTADO]], na.rm = TRUE), 3),
    Desv_Est = round(sd(  .data[[COLUMNA_RESULTADO]], na.rm = TRUE), 3),
    N        = dplyr::n(),
    .groups  = "drop"
  ) %>%
  dplyr::arrange(NUM_DEPTO) %>%
  as.data.frame()
```

Pipeline `dplyr` típico:
- `group_by(NUM_DEPTO, NOMBRE_DEPTO)` agrupa por las dos columnas.
- `summarise()` (a diferencia de `mutate`) **colapsa** los grupos en una sola fila por grupo, con columnas calculadas:
  - `mean(..., na.rm = TRUE)`: media.
  - `sd(...)`: desviación estándar.
  - `dplyr::n()`: cuenta filas del grupo (equivalente a `count()` en pandas).
  - `.groups = "drop"`: quita los grupos automáticamente al terminar.
- `arrange(NUM_DEPTO)`: ordena ascendentemente por número de departamento.

Equivalente al `groupby().agg()` de pandas.

---

## Celda 10 — Visualizaciones

`ggplot2` se basa en la **gramática de gráficos**: un gráfico se construye sumando capas con el operador `+`.

```r
p1 <- ggplot(df_total, aes(x = .data[[COLUMNA_RESULTADO]])) +
  geom_histogram(bins = 60, fill = "#2196F3", color = "white", alpha = 0.85) +
  geom_vline(xintercept = media_gral, color = "red", linetype = "dashed", linewidth = 0.8) +
  ...
```

- `ggplot(data, aes(...))` inicia un gráfico: `data` es el `data.frame` y `aes()` mapea variables a propiedades visuales (eje x, eje y, color).
- `geom_histogram(bins = 60)` agrega un histograma con 60 contenedores.
- `geom_vline(xintercept = ...)` traza una línea vertical (aquí, la media general).
- `annotate("text", ...)` agrega un texto en una posición fija (no ligado a los datos).
- `labs(title=, x=, y=)` define títulos.

---

```r
p2 <- ggplot(df_total, aes(x = factor(AÑO), y = ..., fill = factor(AÑO))) +
  geom_boxplot(outlier.size = 0.5, outlier.alpha = 0.4) +
  scale_fill_manual(values = c("#90CAF9", "#42A5F5", "#FB8C00", "#EF5350")) +
  ...
```

- `factor(AÑO)` convierte el año numérico en una variable categórica, lo que produce un boxplot por cada año.
- `scale_fill_manual(values = ...)` asigna los colores manualmente, en el orden de los niveles del factor (orden alfabético/numérico por defecto).

---

```r
prom_depto <- df_total %>%
  group_by(NUM_DEPTO, NOMBRE_DEPTO) %>%
  summarise(promedio = mean(...), .groups = "drop") %>%
  mutate(NOMBRE_DEPTO = factor(NOMBRE_DEPTO, levels = NOMBRE_DEPTO[order(promedio)]),
         color = ifelse(promedio < media_gral, "bajo", "alto"))
```

Aquí se reordena el factor `NOMBRE_DEPTO` según el promedio para que el `geom_col()` lo muestre ordenado de menor a mayor en el eje vertical. `ggplot` respeta el orden de los niveles del factor.

---

```r
p4 <- ggplot(agg, aes(x = distancia, y = promedio)) +
  geom_point(...) +
  geom_smooth(method = "lm", se = FALSE, color = "red", ...) +
  geom_text(aes(label = NUM_DEPTO), vjust = -0.9, size = 2.5)
```

- `geom_point()`: nube de puntos.
- `geom_smooth(method = "lm")`: agrega una línea de regresión lineal ajustada por mínimos cuadrados (`lm()` internamente). `se = FALSE` oculta la banda de confianza.
- `geom_text(aes(label = ...))`: rotula cada punto con el número de departamento.

---

```r
figura <- (p1 | p2) / (p3 | p4) +
  patchwork::plot_annotation(...)
```

`patchwork` permite componer varios `ggplot` con operadores sobrecargados:
- `p1 | p2`: dos gráficos en una fila.
- `(...) / (...)`: dos filas apiladas verticalmente.
- `plot_annotation()`: agrega un título global a la composición.

---

```r
ggsave("analisis_departamentos.png", figura, width = 16, height = 12,
       dpi = 150, bg = "white")
```

`ggsave()` exporta el último gráfico (o uno específico) como PNG/PDF/SVG/etc. `bg = "white"` fuerza fondo blanco (por defecto `ggplot` puede dejarlo transparente).

---

## Celda 11 — Exportar

```r
readr::write_csv(df_total, nombre_salida)
```

`readr::write_csv()` escribe un `data.frame` a CSV. Es más rápido y predecible que el `write.csv` base. Usa UTF-8 por defecto, sin BOM. El equivalente exacto de la línea `df_total.to_csv(..., encoding='utf-8-sig')` del notebook de Python (aunque sin BOM; si necesita BOM, use `readr::write_excel_csv()` que sí lo agrega).

---

```r
descargado <- tryCatch({
  system(sprintf("python3 -c \"from google.colab import files; files.download('%s')\"",
                 nombre_salida), intern = FALSE) == 0
}, error = function(e) FALSE, warning = function(w) FALSE)
```

Truco para descargar automáticamente en Colab desde R: el runtime R de Colab también tiene `python3` instalado, así que delegamos la descarga al módulo `google.colab.files` mediante `system()`. Si la llamada falla por cualquier razón (entorno fuera de Colab, módulo no disponible), `tryCatch()` captura la excepción y el flag `descargado` queda `FALSE`; en ese caso el usuario simplemente descarga el archivo manualmente desde el panel de archivos.

`tryCatch()` es el equivalente de `try/except` de Python:
- El bloque `{}` es el código que puede fallar.
- `error = function(e) FALSE` captura cualquier error y devuelve `FALSE`.
- `warning = function(w) FALSE` hace lo mismo para advertencias.

---

## Diferencias intencionales con la versión Python

| Tema | Python | R | Motivo |
|------|--------|---|--------|
| Selección de columnas | Widget `ipywidgets` | Variable de texto `"TODAS"` / `"MINIMAS"` / vector | Colab con runtime R no soporta `ipywidgets` |
| Descarga del CSV | `files.download()` nativo | Llamada a `python3` vía `system()` | Mismo efecto, mecanismo distinto |
| Normalización de tildes | 5 `str.replace` regex | `stri_trans_general(x, "Latin-ASCII")` | Una sola llamada exhaustiva en R |
| Suma de gráficos | `plt.subplots(2,2)` | `patchwork::(p1 \| p2) / (p3 \| p4)` | Sintaxis gramatical de `ggplot2` |

El **resultado final** (`datos_analisis_departamentos.csv` y `analisis_departamentos.png`) es **idéntico** entre las dos versiones para un mismo set de CSV de entrada.
