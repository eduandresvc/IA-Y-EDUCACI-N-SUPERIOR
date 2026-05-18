"""
==============================================================================
colab_pipeline.py
==============================================================================
Pipeline de automatización para la investigación:

    "Disparidades en el desempeño Saber Pro y su asociación con el período
     de adopción de IA Generativa (2021-2024)"
    Eduardo Andrés Victoria Cadena — Universidad Surcolombiana, 2026.

Objetivo del script
-------------------
Automatizar, de extremo a extremo y sobre Google Colab, las fases iniciales
de la investigación: conectar Colab con Google Drive, cargar los microdatos
anuales de DataICFES (Saber Pro 2021 a 2024) almacenados como archivos
.txt en la ruta "Mi unidad/IA_EDUCACION_SUPERIOR", construir las variables
operacionalizadas en el documento (periodo_ia, departamento 0-32,
distancia_bogota_km, puntaje_saberpro_generico, etc.), conservar
únicamente las columnas relevantes definidas por la metodología (sección
8 del documento), limpiar exhaustivamente cada dataframe anual
(valores faltantes, formatos, inconsistencias, rangos) y producir tanto
los dataframes individuales por año (df_2021, df_2022, df_2023, df_2024)
como el dataframe consolidado final df_consolidado listo para los
análisis bivariado y multivariado.

Cómo ejecutarlo
---------------
1. Subir la carpeta del proyecto a Google Drive con el nombre
   IA_EDUCACION_SUPERIOR (en "Mi unidad").
2. Colocar dentro de esa carpeta los archivos crudos descargados de
   DataICFES con los nombres exactos:
       Examen_Saber_Pro_Genericas_2021.txt
       Examen_Saber_Pro_Genericas_2022.txt
       Examen_Saber_Pro_Genericas_2023.txt
       Examen_Saber_Pro_Genericas_2024.txt
3. Abrir un cuaderno de Colab, copiar el contenido de este script (o
   cargarlo con %run colab_pipeline.py) y ejecutar la función
   `ejecutar_pipeline()`.
4. Los dataframes individuales y el consolidado quedan disponibles como
   variables Python y se persisten en la subcarpeta `procesados/`.

Estructura del módulo
---------------------
1. Bloque de constantes (variables relevantes, mapas de departamentos,
   distancias a Bogotá, separadores admitidos por DataICFES, etc.).
2. Funciones de E/S: conexión con Drive y lectura robusta de los .txt.
3. Funciones de construcción de variables (periodo_ia, edad,
   departamento 0-32, distancia, puntajes, dummies socioeconómicas).
4. Funciones de limpieza (faltantes, rangos, tipos, duplicados).
5. Orquestador `ejecutar_pipeline()` que devuelve el diccionario de
   df_año y el dataframe consolidado.

Dependencias
------------
- google.colab (sólo si se ejecuta en Colab; se importa de forma
  perezosa para que el módulo siga siendo importable fuera de Colab).
- pandas >= 1.5
- numpy  >= 1.23

Salida persistida
-----------------
- procesados/df_2021.csv ... df_2024.csv
- procesados/df_consolidado.csv
- procesados/df_consolidado.parquet (si pyarrow está disponible)
==============================================================================
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


# =============================================================================
# 1. CONSTANTES DEL PROYECTO
# =============================================================================
# Ruta del proyecto dentro de Google Drive: "Mi unidad" se monta en
# /content/drive/MyDrive cuando `drive.mount('/content/drive')` se ejecuta.
RUTA_PROYECTO_DEFECTO: str = "/content/drive/MyDrive/IA_EDUCACION_SUPERIOR"

# Nombre del archivo crudo por año. {anio} se reemplaza por 2021..2024.
PATRON_ARCHIVO: str = "Examen_Saber_Pro_Genericas_{anio}.txt"

# Años analizados en la investigación: 4 cohortes (2 pre-IA + 2 post-IA).
ANIOS: List[int] = [2021, 2022, 2023, 2024]
ANIOS_PREVIO: List[int] = [2021, 2022]
ANIOS_IA: List[int] = [2023, 2024]

# Separadores comunes en los archivos de DataICFES. Se prueban en orden
# para detectar automáticamente el formato (¦, |, tabulador o coma).
SEPARADORES_CANDIDATOS: Tuple[str, ...] = ("¦", "|", "\t", ";", ",")

# Codificaciones probables: el ICFES típicamente entrega latin-1 o utf-8.
CODIFICACIONES_CANDIDATAS: Tuple[str, ...] = ("utf-8", "latin-1", "cp1252")

# -----------------------------------------------------------------------------
# 1.1  Mapeo de columnas crudas (DataICFES) → nombres operativos del estudio.
# -----------------------------------------------------------------------------
# La nomenclatura DataICFES varía levemente entre años; el diccionario
# contempla las variantes documentadas en el diccionario oficial.
MAPA_COLUMNAS: Dict[str, str] = {
    # Identificadores
    "ESTU_CONSECUTIVO":            "id_estudiante",
    # Módulos genéricos (variables dependientes)
    "MOD_LECTURA_CRITICA_PUNT":    "punt_lectura_critica",
    "MOD_RAZONA_CUANTITAT_PUNT":   "punt_razona_cuant",
    "MOD_RAZONA_CUANTITATIVO_PUNT": "punt_razona_cuant",
    "MOD_COMPETEN_CIUDADA_PUNT":   "punt_competen_ciud",
    "MOD_COMPETEN_CIUDADANA_PUNT": "punt_competen_ciud",
    "MOD_COMUNI_ESCRITA_PUNT":     "punt_comuni_escrita",
    "MOD_INGLES_PUNT":             "punt_ingles",
    # Institución y geografía
    "INST_NOMBRE_INSTITUCION":     "nombre_ies",
    "ESTU_INST_NOMBRE":            "nombre_ies",
    "INST_ORIGEN":                 "naturaleza_ies_raw",
    "INST_CARACTER_ACADEMICO":     "caracter_ies",
    "INST_DEPARTAMENTO_NOMBRE":    "departamento_ies_raw",
    "INST_MUNICIPIO_NOMBRE":       "municipio_ies",
    # Programa académico
    "ESTU_PRGM_ACADEMICO":         "programa_academico",
    "ESTU_NUCLEO_PREGRADO":        "nucleo_pregrado",
    "ESTU_METODO_PRGM":            "metodologia_prgm",
    "ESTU_HORARIO_PRGM":           "horario_prgm",
    # Socioeconómicas y demográficas
    "FAMI_ESTRATOVIVIENDA":        "estrato_raw",
    "ESTU_GENERO":                 "genero_raw",
    "ESTU_FECHANACIMIENTO":        "fecha_nacimiento_raw",
    "FAMI_EDUCACIONPADRE":         "nivel_educ_padre_raw",
    "ESTU_HORASSEMANATRABAJA":     "horas_trabaja_raw",
    "ESTU_PAGOMATRICULAPADRES":    "pago_matricula_raw",
    "FAMI_TIENEINTERNET":          "internet_raw",
    "ESTU_AREARESIDE":             "area_residencia_raw",
    # Año (algunos archivos lo traen como periodo)
    "ESTU_FECHASESION":            "fecha_sesion_raw",
    "PERIODO":                     "periodo_icfes",
}

# -----------------------------------------------------------------------------
# 1.2  Variables FINALES que conserva el dataframe procesado.
# -----------------------------------------------------------------------------
# Estas columnas se derivan de las Tablas 1 y 2 del documento (sección 8).
# Cualquier columna no incluida aquí se descarta en la depuración final.
VARIABLES_FINALES: List[str] = [
    # Identificación + año
    "id_estudiante", "anio",
    # Dependientes
    "punt_lectura_critica", "punt_razona_cuant",
    "punt_competen_ciud", "punt_comuni_escrita", "punt_ingles",
    "puntaje_saberpro_generico",
    # Variable de interés (dummy temporal)
    "periodo_ia",
    # Socioeconómicas/demográficas/académicas
    "estrato", "genero", "edad",
    "nivel_educ_padre", "estu_trabaja",
    "estu_cabeza_familia", "jornada",
    "internet", "area_residencia", "naturaleza_ies",
    # Geográficas
    "departamento", "departamento_nombre", "distancia_bogota_km",
]

# Los cinco módulos genéricos cuyo promedio define el puntaje agregado.
MODULOS_GENERICOS: List[str] = [
    "punt_lectura_critica",
    "punt_razona_cuant",
    "punt_competen_ciud",
    "punt_comuni_escrita",
    "punt_ingles",
]

# -----------------------------------------------------------------------------
# 1.3  Codificación de departamentos (Tabla 1 del documento).
# -----------------------------------------------------------------------------
# 0 = Bogotá D.C. (categoría de referencia). 1..32 = departamentos en orden
# alfabético (Amazonas=1, ..., Vichada=32). Cada entrada contiene el código
# numérico, el nombre canonizado y la distancia oficial a Bogotá (km).
DEPARTAMENTOS: Dict[str, Tuple[int, float]] = {
    "BOGOTA":              (0,    0.0),
    "AMAZONAS":            (1, 1100.0),
    "ANTIOQUIA":           (2,  415.0),
    "ARAUCA":              (3,  670.0),
    "ATLANTICO":           (4, 1000.0),
    "BOLIVAR":             (5, 1060.0),
    "BOYACA":              (6,  140.0),
    "CALDAS":              (7,  300.0),
    "CAQUETA":             (8,  540.0),
    "CASANARE":            (9,  360.0),
    "CAUCA":              (10,  595.0),
    "CESAR":              (11,  870.0),
    "CHOCO":              (12,  715.0),
    "CORDOBA":            (13,  770.0),
    "CUNDINAMARCA":       (14,   40.0),
    "GUAINIA":            (15, 1080.0),
    "GUAVIARE":           (16,  390.0),
    "HUILA":              (17,  310.0),
    "LA GUAJIRA":         (18, 1050.0),
    "MAGDALENA":          (19,  945.0),
    "META":               (20,  115.0),
    "NARINO":             (21,  785.0),
    "NORTE DE SANTANDER": (22,  565.0),
    "PUTUMAYO":           (23,  670.0),
    "QUINDIO":            (24,  280.0),
    "RISARALDA":          (25,  340.0),
    "SAN ANDRES":         (26,  720.0),
    "SANTANDER":          (27,  395.0),
    "SUCRE":              (28,  870.0),
    "TOLIMA":             (29,  210.0),
    "VALLE":              (30,  460.0),
    "VAUPES":             (31,  870.0),
    "VICHADA":            (32,  760.0),
}

# Aliases adicionales que aparecen en DataICFES (acentos, abreviaciones).
ALIAS_DEPARTAMENTOS: Dict[str, str] = {
    "BOGOTA D.C.":               "BOGOTA",
    "BOGOTA D C":                "BOGOTA",
    "BOGOTA DC":                 "BOGOTA",
    "BOGOTÁ":                    "BOGOTA",
    "BOGOTÁ D.C.":               "BOGOTA",
    "BOGOTÁ, D.C.":              "BOGOTA",
    "SANTAFE DE BOGOTA":         "BOGOTA",
    "VALLE DEL CAUCA":           "VALLE",
    "SAN ANDRES Y PROVIDENCIA":  "SAN ANDRES",
    "SAN ANDRES, PROVIDENCIA Y SANTA CATALINA": "SAN ANDRES",
    "ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA": "SAN ANDRES",
    "GUAJIRA":                   "LA GUAJIRA",
    "NORTE SANTANDER":           "NORTE DE SANTANDER",
    "N. DE SANTANDER":           "NORTE DE SANTANDER",
}


# =============================================================================
# 2. UTILIDADES GENERALES
# =============================================================================
def _normalizar_texto(valor: object) -> str:
    """Mayúsculas, sin tildes ni espacios duplicados; '' si no hay dato."""
    # Convertir nulos o NaN a cadena vacía para evitar fallos del normalizador.
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    texto = str(valor).strip().upper()
    # NFKD descompone acentos para poder filtrarlos por categoría unicode.
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    # Comprimir espacios múltiples a uno solo.
    texto = re.sub(r"\s+", " ", texto)
    return texto


def _registrar(mensaje: str) -> None:
    """Logger minimalista con timestamp para trazabilidad en Colab."""
    ahora = datetime.now().strftime("%H:%M:%S")
    print(f"[{ahora}] {mensaje}")


# =============================================================================
# 3. CONEXIÓN CON GOOGLE DRIVE
# =============================================================================
def montar_drive(ruta_proyecto: str = RUTA_PROYECTO_DEFECTO) -> str:
    """
    Monta Google Drive en `/content/drive` y verifica que exista la carpeta
    del proyecto. Devuelve la ruta del proyecto.

    Fuera de Colab (entornos locales o de pruebas) sólo verifica que la
    ruta exista, sin intentar montar nada.
    """
    # Detección de entorno: 'google.colab' sólo existe en Colab.
    if "google.colab" in sys.modules or os.path.exists("/content"):
        # Importación perezosa para que el módulo siga siendo importable
        # en una máquina local que no tiene google.colab instalado.
        from google.colab import drive  # type: ignore
        if not os.path.ismount("/content/drive"):
            _registrar("Montando Google Drive en /content/drive ...")
            drive.mount("/content/drive", force_remount=False)
        else:
            _registrar("Google Drive ya estaba montado.")
    else:
        _registrar("Entorno no-Colab detectado; se omite el montaje de Drive.")

    if not os.path.isdir(ruta_proyecto):
        raise FileNotFoundError(
            f"No se encontró la carpeta del proyecto: {ruta_proyecto}\n"
            f"Cree la carpeta 'IA_EDUCACION_SUPERIOR' en 'Mi unidad' y "
            f"coloque allí los archivos {PATRON_ARCHIVO.format(anio='YYYY')}."
        )
    _registrar(f"Ruta del proyecto verificada: {ruta_proyecto}")
    return ruta_proyecto


# =============================================================================
# 4. LECTURA ROBUSTA DE LOS .TXT DE DATAICFES
# =============================================================================
def _detectar_separador_y_codificacion(ruta: str) -> Tuple[str, str]:
    """Prueba combinaciones de codificación y separador y devuelve la primera
    que produzca un dataframe con más de una columna y al menos una fila."""
    for codificacion in CODIFICACIONES_CANDIDATAS:
        for separador in SEPARADORES_CANDIDATOS:
            try:
                muestra = pd.read_csv(
                    ruta,
                    sep=separador,
                    encoding=codificacion,
                    nrows=5,
                    on_bad_lines="skip",
                    engine="python",
                )
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
            if muestra.shape[1] > 1 and muestra.shape[0] >= 1:
                return separador, codificacion
    raise ValueError(
        f"No se pudo detectar separador/codificación para: {ruta}. "
        "Verifique manualmente el archivo."
    )


def leer_archivo_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:
    """Lee el .txt anual de DataICFES y le agrega la columna `anio`."""
    nombre = PATRON_ARCHIVO.format(anio=anio)
    ruta = os.path.join(ruta_proyecto, nombre)
    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"Archivo no encontrado: {ruta}.\n"
            "Verifique que el nombre coincida exactamente con "
            f"'{PATRON_ARCHIVO.format(anio='YYYY')}'."
        )
    sep, enc = _detectar_separador_y_codificacion(ruta)
    _registrar(f"Leyendo {nombre} (sep='{sep}', enc='{enc}') ...")
    df = pd.read_csv(
        ruta,
        sep=sep,
        encoding=enc,
        on_bad_lines="skip",
        engine="python",
    )
    df["anio"] = anio
    _registrar(f"  {nombre}: {len(df):,} filas × {df.shape[1]} columnas.")
    return df


# =============================================================================
# 5. NORMALIZACIÓN DE NOMBRES DE COLUMNAS
# =============================================================================
def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra las columnas crudas según MAPA_COLUMNAS (case-insensitive)."""
    # Diccionario auxiliar con las claves en mayúsculas para emparejar
    # independientemente de cómo vengan rotuladas en el archivo original.
    mapa_mayus = {k.upper(): v for k, v in MAPA_COLUMNAS.items()}
    nuevas = {}
    for col in df.columns:
        clave = col.upper().strip()
        if clave in mapa_mayus:
            nuevas[col] = mapa_mayus[clave]
    df = df.rename(columns=nuevas)
    return df


