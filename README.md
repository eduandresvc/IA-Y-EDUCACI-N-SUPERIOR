# Disparidades en el Desempeño Saber Pro y su Asociación con el Período de Adopción de IA Generativa (2021–2024)

**Autor:** Eduardo Andrés Victoria Cadena (Código U20191179104)  
**Facultad:** Economía y Administración — Universidad Surcolombiana, Neiva, 2026

---

## Descripción

Este proyecto implementa el análisis empírico de la investigación:
análisis descriptivo comparativo (Parte 1) y modelo de regresión lineal múltiple
por MCO (Parte 2) para estimar la asociación condicional entre el período de
adopción masiva de IA Generativa y los puntajes en habilidades genéricas de
la Prueba Saber Pro.

**Muestra:** Todos los registros nacionales de DataICFES 2021–2024 (sin filtro
por institución ni programa). Los 33 departamentos de Colombia + Bogotá D.C.,
con Bogotá como categoría de referencia en el modelo.

---

## 📘 Libro didáctico — `libro/`

Para quien quiera entender **palabra por palabra** cada archivo del
proyecto (los `.py` y los `.ipynb`), abre [`libro/README.md`](./libro/README.md).
Está organizado en ocho capítulos:

1. Python básico (palabras reservadas, operadores, sintaxis).
2. Librerías clave (`pandas`, `numpy`, `scipy`, `statsmodels`, …).
3. `preparar_datos.py` — preparación de microdatos.
4. `analisis_descriptivo.py` — análisis bivariado.
5. `regresion_mco.py` — 18 modelos MCO + diagnósticos.
6. `main.py` — orquestador.
7. Notebooks Colab (`colab_01`, `colab_02`, `colab_03`).
8. Glosario alfabético.

---

## Estructura del proyecto

```
IA-Y-EDUCACION-SUPERIOR/
├── R/
│   ├── 00_main.R                  # Script principal (ejecutar este)
│   ├── 01_preparar_datos.R        # Carga, filtro por año y construcción de variables
│   ├── 02_analisis_descriptivo.R  # Parte 1: descriptivos y pruebas bivariadas
│   ├── 03_regresion_ols.R         # Parte 2: modelos MCO (6 × 3 especificaciones)
│   ├── 04_diagnosticos.R          # Diagnósticos: normalidad, BP, VIF, DW, RESET
│   ├── 05_visualizaciones.R       # Figuras 1-7
│   └── utils.R                    # Constantes y funciones auxiliares
├── python/
│   ├── 00_main.ipynb              # Notebook principal Google Colab
│   ├── 01_preparar_datos.ipynb    # Equivalente Python de 01_preparar_datos.R
│   ├── 02_analisis_descriptivo.ipynb
│   ├── 03_regresion_ols.ipynb
│   ├── 04_diagnosticos.ipynb
│   ├── 05_visualizaciones.ipynb
│   └── utils.py                   # Constantes compartidas Python
├── data/
│   ├── raw/        # Colocar aquí los CSV/SAV de DataICFES (no versionado)
│   └── processed/  # Datos procesados (no versionados)
├── outputs/
│   ├── tablas/     # CSVs con resultados
│   ├── figuras/    # PNGs de las figuras
│   └── modelos/    # RDS / PKL de los modelos
└── README.md
```

---

## Cómo ejecutar

### Versión R

1. Descarga los microdatos Saber Pro 2021–2024 desde [DataICFES](https://www.icfes.gov.co/data-icfes/)
   y colócalos en `data/raw/` como `saberpro_2021.csv` … `saberpro_2024.csv`
   (también acepta `.sav` y `.xlsx`).
2. Desde R, en la raíz del proyecto:

```r
source("R/00_main.R")
```

### Versión Python / Google Colab

1. Sube la carpeta del proyecto a Google Drive.
2. Abre `python/00_main.ipynb` en Colab.
3. Ajusta `RUTA_PROYECTO` a tu ruta en Drive.
4. Ejecuta todas las celdas en orden.

> Sin datos reales, ambas versiones generan datos **simulados** para probar el flujo.
> Los resultados simulados no son válidos para el artículo.

---

## Variable de interés principal

| Variable | Tipo | Descripción |
|---|---|---|
| `periodo_ia` | Dummy (0/1) | 0 = 2021-2022 (pre-IA); 1 = 2023-2024 (adopción masiva IA Gen) |

## Variables geográficas (análisis nacional)

| Variable | Tipo | Descripción |
|---|---|---|
| `depto_ies` | Categórica | 33 departamentos + D.C. — Bogotá = referencia |
| `distancia_bogota_km` | Continua | Km por vía terrestre desde capital del dpto. a Bogotá D.C. |

## Variables de control

| Variable | Tipo | Descripción |
|---|---|---|
| `puntaje_saberpro_generico` | Dependiente | Promedio 5 módulos genéricos (0-300) |
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

- **Spec 1 (base):** `factor(depto_ies)` + `distancia_bogota_km` + controles. Errores HC3 + clusterizados por IES.
- **Spec 2 (ef_ies):** Efectos fijos por institución.
- **Spec 3 (ef_mun):** Efectos fijos por tipo de municipio.

6 variables dependientes × 3 especificaciones = **18 modelos en total**.

---

## Diagnósticos implementados

- Normalidad: Shapiro-Wilk (n < 5.000) / Kolmogorov-Smirnov (n ≥ 5.000)
- Homocedasticidad: Breusch-Pagan
- Multicolinealidad: VIF (umbral > 10)
- Autocorrelación: Durbin-Watson
- Especificación: RESET de Ramsey
- Corrección por pruebas múltiples: Holm y Benjamini-Hochberg

---

## Fuente de datos

ICFES (2023a). *DataICFES: repositorio de microdatos del ICFES.*  
https://www.icfes.gov.co/data-icfes/

---

## Limitaciones (diseño observacional)

Los coeficientes son **asociaciones condicionales**, no efectos causales.
β_IA puede estar sesgado por variables omitidas, confusión temporal con
la pandemia COVID-19 y ausencia de aleatorización (Wooldridge, 2020;
Angrist & Pischke, 2009).
