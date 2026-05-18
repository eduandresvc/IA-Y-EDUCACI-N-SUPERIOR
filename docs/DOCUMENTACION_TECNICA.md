# Documentación técnica del proyecto

Investigación:

> **Disparidades en el desempeño Saber Pro y su asociación con el período
> de adopción de IA Generativa (2021–2024)**
> Eduardo Andrés Victoria Cadena. Universidad Surcolombiana, 2026.

---

## 1. Objetivo del proyecto

Estimar, mediante un análisis descriptivo comparativo (Parte 1) y un
modelo de regresión lineal múltiple por MCO (Parte 2), la asociación
condicional entre el período de adopción masiva de IA generativa
(`periodo_ia = 1` para 2023–2024) y los puntajes en competencias
genéricas de la Prueba Saber Pro, controlando por variables
socioeconómicas, demográficas, académicas, institucionales y
geográficas. La fuente única de datos es DataICFES.

---

## 2. Funcionamiento general del sistema

El sistema se compone de **tres módulos Python independientes** que se
ejecutan en cadena y se comunican a través de archivos en disco.

```
        ┌─────────────────────────┐
   txt  │  1. preparar_datos.py   │ ── procesados/df_consolidado.csv
DataICFES│  (limpieza + variables) │
        └─────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │  2. analisis_descriptivo.py  │ ── resultados/tabla3_*.csv
   │  (Parte 1, §9 del documento) │    figuras/*.png
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │  3. regresion_mco.py         │ ── resultados/tabla4_*.csv
   │  (Parte 2, §8 y §10)         │    diagnosticos.csv
   └──────────────────────────────┘    beta_ia_resumen.csv
```

Un cuarto módulo, `main.py`, orquesta los tres anteriores.

---

## 3. Estructura del código

```
python/
├── preparar_datos.py          # módulo 1: limpieza y construcción de variables
├── analisis_descriptivo.py    # módulo 2: Parte 1 (Tabla 3 + figuras)
├── regresion_mco.py           # módulo 3: Parte 2 (18 modelos MCO)
├── main.py                    # orquestador
└── (notebooks históricos)     # 00_*.ipynb … 05_*.ipynb (versión previa)
docs/
├── DOCUMENTACION_TECNICA.md   # este documento
└── GUIA_EDUCATIVA.md          # glosario didáctico del código
```

Cada módulo expone:

- Un conjunto de **constantes** públicas (en MAYÚSCULAS).
- Funciones reutilizables documentadas (`construir_*`,
  `estimar_modelo`, `figura_*`, etc.).
- Un punto de entrada (`ejecutar_pipeline` /
  `ejecutar_analisis_descriptivo` / `ejecutar_regresion`).
- Una interfaz de línea de comandos vía `argparse`.

---

## 4. Dependencias

| Paquete         | Versión recomendada | Usado por |
|-----------------|---------------------|-----------|
| Python          | ≥ 3.10              | Todos. |
| `pandas`        | ≥ 1.5               | Todos. |
| `numpy`         | ≥ 1.23              | Todos. |
| `scipy`         | ≥ 1.10              | `analisis_descriptivo` (t, χ², MW), `regresion_mco` (Shapiro, KS). |
| `statsmodels`   | ≥ 0.14              | `regresion_mco` (OLS, BP, RESET, VIF, DW, Holm, BH). |
| `matplotlib`    | ≥ 3.5               | `analisis_descriptivo` (cuatro figuras). |

Instalación rápida:

```bash
pip install pandas numpy scipy statsmodels matplotlib
```

---

## 5. Módulo 1 — `preparar_datos.py`

### 5.1 Responsabilidad

Cargar los `.txt` de DataICFES, leer **sólo las 19 columnas necesarias**
del diccionario oficial, construir las variables del estudio con
**drop incremental** (la columna cruda se elimina apenas se usa) y
producir un dataframe por año (`df_2021…df_2024`) más el consolidado.

### 5.2 Distinción Tabla 2 vs Tabla 3