# =============================================================================
# 6. CONSTRUCCIÓN DE LAS VARIABLES DE LA INVESTIGACIÓN
# =============================================================================
def _a_numerico(serie: pd.Series) -> pd.Series:
    """Convierte una serie a numérico tolerando comas decimales y texto."""
    if serie.dtype.kind in "iuf":
        return serie
    return pd.to_numeric(
        serie.astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def construir_periodo_ia(df: pd.DataFrame) -> pd.DataFrame:
    """periodo_ia = 0 si anio ∈ {2021, 2022}; 1 si anio ∈ {2023, 2024}."""
    df["periodo_ia"] = df["anio"].apply(
        lambda a: 0 if a in ANIOS_PREVIO else (1 if a in ANIOS_IA else np.nan)
    ).astype("Int64")
    return df


def construir_puntaje_generico(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte los 5 módulos a numérico y calcula el promedio simple."""
    disponibles: List[str] = []
    for modulo in MODULOS_GENERICOS:
        if modulo in df.columns:
            df[modulo] = _a_numerico(df[modulo])
            disponibles.append(modulo)
    # Promedio simple sobre los módulos disponibles fila a fila.
    df["puntaje_saberpro_generico"] = (
        df[disponibles].mean(axis=1, skipna=True) if disponibles else np.nan
    )
    return df


def construir_edad(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la edad a partir de la fecha de nacimiento y el año de prueba."""
    if "fecha_nacimiento_raw" not in df.columns:
        df["edad"] = np.nan
        return df
    # to_datetime con errors='coerce' deja NaT donde no se pueda parsear.
    fecha = pd.to_datetime(
        df["fecha_nacimiento_raw"], errors="coerce", dayfirst=True,
    )
    # Edad = año_de_prueba - año_nacimiento, asumiendo aplicación en otoño.
    df["edad"] = (df["anio"] - fecha.dt.year).astype("Float64")
    # Saneamiento: edades fuera de [15, 80] se marcan como NaN.
    df.loc[(df["edad"] < 15) | (df["edad"] > 80), "edad"] = np.nan
    return df


def construir_estrato(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte 'Estrato 1'..'Estrato 6' / 'Sin estrato' a 1..6 / NaN."""
    if "estrato_raw" not in df.columns:
        df["estrato"] = np.nan
        return df
    # Extraer el primer dígito presente en la cadena; 'Sin estrato' → NaN.
    df["estrato"] = (
        df["estrato_raw"].astype(str).str.extract(r"(\d)", expand=False)
        .astype("Float64")
    )
    df.loc[(df["estrato"] < 1) | (df["estrato"] > 6), "estrato"] = np.nan
    return df


def construir_genero(df: pd.DataFrame) -> pd.DataFrame:
    """genero: 0 = Femenino, 1 = Masculino (otros valores → NaN)."""
    if "genero_raw" not in df.columns:
        df["genero"] = np.nan
        return df
    serie = df["genero_raw"].apply(_normalizar_texto)
    df["genero"] = serie.map({"F": 0, "FEMENINO": 0,
                              "M": 1, "MASCULINO": 1})
    df["genero"] = df["genero"].astype("Int64")
    return df


def construir_nivel_educ_padre(df: pd.DataFrame) -> pd.DataFrame:
    """Codifica el nivel educativo del padre en una escala ordinal 1..7."""
    if "nivel_educ_padre_raw" not in df.columns:
        df["nivel_educ_padre"] = np.nan
        return df
    serie = df["nivel_educ_padre_raw"].apply(_normalizar_texto)
    mapa = {
        "NINGUNO":                          1,
        "NO SABE":                          np.nan,
        "NO APLICA":                        np.nan,
        "PRIMARIA INCOMPLETA":              2,
        "PRIMARIA COMPLETA":                3,
        "SECUNDARIA (BACHILLERATO) INCOMPLETA": 4,
        "SECUNDARIA INCOMPLETA":            4,
        "SECUNDARIA (BACHILLERATO) COMPLETA":   5,
        "SECUNDARIA COMPLETA":              5,
        "BACHILLERATO COMPLETO":            5,
        "TECNICA O TECNOLOGICA INCOMPLETA": 5,
        "TECNICA O TECNOLOGICA COMPLETA":   6,
        "EDUCACION PROFESIONAL INCOMPLETA": 6,
        "EDUCACION PROFESIONAL COMPLETA":   7,
        "POSTGRADO":                        7,
    }
    df["nivel_educ_padre"] = serie.map(mapa).astype("Float64")
    return df


def construir_estu_trabaja(df: pd.DataFrame) -> pd.DataFrame:
    """Trabaja = 1 si reporta cualquier hora positiva semanal, 0 si no."""
    if "horas_trabaja_raw" not in df.columns:
        df["estu_trabaja"] = np.nan
        return df
    serie = df["horas_trabaja_raw"].apply(_normalizar_texto)
    df["estu_trabaja"] = serie.map({
        "0":                          0,
        "NO":                         0,
        "0 HORAS":                    0,
        "NO TRABAJA":                 0,
        "MENOS DE 10 HORAS":          1,
        "ENTRE 11 Y 20 HORAS":        1,
        "ENTRE 21 Y 30 HORAS":        1,
        "MAS DE 30 HORAS":            1,
        "MAS DE 31 HORAS":            1,
        "MAS DE 20 HORAS":            1,
        "MAS DE 30 HORAS Y MENOS DE TIEMPO COMPLETO": 1,
        "TIEMPO COMPLETO":            1,
    }).astype("Int64")
    return df


def construir_cabeza_familia(df: pd.DataFrame) -> pd.DataFrame:
    """Proxy: si los padres NO pagan la matrícula, se considera cabeza fam."""
    if "pago_matricula_raw" not in df.columns:
        df["estu_cabeza_familia"] = np.nan
        return df
    serie = df["pago_matricula_raw"].apply(_normalizar_texto)
    df["estu_cabeza_familia"] = serie.map({
        "SI":  0,   # los padres pagan ⇒ no es cabeza de familia
        "NO":  1,   # no pagan ⇒ asume autosostenimiento
    }).astype("Int64")
    return df


def construir_jornada(df: pd.DataFrame) -> pd.DataFrame:
    """jornada = 1 si nocturna/distancia/virtual, 0 si diurna/presencial."""
    candidatas = [c for c in ("horario_prgm", "metodologia_prgm") if c in df.columns]
    if not candidatas:
        df["jornada"] = np.nan
        return df
    texto = df[candidatas].astype(str).agg(" ".join, axis=1).apply(_normalizar_texto)
    df["jornada"] = np.where(
        texto.str.contains("NOCTURN|DISTANCIA|VIRTUAL", regex=True), 1,
        np.where(texto.str.contains("DIURN|PRESENCIAL|MIXTA"), 0, np.nan),
    )
    df["jornada"] = pd.array(df["jornada"], dtype="Float64").astype("Int64")
    return df


def construir_internet(df: pd.DataFrame) -> pd.DataFrame:
    """internet = 1 si el hogar tiene conexión, 0 si no."""
    if "internet_raw" not in df.columns:
        df["internet"] = np.nan
        return df
    serie = df["internet_raw"].apply(_normalizar_texto)
    df["internet"] = serie.map({"SI": 1, "NO": 0}).astype("Int64")
    return df


def construir_area_residencia(df: pd.DataFrame) -> pd.DataFrame:
    """area_residencia = 1 urbana, 0 rural."""
    if "area_residencia_raw" not in df.columns:
        df["area_residencia"] = np.nan
        return df
    serie = df["area_residencia_raw"].apply(_normalizar_texto)
    df["area_residencia"] = serie.map({
        "URBANO": 1, "URBANA": 1, "CABECERA MUNICIPAL": 1,
        "RURAL":  0, "CENTRO POBLADO": 0, "DISPERSO": 0,
    }).astype("Int64")
    return df


def construir_naturaleza_ies(df: pd.DataFrame) -> pd.DataFrame:
    """naturaleza_ies = 1 privada, 0 pública (oficial)."""
    if "naturaleza_ies_raw" not in df.columns:
        df["naturaleza_ies"] = np.nan
        return df
    serie = df["naturaleza_ies_raw"].apply(_normalizar_texto)
    df["naturaleza_ies"] = np.where(
        serie.str.contains("PRIVAD|NO OFICIAL", regex=True), 1,
        np.where(serie.str.contains("OFICIAL|PUBLIC"), 0, np.nan),
    )
    df["naturaleza_ies"] = pd.array(df["naturaleza_ies"], dtype="Float64").astype("Int64")
    return df


def _canonizar_departamento(valor: object) -> Optional[str]:
    """Devuelve el nombre canónico del departamento (clave de DEPARTAMENTOS)."""
    texto = _normalizar_texto(valor)
    if not texto:
        return None
    # 1) Alias directos (variantes con tildes o nombres oficiales largos).
    if texto in ALIAS_DEPARTAMENTOS:
        return ALIAS_DEPARTAMENTOS[texto]
    # 2) Coincidencia exacta con la clave canónica.
    if texto in DEPARTAMENTOS:
        return texto
    # 3) Coincidencia por prefijo (p. ej. 'BOGOTA DC, ...').
    for canon in DEPARTAMENTOS:
        if texto.startswith(canon) or canon in texto:
            return canon
    return None


def construir_departamento(df: pd.DataFrame) -> pd.DataFrame:
    """Crea 'departamento' (código 0-32) y 'departamento_nombre'."""
    if "departamento_ies_raw" not in df.columns:
        df["departamento"] = np.nan
        df["departamento_nombre"] = np.nan
        return df
    canonico = df["departamento_ies_raw"].apply(_canonizar_departamento)
    df["departamento_nombre"] = canonico
    df["departamento"] = canonico.map(
        {nombre: codigo for nombre, (codigo, _) in DEPARTAMENTOS.items()}
    ).astype("Int64")
    return df


def construir_distancia_bogota(df: pd.DataFrame) -> pd.DataFrame:
    """Asigna distancia_bogota_km a partir del departamento canónico."""
    df["distancia_bogota_km"] = df["departamento_nombre"].map(
        {nombre: dist for nombre, (_, dist) in DEPARTAMENTOS.items()}
    ).astype("Float64")
    return df


def construir_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta secuencialmente todas las funciones de construcción."""
    # Cada paso es idempotente: si una columna fuente falta, deja NaN.
    df = construir_periodo_ia(df)
    df = construir_puntaje_generico(df)
    df = construir_edad(df)
    df = construir_estrato(df)
    df = construir_genero(df)
    df = construir_nivel_educ_padre(df)
    df = construir_estu_trabaja(df)
    df = construir_cabeza_familia(df)
    df = construir_jornada(df)
    df = construir_internet(df)
    df = construir_area_residencia(df)
    df = construir_naturaleza_ies(df)
    df = construir_departamento(df)
    df = construir_distancia_bogota(df)
    return df


# =============================================================================
# 7. LIMPIEZA DE DATOS
# =============================================================================
def seleccionar_variables_finales(df: pd.DataFrame) -> pd.DataFrame:
    """Conserva sólo las columnas listadas en VARIABLES_FINALES."""
    # Si alguna no existió (por ejemplo, archivo sin internet_raw), se crea
    # como NaN para mantener el esquema constante entre años.
    for col in VARIABLES_FINALES:
        if col not in df.columns:
            df[col] = np.nan
    return df[VARIABLES_FINALES].copy()


def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica saneamiento integral: tipos, rangos, duplicados, faltantes."""
    n_inicial = len(df)
    # 1) Tipos numéricos definitivos donde corresponda.
    for col in MODULOS_GENERICOS + ["puntaje_saberpro_generico",
                                    "edad", "distancia_bogota_km"]:
        if col in df.columns:
            df[col] = _a_numerico(df[col])

    # 2) Rango de puntajes: la escala oficial Saber Pro va de 0 a 300.
    for col in MODULOS_GENERICOS + ["puntaje_saberpro_generico"]:
        if col in df.columns:
            fuera = ~df[col].between(0, 300)
            df.loc[fuera & df[col].notna(), col] = np.nan

    # 3) Filas sin puntaje agregado (variable dependiente) → se eliminan,
    #    porque no aportan información al análisis.
    df = df[df["puntaje_saberpro_generico"].notna()].copy()

    # 4) Filas sin departamento → se eliminan; sin geografía no hay anclaje
    #    institucional ni distancia a Bogotá.
    df = df[df["departamento"].notna()].copy()

    # 5) Duplicados exactos por id_estudiante + año (registros repetidos por
    #    error de carga). Se conserva el primero.
    if "id_estudiante" in df.columns:
        df = df.drop_duplicates(subset=["id_estudiante", "anio"], keep="first")

    # 6) Reindexar para tener un índice continuo después del filtrado.
    df = df.reset_index(drop=True)

    # 7) Reporte de limpieza para auditoría.
    n_final = len(df)
    _registrar(
        f"Limpieza: {n_inicial:,} → {n_final:,} filas "
        f"(eliminadas {n_inicial - n_final:,} = "
        f"{(n_inicial - n_final) / max(n_inicial, 1):.1%})."
    )
    return df


# =============================================================================
# 8. PROCESAMIENTO POR AÑO Y CONSOLIDACIÓN
# =============================================================================
def procesar_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:
    """Pipeline completo para un único año: leer → normalizar → construir →
    seleccionar → limpiar. Devuelve df_<anio> listo para análisis."""
    crudo = leer_archivo_anio(ruta_proyecto, anio)
    crudo = normalizar_columnas(crudo)
    construido = construir_variables(crudo)
    seleccionado = seleccionar_variables_finales(construido)
    limpio = limpiar_dataframe(seleccionado)
    _registrar(f"df_{anio} listo: {len(limpio):,} filas × {limpio.shape[1]} columnas.")
    return limpio


def consolidar(dfs: Dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Apila los dataframes anuales en uno solo y reordena las columnas."""
    df = pd.concat(dfs.values(), axis=0, ignore_index=True)
    # Volver a aplicar el orden canónico de columnas, por si concat lo altera.
    df = df[VARIABLES_FINALES].copy()
    _registrar(f"df_consolidado: {len(df):,} filas × {df.shape[1]} columnas.")
    return df


def persistir(ruta_proyecto: str,
              dfs: Dict[int, pd.DataFrame],
              df_consolidado: pd.DataFrame) -> str:
    """Guarda los df anuales y el consolidado en `procesados/`."""
    salida = os.path.join(ruta_proyecto, "procesados")
    os.makedirs(salida, exist_ok=True)
    for anio, df in dfs.items():
        ruta_csv = os.path.join(salida, f"df_{anio}.csv")
        df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
        _registrar(f"Guardado: {ruta_csv}")
    ruta_csv_cons = os.path.join(salida, "df_consolidado.csv")
    df_consolidado.to_csv(ruta_csv_cons, index=False, encoding="utf-8-sig")
    _registrar(f"Guardado: {ruta_csv_cons}")
    # Intento de guardar también en parquet (más rápido y tipado).
    try:
        ruta_parquet = os.path.join(salida, "df_consolidado.parquet")
        df_consolidado.to_parquet(ruta_parquet, index=False)
        _registrar(f"Guardado: {ruta_parquet}")
    except Exception as exc:  # noqa: BLE001
        _registrar(f"(Parquet omitido: {exc})")
    return salida


# =============================================================================
# 9. ORQUESTADOR
# =============================================================================
def ejecutar_pipeline(
    ruta_proyecto: str = RUTA_PROYECTO_DEFECTO,
    anios: Iterable[int] = ANIOS,
    persistir_disco: bool = True,
) -> Tuple[Dict[int, pd.DataFrame], pd.DataFrame]:
    """
    Punto de entrada principal. Ejecuta el pipeline completo y devuelve:
        - diccionario {anio: df_anio} con los df individuales,
        - df_consolidado con los 4 años apilados.
    """
    _registrar("== INICIO DEL PIPELINE ==")
    ruta = montar_drive(ruta_proyecto)
    dfs: Dict[int, pd.DataFrame] = {}
    for anio in anios:
        _registrar(f"-- Procesando año {anio} --")
        dfs[anio] = procesar_anio(ruta, anio)
    df_consolidado = consolidar(dfs)
    if persistir_disco:
        persistir(ruta, dfs, df_consolidado)
    _registrar("== FIN DEL PIPELINE ==")
    return dfs, df_consolidado


# =============================================================================
# 10. EJECUCIÓN DIRECTA (python colab_pipeline.py)
# =============================================================================
if __name__ == "__main__":
    # Permite ejecutar el módulo desde la línea de comandos. En Colab se
    # recomienda llamar `ejecutar_pipeline()` directamente desde una celda.
    dfs_anio, df_total = ejecutar_pipeline()
    # Acceso rápido por nombre solicitado en el documento.
    df_2021 = dfs_anio.get(2021)
    df_2022 = dfs_anio.get(2022)
    df_2023 = dfs_anio.get(2023)
    df_2024 = dfs_anio.get(2024)
    df_consolidado = df_total
    print("\nResumen final:")
    print(df_consolidado.describe(include="all").T.head(20))
