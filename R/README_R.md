# Análisis de Resultados de Examen por Departamento — Colombia (2021–2024) — Versión R

Notebook de Google Colab (runtime **R**) para la carga, limpieza, enriquecimiento y análisis descriptivo de microdatos de exámenes estandarizados nacionales, organizado en cuatro cortes anuales (2021, 2022, 2023 y 2024) con desagregación a nivel departamental.

> Esta es la **versión R** del notebook `../analisis_departamentos_colombia.ipynb` (versión Python). La lógica de programación, el número de celdas, las variables creadas y los outputs son **idénticos**; sólo cambia el lenguaje y la sintaxis.

---

## Tabla de contenido

1. [Descripción general](#1-descripción-general)
2. [Requisitos](#2-requisitos)
3. [Estructura del notebook](#3-estructura-del-notebook)
4. [Guía de uso paso a paso](#4-guía-de-uso-paso-a-paso)
5. [Variables creadas](#5-variables-creadas)
6. [Referencia de departamentos](#6-referencia-de-departamentos)
7. [Outputs generados](#7-outputs-generados)
8. [Equivalencias Python ↔ R](#8-equivalencias-python--r)
9. [Preguntas frecuentes](#9-preguntas-frecuentes)

---

## 1. Descripción general

El notebook `analisis_departamentos_colombia_R.ipynb` permite consolidar cuatro archivos CSV anuales en un único `data.frame` analítico enriquecido con variables de identificación territorial, temporal y estadística. El flujo completo corre íntegramente en **Google Colab con runtime R**, sin necesidad de instalación local.

### Casos de uso típicos

- Análisis de diferencias en resultados antes y después de un evento o reforma (diseño de diferencias en diferencias).
- Estudio de brechas territoriales entre departamentos colombianos.
- Construcción de bases de datos panel para modelos econométricos o de regresión (alimenta directamente la regresión lineal múltiple por MCO descrita en el trabajo de grado).

---

## 2. Requisitos

| Requisito | Detalle |
|-----------|---------|
| Entorno | Google Colab con runtime **R** (R 4.x) |
| Paquetes | `dplyr`, `readr`, `tidyr`, `ggplot2`, `stringi`, `scales`, `patchwork` — todos se instalan automáticamente si faltan |
| Archivos de entrada | 4 archivos `.csv` con datos de los años 2021, 2022, 2023 y 2024 |
| Codificación soportada | UTF-8, Latin-1, UTF-8-BOM, CP1252 (detección automática) |

> Los archivos CSV deben contener al menos una columna que identifique el departamento (código DANE numérico o nombre en texto) y una columna con el resultado o puntaje del examen.

### Cómo activar el runtime R en Colab

Existen dos formas:

1. **URL directa**: abra el notebook usando la URL `https://colab.to/r` (la primera vez Colab le pedirá confirmación para iniciar el runtime R).
2. **Desde un notebook abierto**: menú **Entorno de ejecución** → **Cambiar tipo de entorno** → seleccione **R** en el desplegable y haga clic en **Guardar**.

---

## 3. Estructura del notebook

El notebook está dividido en **11 celdas** con responsabilidades bien delimitadas (idénticas al notebook de Python):

```
Celda  1 — Librerías (instala/carga paquetes R)
Celda  2 — Configuración (nombres de columnas)        ← editar antes de ejecutar
Celda  3 — Detección de archivos CSV subidos a /content
Celda  4 — DataFrames individuales por año
Celda  5 — Selección de columnas a conservar          ← editar vector
Celda  6 — Unión de los 4 DataFrames (bind_rows)
Celda  7 — Creación de variables nuevas
Celda  8 — Exclusión de Bogotá D.C.
Celda  9 — Estadística descriptiva
Celda 10 — Visualizaciones (ggplot2 + patchwork)
Celda 11 — Exportación del resultado final
```

---

## 4. Guía de uso paso a paso

### Paso 1 — Abrir el notebook en Google Colab con runtime R

1. Ingrese a `https://colab.to/r` (esto crea un notebook nuevo ya con runtime R) o abra Colab y cambie el runtime a R desde el menú **Entorno de ejecución → Cambiar tipo de entorno → R**.
2. Seleccione **Archivo → Subir notebook** y cargue el archivo `analisis_departamentos_colombia_R.ipynb`.

### Paso 2 — Configurar nombres de columnas (Celda 2)

Esta es la única edición obligatoria antes de ejecutar:

```r
# Columna que identifica el departamento en sus CSV
# Si es código numérico DANE:  "ESTU_COD_DEPTO_PRESENTACION"
# Si es nombre en texto:       "ESTU_DEPTO_PRESENTACION"
COLUMNA_DEPARTAMENTO <- "ESTU_COD_DEPTO_PRESENTACION"

# Columna con el resultado o puntaje del examen
# Ejemplos: "MOD_RAZONA_CUANTITAT_PUNT", "PUNT_GLOBAL", "PUNTAJE_TOTAL"
COLUMNA_RESULTADO <- "MOD_RAZONA_CUANTITAT_PUNT"
```

> **Tip:** Para conocer los nombres exactos de sus columnas, puede ejecutar `colnames(df_2021)` después de la Celda 4.

### Paso 3 — Subir los archivos CSV

En Colab abra el **panel de archivos** (ícono de carpeta en la barra lateral izquierda) y **arrastre los 4 archivos `.csv` a la carpeta `/content/`** en orden cronológico: 2021 → 2022 → 2023 → 2024.

La Celda 3 detecta automáticamente todos los `.csv` en `/content/` y los ordena por fecha de carga.

> Si los sube en un orden diferente, edite el vector `anios_orden` en la Celda 4 para que coincida con el orden real de carga.

### Paso 4 — Seleccionar columnas a conservar (Celda 5)

A diferencia del notebook de Python (que usa un widget interactivo `ipywidgets`), en R la selección se hace editando una variable. Tres modos:

| Valor de `columnas_a_conservar` | Acción |
|---------------------------------|--------|
| `"TODAS"` | Mantiene todas las columnas del CSV original |
| `"MINIMAS"` | Conserva únicamente la columna de departamento y la de resultado |
| `c("col1", "col2", ...)` | Conserva sólo las columnas listadas |

Las columnas `AÑO`, `COLUMNA_DEPARTAMENTO` y `COLUMNA_RESULTADO` siempre se conservan automáticamente, independientemente de la selección.

### Paso 5 — Ejecutar las celdas restantes en orden

Ejecute las celdas 6 a 11 en secuencia. Cada celda imprime un resumen de lo que realizó.

---

## 5. Variables creadas

El notebook añade las siguientes columnas al `data.frame` consolidado (idénticas a la versión Python):

### `AÑO`
Año al que pertenece el registro. Se agrega durante la lectura de cada archivo CSV individual.

- Tipo: entero (`integer`)
- Valores: `2021`, `2022`, `2023`, `2024`

---

### `DUMMY_POST`
Variable dicotómica que indica el periodo temporal del registro. Corresponde a la variable `periodo_ia` del trabajo de grado.

| Valor | Significado |
|-------|-------------|
| `0` | Periodo **pre** → el registro corresponde al año 2021 o 2022 |
| `1` | Periodo **post** → el registro corresponde al año 2023 o 2024 |

Esta variable es la **variable de interés** del modelo de regresión lineal múltiple por MCO descrito en la sección 8.4 del trabajo de grado. El coeficiente β_IA asociado captura la diferencia condicional promedio en el puntaje Saber Pro entre la cohorte 2023–2024 (expuesta a la adopción masiva de IA generativa) y la cohorte 2021–2022 (previa).

---

### `NUM_DEPTO`
Identificador numérico ordinal del departamento, de 1 a 32. **Los registros de Bogotá D.C. reciben `NA` y son eliminados del análisis** para que Bogotá opere como categoría de referencia implícita del modelo, tal como se especifica en la sección 8.6 del trabajo de grado.

El notebook detecta automáticamente si la columna de departamento contiene:
- **Código DANE numérico** (ej. `5` para Antioquia, `76` para Valle del Cauca): usa el mapeo DANE estándar.
- **Nombre en texto** (ej. `"ANTIOQUIA"`, `"VALLE DEL CAUCA"`): normaliza mayúsculas y tildes con `stringi::stri_trans_general(x, "Latin-ASCII")` antes de mapear.

Véase la [tabla de referencia completa](#6-referencia-de-departamentos) más abajo.

---

### `DIST_BOGOTA_KM`
Distancia en kilómetros desde la **capital del departamento** hasta **Bogotá D.C.**, medida por carretera (ruta terrestre principal). Para departamentos cuya capital solo se conecta por vía aérea o fluvial (Amazonas, Guainía, Vaupés) se usa la distancia aproximada de la ruta más corta disponible.

Esta variable corresponde a `distancia_bogota_km` del trabajo de grado y se usa como **proxy de centralización geográfica** de la educación superior.

---

### `PROM_RESULTADO_DEPTO`
Promedio del resultado del examen (`COLUMNA_RESULTADO`) calculado sobre **todos los registros del mismo departamento** (sin distinción de año) y asignado como valor constante a cada registro de ese departamento.

Es útil para análisis que requieren un indicador de nivel departamental dentro de una regresión a nivel individual, o para identificar departamentos cuyo desempeño promedio supera o cae por debajo de la media nacional.

---

### `NOMBRE_DEPTO`
Nombre del departamento en texto (columna auxiliar generada en la Celda 8). Sirve para etiquetar visualizaciones y tablas de resultados.

---

## 6. Referencia de departamentos

| Num | Departamento | Capital | Dist. Bogotá (km) |
|-----|-------------|---------|------------------:|
| 1 | Amazonas | Leticia | 1 500 |
| 2 | Antioquia | Medellín | 415 |
| 3 | Arauca | Arauca | 800 |
| 4 | Atlántico | Barranquilla | 1 002 |
| 5 | Bolívar | Cartagena | 1 044 |
| 6 | Boyacá | Tunja | 148 |
| 7 | Caldas | Manizales | 308 |
| 8 | Caquetá | Florencia | 487 |
| 9 | Casanare | Yopal | 360 |
| 10 | Cauca | Popayán | 594 |
| 11 | Cesar | Valledupar | 1 011 |
| 12 | Chocó | Quibdó | 529 |
| 13 | Córdoba | Montería | 821 |
| 14 | Cundinamarca | Bogotá | 0 |
| 15 | Guainía | Inírida | 1 800 |
| 16 | Guaviare | San José del Guaviare | 679 |
| 17 | Huila | Neiva | 303 |
| 18 | La Guajira | Riohacha | 1 204 |
| 19 | Magdalena | Santa Marta | 1 096 |
| 20 | Meta | Villavicencio | 89 |
| 21 | Nariño | Pasto | 869 |
| 22 | Norte de Santander | Cúcuta | 605 |
| 23 | Putumayo | Mocoa | 612 |
| 24 | Quindío | Armenia | 291 |
| 25 | Risaralda | Pereira | 341 |
| 26 | San Andrés y Providencia | San Andrés | 752 |
| 27 | Santander | Bucaramanga | 396 |
| 28 | Sucre | Sincelejo | 942 |
| 29 | Tolima | Ibagué | 204 |
| 30 | Valle del Cauca | Cali | 462 |
| 31 | Vaupés | Mitú | 1 600 |
| 32 | Vichada | Puerto Carreño | 1 395 |
| — | **Bogotá D.C.** | — | **EXCLUIDA (categoría de referencia)** |

---

## 7. Outputs generados

Al finalizar la ejecución completa el notebook produce dos archivos:

| Archivo | Descripción |
|---------|-------------|
| `datos_analisis_departamentos.csv` | `data.frame` final con todas las columnas seleccionadas más las variables nuevas. Escrito con `readr::write_csv()`. |
| `analisis_departamentos.png` | Figura con 4 paneles compuestos con `patchwork`: histograma de puntajes, boxplot por año, promedio por departamento y dispersión distancia vs promedio. |

### Estructura del CSV de salida

```
AÑO | DUMMY_POST | NUM_DEPTO | NOMBRE_DEPTO | DIST_BOGOTA_KM | PROM_RESULTADO_DEPTO
```

---

## 8. Equivalencias Python ↔ R

Esta tabla sintetiza las equivalencias entre los dos notebooks para facilitar el mantenimiento paralelo.

| Operación | Python | R |
|-----------|--------|---|
| Leer CSV | `pd.read_csv()` | `readr::read_csv()` |
| Agregar columna | `df['x'] = ...` | `df$x <- ...` |
| Concatenar DataFrames | `pd.concat([...])` | `dplyr::bind_rows(...)` |
| Filtrar filas | `df[df['x'].notna()]` | `df[!is.na(df$x), ]` |
| `groupby` + transformación | `df.groupby('g')['x'].transform('mean')` | `df %>% group_by(g) %>% mutate(prom = mean(x))` |
| Mapeo diccionario | `serie.map(dict)` | `vector_nombrado[as.character(serie)]` |
| Normalizar tildes | `str.replace('[ÁÀ]', 'Á', regex=True)` | `stringi::stri_trans_general(x, "Latin-ASCII")` |
| Histograma | `plt.hist()` | `geom_histogram()` |
| Boxplot | `plt.boxplot()` | `geom_boxplot()` |
| Subplots | `plt.subplots(2,2)` | `patchwork::(p1 \| p2) / (p3 \| p4)` |
| Exportar CSV | `df.to_csv(..., encoding='utf-8-sig')` | `readr::write_csv(df, ...)` |

---

## 9. Preguntas frecuentes

**¿Por qué la celda 5 no usa un widget interactivo como la versión Python?**
Colab con runtime R no tiene soporte nativo para `ipywidgets`. La alternativa es editar directamente el vector `columnas_a_conservar`, lo cual es igualmente expresivo en R y mantiene el flujo idéntico.

**¿Qué sucede si mis archivos tienen distintas columnas entre años?**
`dplyr::bind_rows()` rellena automáticamente con `NA` las columnas que no existan en alguno de los DataFrames, igual que `pd.concat()` en Python.

**¿Puedo usar nombres de departamento con tildes o en minúsculas?**
Sí. El notebook normaliza el texto a mayúsculas y reemplaza los caracteres acentuados con `stringi::stri_trans_general(x, "Latin-ASCII")` antes de hacer el mapeo. Funciona con variantes como `"Antioquia"`, `"ANTIOQUIA"` o `"antioquia"`.

**¿Qué pasa si mi columna de departamento usa un código diferente al DANE?**
Deberá editar el vector nombrado `MAPA_NOMBRE` o `MAPA_DANE` en la Celda 7 para agregar su propio esquema de codificación.

**¿Por qué Cundinamarca tiene distancia 0 km a Bogotá?**
La capital oficial del departamento de Cundinamarca es Bogotá D.C. (aunque administrativamente son entidades separadas). El notebook asigna distancia 0 km para reflejar ese hecho. Los registros de **Bogotá D.C. como entidad territorial propia** sí son excluidos del análisis para que opere como categoría de referencia.

**¿Puedo agregar más años o cambiar los periodos de la dummy?**
Sí. En la Celda 4 puede agregar más entradas a `anios_orden` y en la Celda 7 puede modificar la condición de `DUMMY_POST`:
```r
# Ejemplo: dummy para años >= 2023
df_total$DUMMY_POST <- ifelse(df_total$AÑO < 2023, 0L, 1L)
```

**¿La salida es 100 % idéntica a la del notebook de Python?**
Sí en estructura y contenido (mismas variables, mismos filtros, mismos cálculos). El archivo `datos_analisis_departamentos.csv` resultante de ambos notebooks es intercambiable.