| Conjunto | Tabla del documento | Finalidad | Contenido |
|---|---|---|---|
| `VARIABLES_DESCRIPTIVO` | Tabla 3 | Análisis bivariado (Parte 1). | id, anio, periodo_ia, 5 puntajes + agregado, estrato, genero, estu_trabaja, internet, naturaleza_ies. |
| `VARIABLES_MODELO` | Tabla 2 | Regresión MCO (Parte 2). | Todo lo anterior + edad, nivel_educ_padre, estu_cabeza_familia, jornada, area_residencia, departamento (0-32) + departamento_nombre, distancia_bogota_km, cod_ies, municipio_ies, tipo_municipio. |

La unión (`VARIABLES_FINALES`, 25 columnas) es lo que el dataframe
final conserva.

### 5.3 Columnas leídas (diccionario DataICFES, sección 2)

| Campo crudo | Variable producida | Conjunto |
|---|---|---|
| `estu_consecutivo` | `id_estudiante` | Ambos |
| `mod_lectura_critica_punt` | `punt_lectura_critica` | Ambos |
| `mod_razona_cuantitat_punt` | `punt_razona_cuant` | Ambos |
| `mod_competen_ciudada_punt` | `punt_competen_ciud` | Ambos |
| `mod_comuni_escrita_punt` | `punt_comuni_escrita` | Ambos |
| `mod_ingles_punt` | `punt_ingles` | Ambos |
| `estu_genero` | `genero` | Ambos |
| `estu_fechanacimiento` | `edad` (luego se elimina) | Modelo |
| `fami_estratovivienda` | `estrato` | Ambos |
| `fami_educacionpadre` | `nivel_educ_padre` | Modelo |
| `estu_horassemanatrabaja` | `estu_trabaja` | Ambos |
| `estu_pagomatriculapadres` | `estu_cabeza_familia` (proxy) | Modelo |
| `fami_tieneinternet` | `internet` | Ambos |
| `estu_areareside` | `area_residencia` | Modelo |
| `estu_metodo_prgm` | `jornada` (proxy) | Modelo |
| `inst_origen` | `naturaleza_ies` | Ambos |
| `inst_cod_institucion` | `cod_ies` | Aux. EF IES |
| `estu_inst_departamento` | `departamento`, `departamento_nombre`, `distancia_bogota_km` | Modelo |
| `estu_inst_municipio` | `municipio_ies`, `tipo_municipio` | Aux. EF mun. |

### 5.4 Drop incremental de columnas

| Paso | Función | Crea | Elimina |
|----:|---|---|---|
| 1 | `transformar_id_y_modulos` | id + 5 puntajes | (rename) |
| 2 | `construir_periodo_ia` | `periodo_ia` | — |
| 3 | `construir_puntaje_generico` | agregado | — |
| 4 | `construir_edad` | `edad` | `estu_fechanacimiento` |
| 5 | `construir_genero` | `genero` | `estu_genero` |
| 6 | `construir_estrato` | `estrato` | `fami_estratovivienda` |
| 7 | `construir_nivel_educ_padre` | `nivel_educ_padre` | `fami_educacionpadre` |
| 8 | `construir_estu_trabaja` | `estu_trabaja` | `estu_horassemanatrabaja` |
| 9 | `construir_cabeza_familia` | `estu_cabeza_familia` | `estu_pagomatriculapadres` |
| 10 | `construir_jornada` | `jornada` | `estu_metodo_prgm` |
| 11 | `construir_internet` | `internet` | `fami_tieneinternet` |
| 12 | `construir_area_residencia` | `area_residencia` | `estu_areareside` |
| 13 | `construir_naturaleza_ies` | `naturaleza_ies` | `inst_origen` |
| 14 | `construir_departamento_y_distancia` | 3 vars geo | `estu_inst_departamento` |
| 15 | `construir_identificadores_fe` | `cod_ies`, `municipio_ies` | (rename) |
| 16 | `construir_tipo_municipio` | `tipo_municipio` | — (`municipio_ies` se conserva para EF) |

