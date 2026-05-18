# Documentación técnica — `preparar_datos.py`

Pipeline de preparación de microdatos para la investigación:

> **Disparidades en el desempeño Saber Pro y su asociación con el período
> de adopción de IA Generativa (2021–2024)**
> Eduardo Andrés Victoria Cadena. Universidad Surcolombiana, 2026.

---

## 1. Objetivo del proyecto

El estudio estima, mediante regresión lineal múltiple por MCO, la
asociación condicional entre el período de adopción masiva de IA
generativa (`periodo_ia = 1` para 2023–2024) y los puntajes en
competencias genéricas de Saber Pro, controlando por variables
socioeconómicas, demográficas, académicas, institucionales y
geográficas. Este script automatiza la **preparación de los microdatos**
descargados de DataICFES para los años 2021–2024.

---

## 2. Funcionamiento general

El script:

1. Carga los archivos `Examen_Saber_Pro_Genericas_<año>.txt` desde una
   ruta cualquiera del sistema (no requiere Google Colab).
2. Lee **solo las 17 columnas requeridas** del diccionario oficial de
   DataICFES (`usecols`), ignorando el resto del archivo.
3. Construye las 14 variables analíticas que define la metodología
   (Tablas 1, 2 y 3 del documento) y, **en cada paso, elimina la columna
   fuente cuando ya no es necesaria** (incluida `estu_fechanacimiento`,
   que se descarta inmediatamente después de calcular `edad`).
4. Distingue dos conjuntos de variables por finalidad analítica:
   `VARIABLES_DESCRIPTIVO` (Tabla 3, análisis bivariado) y
   `VARIABLES_MODELO` (Tabla 2, regresión MCO). Su unión es lo que
   conserva el dataframe final (22 columnas).
5. Limpia rangos (puntajes 0–300, edades 15–80, estratos 1–6) y filtra
   filas sin variable dependiente o sin departamento.
6. Persiste `df_2021.csv … df_2024.csv` y `df_consolidado.csv` en la
   subcarpeta `procesados/`.

---

## 3. Diferencia entre los dos conjuntos de variables

| Conjunto | Tabla del documento | Finalidad analítica | Contenido |
|---|---|---|---|
| `VARIABLES_DESCRIPTIVO` | Tabla 3 | Análisis bivariado: medias, frecuencias y pruebas (t-test, χ², Mann-Whitney) por cohorte 2021-2022 vs 2023-2024. | `id_estudiante`, `anio`, `periodo_ia`, los 5 puntajes + `puntaje_saberpro_generico`, `estrato`, `genero`, `estu_trabaja`, `internet`, `naturaleza_ies`. |
| `VARIABLES_MODELO` | Tabla 2 | Regresión lineal múltiple por MCO con efectos fijos y errores robustos. Incluye `VARIABLES_DESCRIPTIVO` **+** los controles adicionales del modelo. | Lo anterior **más** `edad`, `nivel_educ_padre`, `estu_cabeza_familia`, `jornada`, `area_residencia`, `departamento`, `departamento_nombre`, `distancia_bogota_km`. |

`VARIABLES_FINALES = VARIABLES_DESCRIPTIVO ∪ VARIABLES_MODELO` (22
columnas). El dataframe final contiene todas las columnas necesarias
para ambos análisis.

---

## 4. Columnas leídas desde DataICFES (17, según el diccionario oficial)

