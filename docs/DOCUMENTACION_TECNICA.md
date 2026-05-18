# Documentación técnica — `colab_pipeline.py`

Pipeline automatizado para la preparación de microdatos de la investigación:

> **Disparidades en el desempeño Saber Pro y su asociación con el período
> de adopción de IA Generativa (2021–2024)**
> Eduardo Andrés Victoria Cadena. Universidad Surcolombiana, 2026.

---

## 1. Objetivo del proyecto

El estudio estima, mediante regresión lineal múltiple por MCO, la asociación
condicional entre el período de adopción masiva de IA generativa
(`periodo_ia = 1` para 2023–2024) y el puntaje en habilidades genéricas de
Saber Pro, controlando por variables socioeconómicas, demográficas,
académicas, institucionales y geográficas. El presente script automatiza
toda la fase de **preparación de datos**:

1. Conectar Google Colab con Google Drive.
2. Cargar los archivos crudos `Examen_Saber_Pro_Genericas_<año>.txt`
   ubicados en `Mi unidad/IA_EDUCACION_SUPERIOR`.
3. Construir las variables operacionalizadas en la Sección 8 del documento.
4. Conservar únicamente las columnas relevantes (Tablas 1 y 2 del
   documento) y descartar las demás.
5. Limpiar los datos (faltantes, formatos, rangos, duplicados).
6. Persistir un dataframe por año (`df_2021` … `df_2024`) y un
   dataframe consolidado `df_consolidado` listo para análisis.

---

## 2. Estructura del repositorio relevante para el pipeline

```
IA-Y-EDUCACION-SUPERIOR/
├── python/
│   └── colab_pipeline.py          ← este script (pipeline completo)
└── docs/
    ├── DOCUMENTACION_TECNICA.md   ← este documento
    └── GUIA_EDUCATIVA.md          ← glosario didáctico línea a línea
```

En Google Drive el usuario debe disponer de:

```
Mi unidad/
└── IA_EDUCACION_SUPERIOR/
    ├── Examen_Saber_Pro_Genericas_2021.txt
    ├── Examen_Saber_Pro_Genericas_2022.txt
    ├── Examen_Saber_Pro_Genericas_2023.txt
    ├── Examen_Saber_Pro_Genericas_2024.txt
    └── procesados/                ← creado automáticamente por el pipeline
        ├── df_2021.csv
        ├── df_2022.csv
        ├── df_2023.csv
        ├── df_2024.csv
        ├── df_consolidado.csv
        └── df_consolidado.parquet  (si pyarrow está instalado)
```

---

## 3. Dependencias

| Paquete        | Versión recomendada | Uso |
|----------------|---------------------|-----|
| `python`       | ≥ 3.10              | Lenguaje base. |
| `pandas`       | ≥ 1.5               | Estructuras de datos (`DataFrame`, `Series`). |
| `numpy`        | ≥ 1.23              | Soporte numérico y `np.nan`. |
| `google.colab` | provisto por Colab  | Montaje de Google Drive. |
| `pyarrow`      | opcional            | Exportación a parquet (más rápida que CSV). |

> En Google Colab, `pandas`, `numpy` y `google.colab` ya están preinstalados.
> Sólo se requiere instalar `pyarrow` si se desea el guardado en parquet.

---

## 4. Estructura del módulo `colab_pipeline.py`

El script se organiza en diez bloques numerados, en orden de ejecución:

| Bloque | Responsabilidad |
|-------:|-----------------|
| 1 | Constantes del proyecto (rutas, años, mapeos de columnas, codificación de departamentos, distancias a Bogotá). |
| 2 | Utilidades generales (`_normalizar_texto`, `_registrar`). |
| 3 | Conexión con Google Drive (`montar_drive`). |
| 4 | Lectura robusta de los `.txt` (`_detectar_separador_y_codificacion`, `leer_archivo_anio`). |
| 5 | Normalización de nombres de columnas (`normalizar_columnas`). |
| 6 | Construcción de las variables de la investigación (14 funciones especializadas + `construir_variables`). |
| 7 | Limpieza (`seleccionar_variables_finales`, `limpiar_dataframe`). |
| 8 | Procesamiento por año y consolidación (`procesar_anio`, `consolidar`, `persistir`). |
| 9 | Orquestador `ejecutar_pipeline`. |
| 10 | Ejecución directa (`if __name__ == "__main__":`). |

### 4.1 Constantes principales