### 5.5 Limpieza

- Puntajes fuera de [0, 300] → `NaN`.
- Edades fuera de [15, 80] → `NaN`.
- Estratos fuera de [1, 6] → `NaN`.
- Filas sin `puntaje_saberpro_generico` → eliminadas.
- Filas sin `departamento` → eliminadas.
- Duplicados por (`id_estudiante`, `anio`) → se conserva el primero.

### 5.6 Ejecución

**Local:**

```bash
python python/preparar_datos.py --ruta /carpeta/con/los_txt
```

**Google Colab:** `--ruta` es opcional; cuando se omite, monta Drive y
usa `/content/drive/MyDrive/IA_EDUCACION_SUPERIOR`:

```python
from preparar_datos import ejecutar_pipeline
dfs, df_consolidado = ejecutar_pipeline()      # equivalente sin args
```

---

## 6. Módulo 2 — `analisis_descriptivo.py`

### 6.1 Responsabilidad

Implementa la **Parte 1** (Sección 9 del documento): comparación
bivariada entre las cohortes 2021–2022 y 2023–2024.

### 6.2 Variables comparadas

- **Continuas / ordinales (10):** los 5 módulos + `puntaje_saberpro_generico`,
  `estrato`, `edad`, `nivel_educ_padre`, `distancia_bogota_km`. Se
  reportan media, desviación, n y se aplican **t de Welch** (no asume
  varianzas iguales) y **Mann–Whitney** (no paramétrica robusta).
- **Dicotómicas (7):** `genero`, `estu_trabaja`, `estu_cabeza_familia`,
  `jornada`, `internet`, `area_residencia`, `naturaleza_ies`. Se
  reportan proporción por cohorte, diferencia en puntos porcentuales y
  **χ² de Pearson** con corrección de Yates.

### 6.3 Salidas

| Archivo | Contenido |
|---|---|
| `procesados/resultados/tabla3_descriptivo.csv` | Tabla 3 completa. |
| `procesados/resultados/tabla3_por_departamento.csv` | Medias × (depto × cohorte). |
| `procesados/figuras/fig_boxplot_periodo.png` | Distribución por cohorte. |
| `procesados/figuras/fig_boxplot_departamento.png` | Distribución por dpto. |
| `procesados/figuras/fig_histograma_cohortes.png` | Histograma comparativo. |
| `procesados/figuras/fig_dispersion_distancia.png` | Dispersión distancia ↔ puntaje. |

### 6.4 Ejecución

```bash
python python/analisis_descriptivo.py --ruta /carpeta/con/procesados
```

---

## 7. Módulo 3 — `regresion_mco.py`

### 7.1 Responsabilidad

Implementa la **Parte 2** (Secciones 8 y 10 del documento): 6
variables dependientes × 3 especificaciones = **18 modelos MCO**.

### 7.2 Especificaciones

| Spec | Términos en `X` | Notas |
|---|---|---|
| `base` | `periodo_ia` + dummies de `departamento` (Bogotá D.C. = referencia) + `distancia_bogota_km` + 10 controles. | Especificación principal. |
| `ef_ies` | `periodo_ia` + EF por `cod_ies` + 10 controles. | `departamento` y `distancia` quedan absorbidos por la IES (cada IES está en un solo dpto.). |
| `ef_mun` | base + EF por `tipo_municipio` (0=Bogotá, 1=capital, 2=resto). | Permite separar el efecto del tipo de municipio del efecto departamental. |

Todos los modelos usan **errores estándar clusterizados por IES**
(`cov_type='cluster'`, `cov_kwds={'groups': cod_ies}`).

### 7.3 Triángulo de colinealidad geográfica

Sobre `puntaje_saberpro_generico`, se reportan tres versiones (§10
del documento):

- (a) sólo `departamento`,
- (b) sólo `distancia_bogota_km`,
- (c) ambos (con VIF para diagnosticar colinealidad).

### 7.4 Diagnósticos (Sección 8.10)

Por cada uno de los 18 modelos se reporta:

- **Normalidad de residuos:** Shapiro–Wilk si n < 5 000, KS en otro
  caso.
- **Homocedasticidad:** Breusch–Pagan.
- **Autocorrelación:** Durbin–Watson.
- **Especificación:** RESET de Ramsey.
- **Multicolinealidad:** VIF (umbral > 10), sólo en Spec `base`.

### 7.5 Corrección por pruebas múltiples (Sección 12)

Sobre los 6 valores p de β_IA (uno por dependiente) **dentro de cada
especificación**, se aplican:

- **Holm** (control de FWER).
- **Benjamini–Hochberg** (control de FDR).

Las columnas `sig_5pct_holm` y `sig_5pct_bh` indican si el coeficiente
sobrevive cada corrección.

### 7.6 Salidas

| Archivo | Contenido |
|---|---|
| `procesados/resultados/tabla4_coeficientes.csv` | Todos los coeficientes de los 18 modelos. |
| `procesados/resultados/diagnosticos.csv` | Las 5 pruebas por modelo. |
| `procesados/resultados/beta_ia_resumen.csv` | β_IA con p crudo, Holm y BH. |
| `procesados/resultados/colinealidad_geografica.csv` | Triángulo (a)/(b)/(c). |

### 7.7 Ejecución

```bash
python python/regresion_mco.py --ruta /carpeta/con/procesados
```

---

## 8. Módulo 4 — `main.py`

Orquestador único que encadena los tres módulos.

```bash
# Local:
python python/main.py --ruta /carpeta/con/los_txt

# Solo regresión, reusando `procesados/` existente:
python python/main.py --ruta /carpeta --solo regresion

# Reanudar tras preparar_datos sin volver a ejecutarlo:
python python/main.py --ruta /carpeta --saltar-preparar
```

En Colab basta:

```python
from main import ejecutar_todo
ejecutar_todo()                    # ruta por defecto en Drive
ejecutar_todo(correr_preparar=False)   # solo descriptivo + regresión
```

---

## 8.bis Ejecución en Google Colab

Hay tres formas equivalentes, en orden de preferencia:

### a) Cuaderno listo (recomendado)

Abrir `python/pipeline_colab.ipynb` en Colab y ejecutar las celdas en
orden. El cuaderno se encarga del montaje de Drive, la copia de los
scripts desde Drive a `/content/` y la ejecución de las tres partes.

### b) Ejecutar los módulos directamente

```python
# Celda 1 — montar Drive
from google.colab import drive
drive.mount('/content/drive')

# Celda 2 — hacer accesibles los .py
import sys, shutil, os
DRIVE = '/content/drive/MyDrive/IA_EDUCACION_SUPERIOR'
for s in ('preparar_datos.py', 'analisis_descriptivo.py',
          'regresion_mco.py', 'main.py'):
    src = os.path.join(DRIVE, 'python', s)
    if os.path.exists(src):
        shutil.copy(src, '/content')
sys.path.insert(0, '/content')

# Celda 3 — pipeline completo (ruta automática a Drive)
from main import ejecutar_todo
ejecutar_todo()
```

### c) Vía CLI con `%run`

```python
%run /content/main.py
# o, para una sola parte:
%run /content/regresion_mco.py
```

En cualquiera de las tres modalidades:

- `ruta_proyecto=None` (predeterminado) ⇒ se monta Drive y se usa
  `Mi unidad/IA_EDUCACION_SUPERIOR`.
- Las dependencias (`scipy`, `statsmodels`, `matplotlib`) se
  auto-instalan si llegasen a faltar (en Colab moderno ya están
  preinstaladas).

---

## 9. Trazabilidad con el documento

