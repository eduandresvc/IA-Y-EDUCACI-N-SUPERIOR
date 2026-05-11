# Análisis de Resultados de Examen por Departamento — Colombia (2021–2024)

Notebook de Google Colab para la carga, limpieza, enriquecimiento y análisis descriptivo de microdatos de exámenes estandarizados nacionales, organizado en cuatro cortes anuales (2021, 2022, 2023 y 2024) con desagregación a nivel departamental.

---

## Tabla de contenido

1. [Descripción general](#1-descripción-general)
2. [Requisitos](#2-requisitos)
3. [Estructura del notebook](#3-estructura-del-notebook)
4. [Guía de uso paso a paso](#4-guía-de-uso-paso-a-paso)
5. [Variables creadas](#5-variables-creadas)
6. [Referencia de departamentos](#6-referencia-de-departamentos)
7. [Outputs generados](#7-outputs-generados)
8. [Preguntas frecuentes](#8-preguntas-frecuentes)

---

## 1. Descripción general

El notebook `analisis_departamentos_colombia.ipynb` permite consolidar cuatro archivos CSV anuales en un único DataFrame analítico enriquecido con variables de identificación territorial, temporal y estadística. El flujo completo corre íntegramente en Google Colab, sin necesidad de instalación local.

### Casos de uso típicos

- Análisis de diferencias en resultados antes y después de un evento o reforma (diseño de diferencias en diferencias).
- Estudio de brechas territoriales entre departamentos colombianos.
- Construcción de bases de datos panel para modelos econométricos o de regresión.

---

## 2. Requisitos

| Requisito | Detalle |
|-----------|---------|
| Entorno | Google Colab (Python 3.10+) |
| Librerías | `pandas`, `numpy`, `matplotlib`, `seaborn`, `ipywidgets` — todas preinstaladas en Colab |
| Archivos de entrada | 4 archivos `.csv` con datos de los años 2021, 2022, 2023 y 2024 |
| Codificación soportada | UTF-8, Latin-1, UTF-8-BOM, CP1252 (detección automática) |

> Los archivos CSV deben contener al menos una columna que identifique el departamento (código DANE numérico o nombre en texto) y una columna con el resultado o puntaje del examen.

---

## 3. Estructura del notebook

El notebook está dividido en **11 celdas** con responsabilidades bien delimitadas:

```
Celda  1 — Librerías e importaciones
Celda  2 — Configuración (nombres de columnas)        ← editar antes de ejecutar
Celda  3 — Carga de archivos CSV
Celda  4 — DataFrames individuales por año
Celda  5 — Selector interactivo de columnas
Celda  6 — Unión de los 4 DataFrames
Celda  7 — Creación de variables nuevas
Celda  8 — Exclusión de Bogotá D.C.
Celda  9 — Estadística descriptiva
Celda 10 — Visualizaciones
Celda 11 — Exportación del resultado final
```

---

## 4. Guía de uso paso a paso

### Paso 1 — Abrir el notebook en Google Colab

1. Ingrese a [colab.research.google.com](https://colab.research.google.com).
2. Seleccione **Archivo → Subir notebook** y cargue el archivo `analisis_departamentos_colombia.ipynb`.

### Paso 2 — Configurar nombres de columnas (Celda 2)

Esta es la única edición obligatoria antes de ejecutar. Localice las dos variables de configuración y ajústelas al nombre exacto de sus columnas:

```python
# Columna que identifica el departamento en sus CSV
# Si es código numérico DANE:  'ESTU_COD_DEPTO_PRESENTACION'
# Si es nombre en texto:       'ESTU_DEPTO_PRESENTACION'
COLUMNA_DEPARTAMENTO = 'ESTU_COD_DEPTO_PRESENTACION'

# Columna con el resultado o puntaje del examen
# Ejemplos: 'MOD_RAZONA_CUANTITAT_PUNT', 'PUNT_GLOBAL', 'PUNTAJE_TOTAL'
COLUMNA_RESULTADO = 'MOD_RAZONA_CUANTITAT_PUNT'
```

> **Tip:** Para conocer los nombres exactos de sus columnas, puede ejecutar `df_2021.columns.tolist()` después de la Celda 4.

### Paso 3 — Subir los archivos CSV (Celda 3)

Al ejecutar la Celda 3 aparecerá el botón **Elegir archivos**. Suba los 4 archivos **en orden cronológico**: 2021 → 2022 → 2023 → 2024.

> Si los sube en un orden diferente, edite la lista `años_orden` en la Celda 4 para que coincida con el orden real de carga.

### Paso 4 — Seleccionar columnas a conservar (Celda 5)

La Celda 5 despliega un **widget interactivo** con todas las columnas disponibles:

| Botón | Acción |
|-------|--------|
| **Conservar TODAS** | Mantiene todas las columnas del CSV original |
| **Solo mínimas** | Conserva únicamente la columna de departamento y la de resultado |
| **✔ Confirmar** | Aplica la selección realizada con Ctrl+Click en la lista |

Las columnas `AÑO`, `COLUMNA_DEPARTAMENTO` y `COLUMNA_RESULTADO` siempre se conservan automáticamente, independientemente de la selección, porque son necesarias para el análisis.

### Paso 5 — Ejecutar las celdas restantes en orden

Ejecute las celdas 6 a 11 en secuencia. Cada celda imprime un resumen de lo que realizó.

---

## 5. Variables creadas

El notebook añade las siguientes columnas al DataFrame consolidado:

### `AÑO`
Año al que pertenece el registro. Se agrega durante la lectura de cada archivo CSV individual.

- Tipo: entero
- Valores: `2021`, `2022`, `2023`, `2024`

---

### `DUMMY_POST`
Variable dicotómica que indica el periodo temporal del registro.

| Valor | Significado |
|-------|-------------|
| `0` | Periodo **pre** → el registro corresponde al año 2021 o 2022 |
| `1` | Periodo **post** → el registro corresponde al año 2023 o 2024 |

Esta variable es útil para diseños de evaluación de impacto como **diferencias en diferencias (DiD)**, donde se compara el comportamiento de una variable antes y después de una intervención o evento.

---

### `NUM_DEPTO`
Identificador numérico ordinal del departamento, de 1 a 32. **Los registros de Bogotá D.C. reciben `NaN` y son eliminados del análisis.**

El notebook detecta automáticamente si la columna de departamento contiene:
- **Código DANE numérico** (ej. `5` para Antioquia, `76` para Valle del Cauca): usa el mapeo DANE estándar.
- **Nombre en texto** (ej. `"ANTIOQUIA"`, `"VALLE DEL CAUCA"`): normaliza mayúsculas y tildes antes de mapear.

Véase la [tabla de referencia completa](#6-referencia-de-departamentos) más abajo.

---

### `DIST_BOGOTA_KM`
Distancia en kilómetros desde la **capital del departamento** hasta **Bogotá D.C.**, medida por carretera (ruta terrestre principal). Para departamentos cuya capital solo se conecta por vía aérea o fluvial (Amazonas, Guainía, Vaupés) se usa la distancia aproximada de la ruta más corta disponible.

Esta variable puede emplearse como **proxy de centralización geográfica** o de acceso a servicios del nivel nacional.

| Departamento | Capital | Distancia (km) |
|---|---|---:|
| Meta | Villavicencio | 89 |
| Boyacá | Tunja | 148 |
| Tolima | Ibagué | 204 |
| Quindío | Armenia | 291 |
| Huila | Neiva | 303 |
| Caldas | Manizales | 308 |
| Risaralda | Pereira | 341 |
| Casanare | Yopal | 360 |
| Antioquia | Medellín | 415 |
| Valle del Cauca | Cali | 462 |
| Caquetá | Florencia | 487 |
| Chocó | Quibdó | 529 |
| Cauca | Popayán | 594 |
| Norte de Santander | Cúcuta | 605 |
| Putumayo | Mocoa | 612 |
| Guaviare | San José del Guaviare | 679 |
| San Andrés y Prov. | San Andrés | 752 (aérea) |
| Arauca | Arauca | 800 |
| Córdoba | Montería | 821 |
| Nariño | Pasto | 869 |
| Sucre | Sincelejo | 942 |
| Atlántico | Barranquilla | 1 002 |
| Cesar | Valledupar | 1 011 |
| Bolívar | Cartagena | 1 044 |
| Magdalena | Santa Marta | 1 096 |
| La Guajira | Riohacha | 1 204 |
| Vichada | Puerto Carreño | 1 395 |
| Amazonas | Leticia | 1 500 |
| Vaupés | Mitú | 1 600 (mixta) |
| Guainía | Inírida | 1 800 (mixta) |

> Cundinamarca tiene distancia **0 km** porque su capital departamental es la misma Bogotá D.C.

---

### `PROM_RESULTADO_DEPTO`
Promedio del resultado del examen (`COLUMNA_RESULTADO`) calculado sobre **todos los registros del mismo departamento** (sin distinción de año) y asignado como valor constante a cada registro de ese departamento.

**Ejemplo:** si el departamento de Antioquia tiene 5 000 registros con puntajes entre 100 y 300, todos esos 5 000 registros reciben el mismo valor en `PROM_RESULTADO_DEPTO`, que es la media aritmética de los 5 000 puntajes.

Esta variable es útil para análisis que requieren un indicador de nivel departamental dentro de una regresión a nivel individual, o para identificar departamentos cuyo desempeño promedio supera o cae por debajo de la media nacional.

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
| — | **Bogotá D.C.** | — | **EXCLUIDA** |

---

## 7. Outputs generados

Al finalizar la ejecución completa el notebook produce tres archivos:

| Archivo | Descripción |
|---------|-------------|
| `datos_analisis_departamentos.csv` | DataFrame final con todas las columnas seleccionadas más las variables nuevas. Se descarga automáticamente. |
| `analisis_departamentos.png` | Figura con 4 paneles: histograma de puntajes, boxplot por año, promedio por departamento y dispersión distancia vs promedio. |

### Estructura del CSV de salida

El archivo de salida contiene las columnas seleccionadas por el usuario más:

```
AÑO | DUMMY_POST | NUM_DEPTO | NOMBRE_DEPTO | DIST_BOGOTA_KM | PROM_RESULTADO_DEPTO
```

---

## 8. Preguntas frecuentes

**¿Qué sucede si mis archivos tienen distintas columnas entre años?**
El notebook conserva solo las columnas que existen en cada DataFrame. Si una columna del año 2021 no existe en 2023, los registros de 2023 tendrán `NaN` en esa columna. Se imprime un aviso si ocurre.

**¿Puedo usar nombres de departamento con tildes o en minúsculas?**
Sí. El notebook normaliza el texto a mayúsculas y reemplaza los caracteres acentuados antes de hacer el mapeo. Funciona con variantes como `"Antioquia"`, `"ANTIOQUIA"` o `"antioquia"`.

**¿Qué pasa si mi columna de departamento usa un código diferente al DANE?**
Deberá editar el diccionario `MAPA_NOMBRE` o `MAPA_DANE` en la Celda 7 para agregar su propio esquema de codificación.

**¿Por qué Cundinamarca tiene distancia 0 km a Bogotá?**
La capital oficial del departamento de Cundinamarca es Bogotá D.C. (aunque administrativamente son entidades separadas). El notebook asigna distancia 0 km para reflejar ese hecho. Los registros de **Bogotá D.C. como entidad territorial propia** sí son excluidos del análisis.

**¿Puedo agregar más años o cambiar los periodos de la dummy?**
Sí. En la Celda 4 puede agregar más archivos a la lista `años_orden` y en la Celda 7 puede modificar la condición de `DUMMY_POST`:
```python
# Ejemplo: dummy para años ≥ 2023
df_total['DUMMY_POST'] = df_total['AÑO'].apply(lambda x: 0 if x < 2023 else 1)
```