| Constante | Tipo | Descripción |
|---|---|---|
| `RUTA_PROYECTO_DEFECTO` | `str` | `/content/drive/MyDrive/IA_EDUCACION_SUPERIOR`. |
| `PATRON_ARCHIVO` | `str` | `Examen_Saber_Pro_Genericas_{anio}.txt`. |
| `ANIOS`, `ANIOS_PREVIO`, `ANIOS_IA` | `list[int]` | Años analizados y particiones temporales. |
| `SEPARADORES_CANDIDATOS` | `tuple[str]` | Caracteres delimitadores que se prueban automáticamente. |
| `CODIFICACIONES_CANDIDATAS` | `tuple[str]` | Codificaciones probables del archivo. |
| `MAPA_COLUMNAS` | `dict[str, str]` | Renombramiento crudo → operativo. |
| `VARIABLES_FINALES` | `list[str]` | Columnas que sobreviven a la depuración. |
| `MODULOS_GENERICOS` | `list[str]` | Las 5 puntuaciones que conforman el agregado. |
| `DEPARTAMENTOS` | `dict[str, tuple[int, float]]` | Codificación 0–32 + distancia oficial a Bogotá. |
| `ALIAS_DEPARTAMENTOS` | `dict[str, str]` | Sinónimos / variantes para canonización. |

### 4.2 Funciones del módulo (orden de llamada)

```text
ejecutar_pipeline
└── montar_drive
└── procesar_anio
    ├── leer_archivo_anio
    │   └── _detectar_separador_y_codificacion
    ├── normalizar_columnas
    ├── construir_variables
    │   ├── construir_periodo_ia
    │   ├── construir_puntaje_generico
    │   ├── construir_edad
    │   ├── construir_estrato
    │   ├── construir_genero
    │   ├── construir_nivel_educ_padre
    │   ├── construir_estu_trabaja
    │   ├── construir_cabeza_familia
    │   ├── construir_jornada
    │   ├── construir_internet
    │   ├── construir_area_residencia
    │   ├── construir_naturaleza_ies
    │   ├── construir_departamento
    │   └── construir_distancia_bogota
    ├── seleccionar_variables_finales
    └── limpiar_dataframe
└── consolidar
└── persistir
```

---

## 5. Variables conservadas en el dataframe final

| # | Variable | Tipo | Origen / Construcción |
|--:|---|---|---|
| 1 | `id_estudiante` | string | `ESTU_CONSECUTIVO` |
| 2 | `anio` | int | Año del archivo |
| 3–7 | `punt_lectura_critica`, `punt_razona_cuant`, `punt_competen_ciud`, `punt_comuni_escrita`, `punt_ingles` | float | Módulos genéricos ICFES (0–300) |
| 8 | `puntaje_saberpro_generico` | float | Promedio simple de los 5 módulos |
| 9 | `periodo_ia` | 0/1 | 0 si `anio` ∈ {2021,2022}; 1 si {2023,2024} |
| 10 | `estrato` | 1–6 | `FAMI_ESTRATOVIVIENDA` |
| 11 | `genero` | 0/1 | `ESTU_GENERO` (F=0, M=1) |
| 12 | `edad` | float | `anio` – año de `ESTU_FECHANACIMIENTO` |
| 13 | `nivel_educ_padre` | 1–7 | `FAMI_EDUCACIONPADRE` |
| 14 | `estu_trabaja` | 0/1 | `ESTU_HORASSEMANATRABAJA` |
| 15 | `estu_cabeza_familia` | 0/1 | Proxy desde `ESTU_PAGOMATRICULAPADRES` |
| 16 | `jornada` | 0/1 | `ESTU_HORARIO_PRGM` + `ESTU_METODO_PRGM` |
| 17 | `internet` | 0/1 | `FAMI_TIENEINTERNET` |
| 18 | `area_residencia` | 0/1 | `ESTU_AREARESIDE` |
| 19 | `naturaleza_ies` | 0/1 | `INST_ORIGEN` |
| 20 | `departamento` | 0–32 | Canonización de `INST_DEPARTAMENTO_NOMBRE` |
| 21 | `departamento_nombre` | string | Nombre canónico (auditoría) |
| 22 | `distancia_bogota_km` | float | Lookup `DEPARTAMENTOS[nombre]` |

Todas las demás columnas del archivo crudo se descartan en
`seleccionar_variables_finales`.

---

## 6. Reglas de limpieza aplicadas

1. **Conversión numérica defensiva**: cualquier columna que represente
   puntajes, edad o distancia se pasa por `pd.to_numeric` con
   `errors='coerce'`. Las celdas no convertibles quedan `NaN`.
2. **Rango Saber Pro 0–300**: los valores fuera del rango oficial se
   convierten a `NaN` (no se eliminan filas completas por un módulo).
3. **Filtro de filas inválidas**:
   - sin `puntaje_saberpro_generico` (no hay variable dependiente),
   - sin `departamento` válido (no hay anclaje geográfico).
4. **Edad**: se descartan edades < 15 o > 80 años (errores de captura).
5. **Estrato**: sólo se aceptan códigos 1–6; "Sin estrato" → `NaN`.
6. **Duplicados**: se eliminan duplicados exactos por
   (`id_estudiante`, `anio`).
7. **Esquema constante**: si un archivo no trae una columna fuente, se
   crea con `NaN` para que todos los `df_<año>` tengan el mismo conjunto
   de columnas en el mismo orden.