| Campo crudo (lowercase) | Descripción (Diccionario DataICFES) | Variable que produce | Conjunto |
|---|---|---|---|
| `estu_consecutivo` | Id público del estudiante | `id_estudiante` | Ambos |
| `mod_lectura_critica_punt` | Puntaje lectura crítica [0, 300] | `punt_lectura_critica` | Ambos |
| `mod_razona_cuantitat_punt` | Puntaje razonamiento cuantitativo [0, 300] | `punt_razona_cuant` | Ambos |
| `mod_competen_ciudada_punt` | Puntaje competencias ciudadanas [0, 300] | `punt_competen_ciud` | Ambos |
| `mod_comuni_escrita_punt` | Puntaje comunicación escrita [0, 300] | `punt_comuni_escrita` | Ambos |
| `mod_ingles_punt` | Puntaje inglés [0, 300] | `punt_ingles` | Ambos |
| `estu_genero` | Género (F/M) | `genero` | Ambos |
| `estu_fechanacimiento` | Fecha de Nacimiento [DD/MM/AAAA] | `edad` (luego se elimina) | Modelo |
| `fami_estratovivienda` | Estrato 1–6 / Sin estrato | `estrato` | Ambos |
| `fami_educacionpadre` | Nivel educativo del padre (10 niveles) | `nivel_educ_padre` | Modelo |
| `estu_horassemanatrabaja` | Horas semanales trabajadas | `estu_trabaja` | Ambos |
| `estu_pagomatriculapadres` | Padres pagan matrícula (Sí/No) | `estu_cabeza_familia` (proxy) | Modelo |
| `fami_tieneinternet` | Conexión a internet (Sí/No) | `internet` | Ambos |
| `estu_areareside` | Área rural / Cabecera municipal | `area_residencia` | Modelo |
| `estu_metodo_prgm` | PRESENCIAL/SEMI-PRESENCIAL/DISTANCIA/DISTANCIA VIRTUAL | `jornada` (proxy) | Modelo |
| `inst_origen` | Naturaleza de la IES (oficial/no oficial) | `naturaleza_ies` | Ambos |
| `estu_inst_departamento` | Departamento de la IES | `departamento`, `departamento_nombre`, `distancia_bogota_km` | Modelo |

> Notas del diccionario: `estu_areareside` aparece marcada con `*`
> (pendiente por publicación) para 2024; si falta, la variable
> `area_residencia` queda `NaN` para ese año. El campo `estu_horario_prgm`
> no existe en 2021–2024, por lo que `jornada` se aproxima desde
> `estu_metodo_prgm` (1 si DISTANCIA/VIRTUAL, 0 si PRESENCIAL).

---

## 5. Transformaciones y drop incremental

El pipeline mantiene el dataframe lo más liviano posible: **cada función
construye una variable y elimina inmediatamente la columna cruda que la
generó**. La secuencia es:

| Paso | Función | Variable que crea | Columna cruda que elimina |
|----:|---|---|---|
| 1 | `transformar_id_y_modulos` | `id_estudiante`, 5 puntajes | (rename de 6 columnas) |
| 2 | `construir_periodo_ia` | `periodo_ia` | — (deriva de `anio`) |
| 3 | `construir_puntaje_generico` | `puntaje_saberpro_generico` | — |
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
| 14 | `construir_departamento_y_distancia` | `departamento`, `departamento_nombre`, `distancia_bogota_km` | `estu_inst_departamento` |

Al final de la construcción, **ninguna columna cruda permanece** en el
dataframe. `seleccionar_variables_finales` reordena las 22 columnas a la
unión `VARIABLES_FINALES`.

---

## 6. Reglas de limpieza

1. **Rango Saber Pro 0–300**: valores fuera del rango oficial se llevan
   a `NaN` (no se eliminan filas completas por un módulo individual).
2. **Edad 15–80**: edades fuera de ese rango (errores de captura) → `NaN`.
3. **Estrato 1–6**: 'Sin estrato' o cualquier código inválido → `NaN`.
4. **Filas sin `puntaje_saberpro_generico`** → eliminadas (no hay
   variable dependiente que modelar).
5. **Filas sin `departamento`** → eliminadas (no hay anclaje geográfico
   ni `distancia_bogota_km`).
6. **Duplicados** por (`id_estudiante`, `anio`) → se conserva el primero.

Cada paso reporta cuántas filas se eliminan, para trazabilidad.

---

## 7. Estructura del módulo

```text
preparar_datos.py
├── 1. Constantes (ANIOS, COLS_REQUERIDAS, DEPARTAMENTOS,
│                  VARIABLES_DESCRIPTIVO, VARIABLES_MODELO, …)
├── 2. Utilidades (_normalizar_texto, _registrar, _a_numerico)
├── 3. Conexión opcional con Drive (montar_drive_si_aplica)
├── 4. Lectura (_detectar_formato, _leer_columnas_disponibles,
│              leer_archivo_anio)
├── 5. Construcción de variables (14 funciones construir_* +
│                                  construir_todas_las_variables)
├── 6. Limpieza (limpiar, seleccionar_variables_finales)
├── 7. Procesamiento y consolidación (procesar_anio, consolidar,
│                                      persistir)
├── 8. Orquestador (ejecutar_pipeline)
└── 9. CLI (_construir_parser + bloque __main__)
```