| Documento | Implementación |
|---|---|
| §8.2 — Fuente DataICFES | `preparar_datos.COLS_REQUERIDAS` |
| §8.3 — Variable dependiente | `construir_puntaje_generico` |
| §8.4 — `periodo_ia` | `construir_periodo_ia` |
| §8.5 — Controles | 10 funciones `construir_*` |
| §8.5 (i) — Departamento 0–32 | `DEPARTAMENTOS`, `construir_departamento_y_distancia` |
| §8.5 (ii) — `distancia_bogota_km` | `construir_departamento_y_distancia` |
| §8.8 — Especificación del modelo | `regresion_mco._formula` |
| §8.9 — EF IES y EF tipo de municipio | Specs `ef_ies` y `ef_mun` |
| §8.10 — Diagnósticos | `regresion_mco.diagnosticos` |
| §9 — Análisis bivariado | `analisis_descriptivo` (módulo completo) |
| §10 — Triángulo de colinealidad | `regresion_mco.colinealidad_geografica` |
| §12 — Corrección por pruebas múltiples | `regresion_mco.aplicar_correcciones` |
| Tabla 1 | `DEPARTAMENTOS`, `CAPITALES` |
| Tabla 2 | `VARIABLES_MODELO` |
| Tabla 3 | `VARIABLES_DESCRIPTIVO`, `analisis_descriptivo.tabla3_descriptivo` |
| Tabla 4 | `regresion_mco.tabla4_un_modelo` |

---

## 10. Estructura de archivos generados

Después de una corrida completa:

```
<ruta_proyecto>/
├── Examen_Saber_Pro_Genericas_2021.txt      (entrada)
├── … 2022.txt … 2023.txt … 2024.txt
└── procesados/
    ├── df_2021.csv      (preparación)
    ├── df_2022.csv
    ├── df_2023.csv
    ├── df_2024.csv
    ├── df_consolidado.csv
    ├── resultados/
    │   ├── tabla3_descriptivo.csv          (Parte 1)
    │   ├── tabla3_por_departamento.csv
    │   ├── tabla4_coeficientes.csv         (Parte 2)
    │   ├── diagnosticos.csv
    │   ├── beta_ia_resumen.csv
    │   └── colinealidad_geografica.csv
    └── figuras/
        ├── fig_boxplot_periodo.png
        ├── fig_boxplot_departamento.png
        ├── fig_histograma_cohortes.png
        └── fig_dispersion_distancia.png
```

---

## 11. Limitaciones del sistema

- `estu_areareside` aparece marcada con `*` (pendiente por publicación)
  para 2024 en el diccionario DataICFES; cuando falte, la variable
  `area_residencia` queda `NaN`.
- `estu_horario_prgm` no existe en 2021–2024 ⇒ `jornada` se aproxima
  desde `estu_metodo_prgm` (no presencial = 1).
- `estu_cabeza_familia` es proxy desde `estu_pagomatriculapadres`.
- `tipo_municipio` se clasifica como Bogotá / capital de otro dpto. /
  resto. No usa la tipología DANE detallada por categorías de Ley 617.
- `distancia_bogota_km` es una sola distancia por departamento (Tabla 1
  del documento); no captura dispersión intra-departamental.
- En `ef_ies` los contrastes departamentales y la distancia quedan
  absorbidos (cada IES está en un único departamento), tal como advierte
  §8.9 del documento. Se reportan, pero su lectura geográfica corresponde
  a las otras dos especificaciones.

---

## 12. Mantenimiento

- **Añadir un año**: incluirlo en `ANIOS` y, según corresponda, en
  `ANIOS_PREVIO` o `ANIOS_IA`. Colocar el `.txt` en la carpeta.
- **Añadir una variable de control**: agregar el nombre crudo a
  `COLS_REQUERIDAS`, implementar `construir_<nueva>` (con drop de la
  fuente), llamarla desde `construir_todas_las_variables` y añadirla
  a `VARIABLES_MODELO` y/o `VARIABLES_DESCRIPTIVO`. Para que entre
  además al MCO, añadirla a `CONTROLES` en `regresion_mco.py`.
- **Cambiar la lista de dependientes**: editar `DEPENDIENTES` en
  `regresion_mco.py`.
- **Otra corrección de pruebas múltiples**: pasar otro `method` a
  `multipletests` (p. ej. `"bonferroni"`).
