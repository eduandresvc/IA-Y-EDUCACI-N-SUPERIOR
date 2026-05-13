# Disparidades en el Desempeño Saber Pro y su Asociación con el Período de Adopción de IA Generativa (2021–2024)

**Autor:** Eduardo Andrés Victoria Cadena (Código U20191179104)  
**Facultad:** Economía y Administración — Universidad Surcolombiana, Neiva, 2026

---

## Descripción

Este proyecto implementa el análisis empírico descrito en la investigación:
análisis descriptivo comparativo (Parte 1) y modelo de regresión lineal múltiple
por MCO (Parte 2) para estimar la asociación condicional entre el período de
adopción masiva de IA Generativa y los puntajes en habilidades genéricas de
la Prueba Saber Pro.

**Muestra:** 9 IES en 6 departamentos (Bogotá D.C., Antioquia, Valle del Cauca,
Huila, Nariño, Tolima) — programas de Economía, Administración y Contaduría Pública,
años 2021–2024.

---

## Estructura del proyecto

```
IA-Y-EDUCACION-SUPERIOR/
├── R/
│   ├── 00_main.R               # Script principal (ejecutar este)
│   ├── 01_preparar_datos.R     # Carga, filtro y construcción de variables
│   ├── 02_analisis_descriptivo.R  # Parte 1: descriptivos y pruebas bivariadas
│   ├── 03_regresion_ols.R      # Parte 2: modelos MCO (6 × 3 especificaciones)
│   ├── 04_diagnosticos.R       # Diagnósticos: normalidad, BP, VIF, DW, RESET
│   ├── 05_visualizaciones.R    # Figuras 1-7
│   └── utils.R                 # Constantes y funciones auxiliares
├── data/
│   ├── raw/        # Colocar aquí los CSV/SAV de DataICFES (no versionado)
│   └── processed/  # Datos procesados (no versionados)
├── outputs/
│   ├── tablas/     # CSVs con resultados
│   ├── figuras/    # PNGs de las figuras
│   └── modelos/    # RDS de los modelos R
└── README.md
```

---

## Cómo ejecutar

### 1. Obtener los datos

Descargar los microdatos Saber Pro 2021–2024 desde [DataICFES](https://www.icfes.gov.co/data-icfes/)
y guardarlos en `data/raw/` con estos nombres:

```
data/raw/saberpro_2021.csv
data/raw/saberpro_2022.csv
data/raw/saberpro_2023.csv
data/raw/saberpro_2024.csv
```

También se aceptan formatos `.sav` (SPSS) y `.xlsx`.

> **Sin datos reales:** el script detecta la ausencia y genera datos simulados
> para probar el flujo. Los resultados simulados **no** son válidos para el artículo.

### 2. Ejecutar el análisis completo

Desde R (con el directorio de trabajo en la raíz del proyecto):

```r
source("R/00_main.R")
```

O desde terminal:

```bash
Rscript R/00_main.R
```

---

## Variables del modelo

| Variable | Tipo | Descripción |
|---|---|---|
| `puntaje_saberpro_generico` | Dependiente | Promedio 5 módulos genéricos (0-300) |
| `periodo_ia` | Dummy (0/1) | 0 = 2021-2022; 1 = 2023-2024 |
| `d_antioquia`, `d_valle`, `d_huila`, `d_narino`, `d_tolima` | Dummies | Departamento de la IES (ref. Bogotá D.C.) |
| `distancia_bogota_km` | Continua | Km vía terrestre desde capital del dpto. a Bogotá |
| `estrato` | Ordinal 1-6 | Estrato socioeconómico |
| `genero` | Dummy | 0=Femenino, 1=Masculino |
| `nivel_educ_padre` | Ordinal 1-7 | Nivel educativo del padre |
| `estu_trabaja` | Dummy | 1=trabaja |
| `internet` | Dummy | 1=tiene internet en el hogar |
| `area_residencia` | Dummy | 1=urbana |
| `naturaleza_ies` | Dummy | 0=pública, 1=privada |
| `puntaje_saber11` | Continua | Puntaje global Saber 11 |

---

## Especificaciones del modelo

- **Spec 1 (base):** Sin efectos fijos. Errores HC3 + clusterizados por IES.
- **Spec 2 (ef_ies):** Efectos fijos por institución.
- **Spec 3 (ef_mun):** Efectos fijos por tipo de municipio.

Cada especificación se estima para 6 variables dependientes:
puntaje genérico agregado + 5 módulos individuales = **18 modelos en total**.

---

## Diagnósticos implementados

- Normalidad: Shapiro-Wilk (n < 5000) / Kolmogorov-Smirnov (n ≥ 5000)
- Homocedasticidad: Breusch-Pagan
- Multicolinealidad: VIF (umbral > 10)
- Autocorrelación: Durbin-Watson
- Especificación: RESET de Ramsey
- Corrección por pruebas múltiples: Holm y Benjamini-Hochberg

---

## Paquetes R requeridos

```r
tidyverse, haven, readxl, sandwich, lmtest, car, estimatr,
fixest, modelsummary, broom, nortest, tseries,
ggplot2, ggthemes, patchwork, corrplot, viridis, scales,
knitr, kableExtra, flextable
```

Se instalan automáticamente al ejecutar `00_main.R`.

---

## Fuente de datos

ICFES (2023a). *DataICFES: repositorio de microdatos del ICFES.*
https://www.icfes.gov.co/data-icfes/

---

## Limitaciones (design observacional)

Los coeficientes estimados son **asociaciones condicionales**, no efectos causales.
El coeficiente β_IA puede estar sesgado por variables omitidas, confusión temporal
con la pandemia COVID-19 y ausencia de aleatorización (Wooldridge, 2020;
Angrist & Pischke, 2009).