---

## 8. Dependencias

| Paquete  | Versión recomendada | Uso |
|----------|---------------------|-----|
| Python   | ≥ 3.10              | Lenguaje base (anotaciones de tipo). |
| `pandas` | ≥ 1.5               | DataFrame, Series, I/O CSV. |
| `numpy`  | ≥ 1.23              | Soporte numérico y `np.nan`. |
| `google.colab` | opcional      | Sólo si se ejecuta dentro de Colab y se desea montar Drive con `montar_drive_si_aplica`. |

---

## 9. Forma de ejecución

### 9.1 Desde la línea de comandos

```bash
python python/preparar_datos.py --ruta /ruta/a/los_txt
```

Argumentos:

| Flag | Tipo | Descripción |
|------|------|---|
| `--ruta` / `-r` | `str` | Carpeta con los `Examen_Saber_Pro_Genericas_<año>.txt`. |
| `--anios` / `-a` | `int*` | Años a procesar (por defecto 2021 2022 2023 2024). |
| `--sin-guardar` | flag | Si se indica, no escribe los CSV en disco. |

### 9.2 Desde otro script o cuaderno

```python
from preparar_datos import ejecutar_pipeline

dfs_anio, df_consolidado = ejecutar_pipeline(
    ruta_proyecto="/ruta/a/los_txt",
)
df_2021, df_2022, df_2023, df_2024 = (dfs_anio[a] for a in (2021, 2022, 2023, 2024))
```

### 9.3 Desde Google Colab (opcional)

```python
from preparar_datos import montar_drive_si_aplica, ejecutar_pipeline
montar_drive_si_aplica()
dfs, df_consolidado = ejecutar_pipeline("/content/drive/MyDrive/IA_EDUCACION_SUPERIOR")
```

---

## 10. Trazabilidad con el documento de investigación

| Documento | Implementación |
|---|---|
| §8.2 Fuente DataICFES | `leer_archivo_anio`, `COLS_REQUERIDAS` |
| §8.3 Variable dependiente | `construir_puntaje_generico` |
| §8.4 Variable de interés `periodo_ia` | `construir_periodo_ia` |
| §8.5 Controles socioeconómicos (Tabla 2) | 10 funciones `construir_*` |
| §8.5 (i) Departamento 0–32 con Bogotá D.C. = 0 | `DEPARTAMENTOS`, `construir_departamento_y_distancia` |
| §8.5 (ii) `distancia_bogota_km` | `construir_departamento_y_distancia` |
| Tabla 1 Mapeo de departamentos y distancias | `DEPARTAMENTOS` |
| Tabla 2 Variables del modelo (multivariado) | `VARIABLES_MODELO` |
| Tabla 3 Análisis bivariado | `VARIABLES_DESCRIPTIVO` |

---

## 11. Limitaciones

- `estu_areareside` no está garantizada en 2024 (marcada con `*` en el
  diccionario); cuando falte, `area_residencia` queda `NaN`.
- `estu_horario_prgm` no existe en 2021–2024; la variable `jornada` se
  aproxima desde `estu_metodo_prgm`.
- `estu_cabeza_familia` es un proxy desde `estu_pagomatriculapadres`,
  tal como advierte la Tabla 2 del documento.
- `distancia_bogota_km` es única por departamento (Tabla 1 del
  documento) y no captura variación intra-departamental.

---

## 12. Mantenimiento

- **Añadir un año**: agregarlo a `ANIOS` y, según corresponda, a
  `ANIOS_PREVIO` o `ANIOS_IA`. Colocar el `.txt` en la carpeta.
- **Añadir una variable de control**: incluir el nombre crudo en
  `COLS_REQUERIDAS`, implementar un `construir_<nueva>` que cree la
  variable y elimine la fuente, llamarla desde
  `construir_todas_las_variables`, y añadirla a `VARIABLES_MODELO`
  y/o `VARIABLES_DESCRIPTIVO`.