El método `limpiar_dataframe` imprime el número de filas eliminadas
para que el usuario tenga trazabilidad.

---

## 7. Forma de ejecución

### 7.1 Desde Google Colab (recomendado)

```python
# Celda 1 — cargar el script desde Drive
!cp /content/drive/MyDrive/IA_EDUCACION_SUPERIOR/colab_pipeline.py /content/

# Celda 2 — ejecutar
from colab_pipeline import ejecutar_pipeline
dfs_anio, df_consolidado = ejecutar_pipeline()

df_2021 = dfs_anio[2021]
df_2022 = dfs_anio[2022]
df_2023 = dfs_anio[2023]
df_2024 = dfs_anio[2024]
df_consolidado.head()
```

### 7.2 Desde una máquina local

```bash
python python/colab_pipeline.py
```

> Requiere que `RUTA_PROYECTO_DEFECTO` se ajuste a una carpeta local
> que contenga los `.txt`, o que se pase otra ruta a `ejecutar_pipeline`.

### 7.3 Salida esperada en consola

```
[10:00:01] == INICIO DEL PIPELINE ==
[10:00:01] Montando Google Drive en /content/drive ...
[10:00:04] Ruta del proyecto verificada: /content/drive/MyDrive/IA_EDUCACION_SUPERIOR
[10:00:04] -- Procesando año 2021 --
[10:00:05] Leyendo Examen_Saber_Pro_Genericas_2021.txt (sep='¦', enc='latin-1') ...
[10:00:18]   Examen_Saber_Pro_Genericas_2021.txt: 188,432 filas × 72 columnas.
[10:00:25] Limpieza: 188,432 → 182,114 filas (eliminadas 6,318 = 3.4%).
[10:00:25] df_2021 listo: 182,114 filas × 22 columnas.
...
[10:01:48] df_consolidado: 742,991 filas × 22 columnas.
[10:01:50] Guardado: .../procesados/df_consolidado.csv
[10:01:53] == FIN DEL PIPELINE ==
```

(Los volúmenes reales dependen del archivo descargado de DataICFES.)

---

## 8. Trazabilidad con el documento de la investigación

| Documento (sección) | Implementación en el script |
|---|---|
| §8.2 — Fuente de datos: DataICFES | `leer_archivo_anio`, `PATRON_ARCHIVO` |
| §8.3 — Variable dependiente: `puntaje_saberpro_generico` | `construir_puntaje_generico` |
| §8.4 — Variable de interés: `periodo_ia` | `construir_periodo_ia` |
| §8.5 — Controles socioeconómicos | `construir_estrato`, `construir_genero`, `construir_edad`, `construir_nivel_educ_padre`, `construir_estu_trabaja`, `construir_cabeza_familia`, `construir_jornada`, `construir_internet`, `construir_area_residencia`, `construir_naturaleza_ies` |
| §8.5 (i) — Departamento 0–32, Bogotá D.C.=0 | `construir_departamento`, `DEPARTAMENTOS`, `ALIAS_DEPARTAMENTOS` |
| §8.5 (ii) — `distancia_bogota_km` | `construir_distancia_bogota` |
| Tabla 1 — Mapeo de departamentos y distancias | `DEPARTAMENTOS` |
| Tabla 2 — Variables del modelo | `VARIABLES_FINALES` |

---

## 9. Limitaciones del pipeline

- El nombre exacto de los campos del ICFES puede cambiar entre años.
  `MAPA_COLUMNAS` contempla las variantes documentadas en el diccionario
  oficial pero pueden faltar nuevas. Si una columna no aparece, la
  variable correspondiente quedará `NaN` (no aborta el pipeline).
- `estu_cabeza_familia` es **un proxy** construido desde
  `ESTU_PAGOMATRICULAPADRES`, tal como advierte la Tabla 2 del documento.
- `jornada` depende de los campos de horario/metodología del programa.
  Cuando el ICFES no reporta horario, queda `NaN`.
- Las distancias a Bogotá son las publicadas por IGAC/INVIAS y, por
  diseño metodológico (Sección 8.5 del documento), son una sola por
  departamento; no capturan dispersión intra-departamental.

---

## 10. Mantenimiento

Para añadir un año nuevo basta con:

1. Subir `Examen_Saber_Pro_Genericas_<año>.txt` a la carpeta del proyecto.
2. Agregar el año a la constante `ANIOS` y, según corresponda, a
   `ANIOS_PREVIO` o `ANIOS_IA`.
3. Volver a ejecutar `ejecutar_pipeline()`.

Para añadir una variable de control:

1. Mapear el nombre crudo en `MAPA_COLUMNAS`.
2. Implementar una función `construir_<nueva_variable>` siguiendo el
   patrón del resto.
3. Llamarla desde `construir_variables`.
4. Añadir la columna al final de `VARIABLES_FINALES`.
