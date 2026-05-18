"""
==============================================================================
preparar_datos.py
==============================================================================
Pipeline de preparación de microdatos para la investigación:

    "Disparidades en el desempeño Saber Pro y su asociación con el período
     de adopción de IA Generativa (2021-2024)"
    Eduardo Andrés Victoria Cadena — Universidad Surcolombiana, 2026.

Diferencia entre objetivos
--------------------------
La investigación define dos conjuntos complementarios de variables:

  • Tabla 2 — Variables del modelo de regresión (análisis multivariado MCO):
        periodo_ia, departamento, distancia_bogota_km, estrato, genero,
        edad, nivel_educ_padre, estu_trabaja, estu_cabeza_familia, jornada,
        internet, area_residencia, naturaleza_ies, puntaje_saberpro_generico
        y los cinco módulos genéricos.

  • Tabla 3 — Variables del análisis bivariado / descriptivo:
        subconjunto de la anterior centrado en cohortes 2021–2022 vs
        2023–2024: los seis puntajes, estrato (media), genero (% mujeres),
        estu_trabaja, internet (en el hogar) y naturaleza_ies (% pública).

Este script construye el dataframe que contiene **todas** las variables
necesarias para los dos análisis y deja marcadas, en `VARIABLES_DESCRIPTIVO`
y `VARIABLES_MODELO`, las columnas que cada uno utiliza.

Cómo se usa
-----------
Es un script genérico de Python (no depende de Google Colab). Puede:

    1) Ejecutarse desde la línea de comandos:
           python preparar_datos.py --ruta /ruta/carpeta_con_los_txt

    2) Importarse desde otro programa o cuaderno:
           from preparar_datos import ejecutar_pipeline
           dfs, df_consolidado = ejecutar_pipeline("/ruta/carpeta")

    3) Ejecutarse opcionalmente en Google Colab llamando primero al
       helper `montar_drive_si_aplica()` antes del pipeline.

Archivos crudos esperados (descargados de DataICFES):
    Examen_Saber_Pro_Genericas_2021.txt
    Examen_Saber_Pro_Genericas_2022.txt
    Examen_Saber_Pro_Genericas_2023.txt
    Examen_Saber_Pro_Genericas_2024.txt

Salida
------
    procesados/df_2021.csv ... df_2024.csv      (dataframes por año)
    procesados/df_consolidado.csv               (los cuatro años apilados)
==============================================================================
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


# =============================================================================
# 1. CONSTANTES
# =============================================================================
PATRON_ARCHIVO: str = "Examen_Saber_Pro_Genericas_{anio}.txt"

# Ruta por defecto cuando se ejecuta en Google Colab: "Mi unidad" se
# monta en /content/drive/MyDrive cuando se invoca `drive.mount(...)`.
RUTA_DEFECTO: str = "/content/drive/MyDrive/IA_EDUCACION_SUPERIOR"

ANIOS: List[int] = [2021, 2022, 2023, 2024]
ANIOS_PREVIO: List[int] = [2021, 2022]   # periodo_ia = 0
ANIOS_IA: List[int] = [2023, 2024]       # periodo_ia = 1

SEPARADORES_CANDIDATOS: Tuple[str, ...] = ("¦", "|", "\t", ";", ",")
CODIFICACIONES_CANDIDATAS: Tuple[str, ...] = ("utf-8", "latin-1", "cp1252")

# Paquetes que el módulo necesita además de los preinstalados en Colab.
PAQUETES_REQUERIDOS: Tuple[str, ...] = ("pandas", "numpy")

# -----------------------------------------------------------------------------
# 1.1  Columnas REQUERIDAS desde DataICFES (período 2021-2024).
#      Nombres exactamente como aparecen en el Diccionario oficial.
# -----------------------------------------------------------------------------
# Fuente: Diccionario "Examen Saber Pro" — DataIcfes, sección 2 (2021-2024).
# Sólo se cargan estas columnas; el resto se descarta en lectura.
COLS_REQUERIDAS: List[str] = [
    # — Identificación —
    "estu_consecutivo",
    # — Módulos genéricos (variables dependientes) —
    "mod_lectura_critica_punt",
    "mod_razona_cuantitat_punt",
    "mod_competen_ciudada_punt",
    "mod_comuni_escrita_punt",
    "mod_ingles_punt",
    # — Demográficas —
    "estu_genero",
    "estu_fechanacimiento",
    # — Socioeconómicas y familiares —
    "fami_estratovivienda",
    "fami_educacionpadre",
    "estu_horassemanatrabaja",
    "estu_pagomatriculapadres",
    "fami_tieneinternet",
    "estu_areareside",
    # — Académicas / institucionales —
    "estu_metodo_prgm",
    "inst_origen",
    "inst_cod_institucion",     # identificador único de IES (EF en regresión)
    # — Geografía institucional —
    "estu_inst_departamento",
    "estu_inst_municipio",      # municipio de la IES (EF tipo_municipio)
]

# -----------------------------------------------------------------------------
# 1.2  Codificación de departamentos (Tabla 1 del documento).
#      0 = Bogotá D.C. (categoría de referencia); 1..32 = orden alfabético.
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 1.2.bis  Capitales departamentales (clasificación 'tipo_municipio').
#          Sirven para identificar si el municipio de la IES es la capital
#          de su departamento (Tabla 1 del documento).
# -----------------------------------------------------------------------------
CAPITALES: Dict[str, str] = {
    "BOGOTA":             "BOGOTA D.C.",
    "AMAZONAS":           "LETICIA",
    "ANTIOQUIA":          "MEDELLIN",
    "ARAUCA":             "ARAUCA",
    "ATLANTICO":          "BARRANQUILLA",
    "BOLIVAR":            "CARTAGENA",
    "BOYACA":             "TUNJA",
    "CALDAS":             "MANIZALES",
    "CAQUETA":            "FLORENCIA",
    "CASANARE":           "YOPAL",
    "CAUCA":              "POPAYAN",
    "CESAR":              "VALLEDUPAR",
    "CHOCO":              "QUIBDO",
    "CORDOBA":            "MONTERIA",
    "CUNDINAMARCA":       "BOGOTA D.C.",
    "GUAINIA":            "INIRIDA",
    "GUAVIARE":           "SAN JOSE DEL GUAVIARE",
    "HUILA":              "NEIVA",
    "LA GUAJIRA":         "RIOHACHA",
    "MAGDALENA":          "SANTA MARTA",
    "META":               "VILLAVICENCIO",
    "NARINO":             "PASTO",
    "NORTE DE SANTANDER": "CUCUTA",
    "PUTUMAYO":           "MOCOA",
    "QUINDIO":            "ARMENIA",
    "RISARALDA":          "PEREIRA",
    "SAN ANDRES":         "SAN ANDRES",
    "SANTANDER":          "BUCARAMANGA",
    "SUCRE":              "SINCELEJO",
    "TOLIMA":             "IBAGUE",
    "VALLE":              "CALI",
    "VAUPES":             "MITU",
    "VICHADA":            "PUERTO CARRENO",
}

# Variantes/aliases que aparecen en DataICFES (con tildes o nombres largos).
ALIAS_DEPARTAMENTOS: Dict[str, str] = {
    "BOGOTA D.C.":               "BOGOTA",
    "BOGOTA D C":                "BOGOTA",
    "BOGOTA DC":                 "BOGOTA",
    "SANTAFE DE BOGOTA":         "BOGOTA",
    "VALLE DEL CAUCA":           "VALLE",
    "SAN ANDRES Y PROVIDENCIA":  "SAN ANDRES",
    "SAN ANDRES, PROVIDENCIA Y SANTA CATALINA": "SAN ANDRES",
    "ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA": "SAN ANDRES",
    "GUAJIRA":                   "LA GUAJIRA",
    "NORTE SANTANDER":           "NORTE DE SANTANDER",
    "N. DE SANTANDER":           "NORTE DE SANTANDER",
}

# -----------------------------------------------------------------------------
# 1.3  Conjuntos de variables por finalidad analítica.
# -----------------------------------------------------------------------------
# Tabla 3 del documento: análisis bivariado / descriptivo.
VARIABLES_DESCRIPTIVO: List[str] = [
    "id_estudiante", "anio", "periodo_ia",
    # Puntajes (continuos)
    "punt_lectura_critica", "punt_razona_cuant",
    "punt_competen_ciud", "punt_comuni_escrita", "punt_ingles",
    "puntaje_saberpro_generico",
    # Variables comparadas entre cohortes
    "estrato", "genero", "estu_trabaja", "internet", "naturaleza_ies",
]

# Tabla 2 del documento: variables del modelo MCO multivariado.
VARIABLES_MODELO: List[str] = [
    "id_estudiante", "anio", "periodo_ia",
    # Dependientes
    "punt_lectura_critica", "punt_razona_cuant",
    "punt_competen_ciud", "punt_comuni_escrita", "punt_ingles",
    "puntaje_saberpro_generico",
    # Controles socioeconómicos / demográficos / académicos
    "estrato", "genero", "edad", "nivel_educ_padre",
    "estu_trabaja", "estu_cabeza_familia", "jornada",
    "internet", "area_residencia", "naturaleza_ies",
    # Geográficas
    "departamento", "departamento_nombre", "distancia_bogota_km",
    # Identificadores auxiliares para efectos fijos (§8.9 del documento)
    "cod_ies",            # EF por institución
    "municipio_ies",      # EF por municipio
    "tipo_municipio",     # EF por tipo de municipio (0=Bogotá, 1=capital, 2=resto)
]

# Unión ordenada que conserva el dataframe final.
VARIABLES_FINALES: List[str] = (
    VARIABLES_DESCRIPTIVO
    + [c for c in VARIABLES_MODELO if c not in VARIABLES_DESCRIPTIVO]
)

MODULOS_GENERICOS: List[str] = [
    "punt_lectura_critica",
    "punt_razona_cuant",
    "punt_competen_ciud",
    "punt_comuni_escrita",
    "punt_ingles",
]


# =============================================================================
# 2. UTILIDADES
# =============================================================================
def _normalizar_texto(valor: object) -> str:
    """Mayúsculas sin tildes ni espacios duplicados; '' si nulo."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto)


def _registrar(mensaje: str) -> None:
    """Log minimalista con timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")


def _a_numerico(serie: pd.Series) -> pd.Series:
    """Convierte a numérico tolerando coma decimal; no-numéricos → NaN."""
    if serie.dtype.kind in "iuf":
        return serie
    return pd.to_numeric(
        serie.astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )


# =============================================================================
# 3. SOPORTE PARA GOOGLE COLAB
# =============================================================================
def en_colab() -> bool:
    """True si el script se está ejecutando dentro de Google Colab."""
    return "google.colab" in sys.modules or os.path.exists("/content")


def instalar_dependencias_si_aplica(
    paquetes: Iterable[str] = PAQUETES_REQUERIDOS,
) -> None:
    """En Colab: hace `pip install` silencioso de los paquetes faltantes."""
    if not en_colab():
        return
    import importlib.util
    import subprocess
    faltan = [p for p in paquetes
              if importlib.util.find_spec(p.replace("-", "_")) is None]
    if faltan:
        _registrar(f"Instalando paquetes faltantes en Colab: {faltan}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", *faltan]
        )


def montar_drive_si_aplica(punto_montaje: str = "/content/drive") -> bool:
    """Si estamos en Google Colab, monta Drive y devuelve True. Si no, False.

    Devuelve True si Drive quedó montado y False en caso contrario.
    """
    if not en_colab():
        return False
    try:
        from google.colab import drive  # type: ignore
    except ImportError:
        return False
    if not os.path.ismount(punto_montaje):
        _registrar(f"Montando Google Drive en {punto_montaje} ...")
        drive.mount(punto_montaje, force_remount=False)
    return True


def setup_colab() -> None:
    """Acceso único para Colab: instala deps + monta Drive (si aplica)."""
    instalar_dependencias_si_aplica()
    montar_drive_si_aplica()


# =============================================================================
# 4. LECTURA DE ARCHIVOS
# =============================================================================
def _detectar_formato(ruta: str) -> Tuple[str, str]:
    """Detecta separador y codificación leyendo una muestra del archivo."""
    for codificacion in CODIFICACIONES_CANDIDATAS:
        for separador in SEPARADORES_CANDIDATOS:
            try:
                muestra = pd.read_csv(
                    ruta, sep=separador, encoding=codificacion,
                    nrows=5, on_bad_lines="skip", engine="python",
                )
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
            if muestra.shape[1] > 1:
                return separador, codificacion
    raise ValueError(
        f"No se pudo detectar separador/codificación para: {ruta}"
    )


def _leer_columnas_disponibles(ruta: str, sep: str, enc: str) -> List[str]:
    """Lee solo la cabecera para saber qué columnas trae el archivo."""
    return list(
        pd.read_csv(ruta, sep=sep, encoding=enc, nrows=0, engine="python").columns
    )


def leer_archivo_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:
    """Carga el .txt del año, restringiéndose a las columnas requeridas."""
    nombre = PATRON_ARCHIVO.format(anio=anio)
    ruta = os.path.join(ruta_proyecto, nombre)
    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"Archivo no encontrado: {ruta}.\n"
            f"Esperado: '{PATRON_ARCHIVO.format(anio='YYYY')}'."
        )
    sep, enc = _detectar_formato(ruta)
    # Comparamos contra las columnas reales del archivo (case-insensitive)
    # porque algunas descargas tienen los nombres en mayúsculas.
    cols_archivo = _leer_columnas_disponibles(ruta, sep, enc)
    mapa_lower = {c.lower(): c for c in cols_archivo}
    usecols = [mapa_lower[c] for c in COLS_REQUERIDAS if c in mapa_lower]

    _registrar(f"Leyendo {nombre} (sep='{sep}', enc='{enc}', "
               f"{len(usecols)}/{len(COLS_REQUERIDAS)} cols solicitadas)")
    df = pd.read_csv(
        ruta, sep=sep, encoding=enc, usecols=usecols,
        on_bad_lines="skip", engine="python",
    )
    # Normalizar nombres a minúsculas para igualar el diccionario.
    df.columns = [c.lower() for c in df.columns]
    df["anio"] = anio
    # Si alguna columna requerida no estaba en el archivo, se crea como NaN
    # para que el esquema sea idéntico entre años.
    for col in COLS_REQUERIDAS:
        if col not in df.columns:
            df[col] = np.nan
    _registrar(f"  {nombre}: {len(df):,} filas × {df.shape[1]} columnas.")
    return df


# =============================================================================
# 5. CONSTRUCCIÓN DE VARIABLES (con drop incremental de fuentes)
# =============================================================================
# Cada función toma el dataframe, construye una variable y elimina la
# columna fuente cuando ya no se necesita más adelante. Así el dataframe
# va perdiendo peso a medida que avanza el pipeline.

def transformar_id_y_modulos(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra ID y los 5 puntajes de módulos a nombres compactos."""
    renombres = {
        "estu_consecutivo":          "id_estudiante",
        "mod_lectura_critica_punt":  "punt_lectura_critica",
        "mod_razona_cuantitat_punt": "punt_razona_cuant",
        "mod_competen_ciudada_punt": "punt_competen_ciud",
        "mod_comuni_escrita_punt":   "punt_comuni_escrita",
        "mod_ingles_punt":           "punt_ingles",
    }
    df = df.rename(columns=renombres)
    for col in MODULOS_GENERICOS:
        df[col] = _a_numerico(df[col])
    return df


def construir_periodo_ia(df: pd.DataFrame) -> pd.DataFrame:
    """periodo_ia = 0 si anio ∈ {2021,2022}; 1 si ∈ {2023,2024}."""
    df["periodo_ia"] = df["anio"].apply(
        lambda a: 0 if a in ANIOS_PREVIO else (1 if a in ANIOS_IA else np.nan)
    ).astype("Int64")
    return df


def construir_puntaje_generico(df: pd.DataFrame) -> pd.DataFrame:
    """Promedio simple de los cinco módulos disponibles fila a fila."""
    df["puntaje_saberpro_generico"] = (
        df[MODULOS_GENERICOS].mean(axis=1, skipna=True)
    )
    return df


def construir_edad(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula edad = anio - año(estu_fechanacimiento) y DESCARTA la fecha."""
    fecha = pd.to_datetime(
        df["estu_fechanacimiento"], errors="coerce", dayfirst=True,
    )
    df["edad"] = (df["anio"] - fecha.dt.year).astype("Float64")
    df.loc[(df["edad"] < 15) | (df["edad"] > 80), "edad"] = np.nan
    # Inmediatamente se elimina la fecha de nacimiento: ya no se necesita.
    df = df.drop(columns=["estu_fechanacimiento"])
    return df


def construir_genero(df: pd.DataFrame) -> pd.DataFrame:
    """genero: F → 0, M → 1. Otros valores → NaN. Drop de la fuente."""
    norm = df["estu_genero"].apply(_normalizar_texto)
    df["genero"] = norm.map({"F": 0, "FEMENINO": 0, "M": 1, "MASCULINO": 1}).astype("Int64")
    df = df.drop(columns=["estu_genero"])
    return df


def construir_estrato(df: pd.DataFrame) -> pd.DataFrame:
    """estrato: extrae 1–6 desde 'Estrato N'. 'Sin estrato' → NaN."""
    extraido = (
        df["fami_estratovivienda"].astype(str)
        .str.extract(r"(\d)", expand=False).astype("Float64")
    )
    extraido = extraido.where(extraido.between(1, 6))
    df["estrato"] = extraido
    df = df.drop(columns=["fami_estratovivienda"])
    return df


def construir_nivel_educ_padre(df: pd.DataFrame) -> pd.DataFrame:
    """Codifica la educación del padre en escala ordinal 1-7."""
    norm = df["fami_educacionpadre"].apply(_normalizar_texto)
    mapa = {
        "NINGUNO":                              1,
        "PRIMARIA INCOMPLETA":                  2,
        "PRIMARIA COMPLETA":                    3,
        "SECUNDARIA (BACHILLERATO) INCOMPLETA": 4,
        "SECUNDARIA (BACHILLERATO) COMPLETA":   5,
        "TECNICA O TECNOLOGICA INCOMPLETA":     5,
        "TECNICA O TECNOLOGICA COMPLETA":       6,
        "EDUCACION PROFESIONAL INCOMPLETA":     6,
        "EDUCACION PROFESIONAL COMPLETA":       7,
        "POSTGRADO":                            7,
        # "NO SABE" → NaN intencional (no se mapea).
    }
    df["nivel_educ_padre"] = norm.map(mapa).astype("Float64")
    df = df.drop(columns=["fami_educacionpadre"])
    return df


def construir_estu_trabaja(df: pd.DataFrame) -> pd.DataFrame:
    """1 si reporta cualquier hora positiva semanal, 0 si '0'."""
    norm = df["estu_horassemanatrabaja"].apply(_normalizar_texto)
    df["estu_trabaja"] = norm.map({
        "0":                       0,
        "MENOS DE 10 HORAS":       1,
        "ENTRE 11 Y 20 HORAS":     1,
        "ENTRE 21 Y 30 HORAS":     1,
        "MAS DE 30 HORAS":         1,
    }).astype("Int64")
    df = df.drop(columns=["estu_horassemanatrabaja"])
    return df


def construir_cabeza_familia(df: pd.DataFrame) -> pd.DataFrame:
    """Proxy: NO pagan padres ⇒ se asume cabeza de familia (1)."""
    norm = df["estu_pagomatriculapadres"].apply(_normalizar_texto)
    df["estu_cabeza_familia"] = norm.map({"SI": 0, "NO": 1}).astype("Int64")
    df = df.drop(columns=["estu_pagomatriculapadres"])
    return df


def construir_jornada(df: pd.DataFrame) -> pd.DataFrame:
    """jornada: 1 si metodología no presencial (DISTANCIA/VIRTUAL), 0 si no.

    Nota: el campo `estu_horario_prgm` no existe para 2021-2024 en el
    diccionario DataICFES, por lo que se aproxima con `estu_metodo_prgm`.
    """
    norm = df["estu_metodo_prgm"].apply(_normalizar_texto)
    df["jornada"] = np.where(
        norm.str.contains("DISTANCIA|VIRTUAL", regex=True), 1,
        np.where(norm.str.contains("PRESENCIAL"), 0, np.nan),
    )
    df["jornada"] = pd.array(df["jornada"], dtype="Float64").astype("Int64")
    df = df.drop(columns=["estu_metodo_prgm"])
    return df


def construir_internet(df: pd.DataFrame) -> pd.DataFrame:
    """internet: Si → 1, No → 0."""
    norm = df["fami_tieneinternet"].apply(_normalizar_texto)
    df["internet"] = norm.map({"SI": 1, "NO": 0}).astype("Int64")
    df = df.drop(columns=["fami_tieneinternet"])
    return df


def construir_area_residencia(df: pd.DataFrame) -> pd.DataFrame:
    """area_residencia: 1 si cabecera/urbano, 0 si rural."""
    norm = df["estu_areareside"].apply(_normalizar_texto)
    df["area_residencia"] = np.where(
        norm.str.contains("CABECERA|URBAN", regex=True), 1,
        np.where(norm.str.contains("RURAL"), 0, np.nan),
    )
    df["area_residencia"] = pd.array(df["area_residencia"], dtype="Float64").astype("Int64")
    df = df.drop(columns=["estu_areareside"])
    return df


def construir_naturaleza_ies(df: pd.DataFrame) -> pd.DataFrame:
    """naturaleza_ies: NO OFICIAL ⇒ 1 (privada); OFICIAL ⇒ 0 (pública)."""
    norm = df["inst_origen"].apply(_normalizar_texto)
    df["naturaleza_ies"] = np.where(
        norm.str.startswith("NO OFICIAL"), 1,
        np.where(norm.str.startswith("OFICIAL") | norm.str.contains("REGIMEN ESPECIAL"),
                 0, np.nan),
    )
    df["naturaleza_ies"] = pd.array(df["naturaleza_ies"], dtype="Float64").astype("Int64")
    df = df.drop(columns=["inst_origen"])
    return df


def _canonizar_departamento(valor: object) -> Optional[str]:
    """Devuelve el nombre canónico (clave de DEPARTAMENTOS) o None."""
    texto = _normalizar_texto(valor)
    if not texto:
        return None
    if texto in ALIAS_DEPARTAMENTOS:
        return ALIAS_DEPARTAMENTOS[texto]
    if texto in DEPARTAMENTOS:
        return texto
    for canon in DEPARTAMENTOS:
        if texto.startswith(canon) or canon in texto:
            return canon
    return None


def construir_departamento_y_distancia(df: pd.DataFrame) -> pd.DataFrame:
    """Construye departamento (0-32), departamento_nombre y distancia_bogota_km."""
    canon = df["estu_inst_departamento"].apply(_canonizar_departamento)
    df["departamento_nombre"] = canon
    df["departamento"] = canon.map(
        {n: c for n, (c, _) in DEPARTAMENTOS.items()}
    ).astype("Int64")
    df["distancia_bogota_km"] = canon.map(
        {n: d for n, (_, d) in DEPARTAMENTOS.items()}
    ).astype("Float64")
    df = df.drop(columns=["estu_inst_departamento"])
    return df


def construir_identificadores_fe(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra cod_ies y municipio_ies (sin transformación adicional)."""
    df = df.rename(columns={
        "inst_cod_institucion": "cod_ies",
        "estu_inst_municipio":  "municipio_ies",
    })
    df["cod_ies"] = pd.to_numeric(df["cod_ies"], errors="coerce").astype("Int64")
    return df


def construir_tipo_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """tipo_municipio: 0 = Bogotá, 1 = capital de otro dpto, 2 = resto.

    Usa el municipio normalizado de la IES y la tabla CAPITALES para
    decidir, sin eliminar municipio_ies (que se conserva para EF).
    """
    mun_norm = df["municipio_ies"].apply(_normalizar_texto)
    # Capital esperada de cada departamento (también normalizada).
    capital_esperada = df["departamento_nombre"].map(
        {n: _normalizar_texto(c) for n, c in CAPITALES.items()}
    )
    es_bogota = df["departamento_nombre"].eq("BOGOTA")
    es_capital_otro = (~es_bogota) & (mun_norm == capital_esperada)
    df["tipo_municipio"] = np.where(
        es_bogota, 0,
        np.where(es_capital_otro, 1, 2),
    )
    df["tipo_municipio"] = pd.array(df["tipo_municipio"], dtype="Int64")
    return df


def construir_todas_las_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica en orden las 16 transformaciones; cada una elimina su fuente
    cuando ya no se necesita."""
    df = transformar_id_y_modulos(df)
    df = construir_periodo_ia(df)
    df = construir_puntaje_generico(df)
    df = construir_edad(df)                 # drop estu_fechanacimiento
    df = construir_genero(df)               # drop estu_genero
    df = construir_estrato(df)              # drop fami_estratovivienda
    df = construir_nivel_educ_padre(df)     # drop fami_educacionpadre
    df = construir_estu_trabaja(df)         # drop estu_horassemanatrabaja
    df = construir_cabeza_familia(df)       # drop estu_pagomatriculapadres
    df = construir_jornada(df)              # drop estu_metodo_prgm
    df = construir_internet(df)             # drop fami_tieneinternet
    df = construir_area_residencia(df)      # drop estu_areareside
    df = construir_naturaleza_ies(df)       # drop inst_origen
    df = construir_departamento_y_distancia(df)  # drop estu_inst_departamento
    df = construir_identificadores_fe(df)   # rename cod_ies, municipio_ies
    df = construir_tipo_municipio(df)       # crea tipo_municipio (mantiene municipio_ies)
    return df


# =============================================================================
# 6. LIMPIEZA
# =============================================================================
def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza integral: rangos, tipos, faltantes críticos y duplicados."""
    n_inicial = len(df)

    # 1) Puntajes fuera del rango oficial Saber Pro [0, 300] → NaN celda.
    for col in MODULOS_GENERICOS + ["puntaje_saberpro_generico"]:
        fuera = ~df[col].between(0, 300)
        df.loc[fuera & df[col].notna(), col] = np.nan

    # 2) Filas sin variable dependiente → no aportan al análisis.
    df = df[df["puntaje_saberpro_generico"].notna()].copy()

    # 3) Filas sin departamento → sin anclaje geográfico ni distancia.
    df = df[df["departamento"].notna()].copy()

    # 4) Duplicados exactos por (id_estudiante, anio).
    df = df.drop_duplicates(subset=["id_estudiante", "anio"], keep="first")

    # 5) Reindexar.
    df = df.reset_index(drop=True)

    _registrar(f"Limpieza: {n_inicial:,} → {len(df):,} filas "
               f"(eliminadas {n_inicial - len(df):,}).")
    return df


def seleccionar_variables_finales(df: pd.DataFrame) -> pd.DataFrame:
    """Reordena y conserva sólo las 22 columnas de la unión Tabla 2 ∪ Tabla 3."""
    return df[VARIABLES_FINALES].copy()


# =============================================================================
# 7. PROCESAMIENTO POR AÑO Y CONSOLIDACIÓN
# =============================================================================
def procesar_anio(ruta_proyecto: str, anio: int) -> pd.DataFrame:
    """Pipeline completo para un único año (lectura → construcción → limpieza)."""
    crudo = leer_archivo_anio(ruta_proyecto, anio)
    construido = construir_todas_las_variables(crudo)
    final = seleccionar_variables_finales(construido)
    final = limpiar(final)
    _registrar(f"df_{anio} listo: {len(final):,} filas × {final.shape[1]} cols.")
    return final


def consolidar(dfs: Dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Apila los dataframes anuales en uno solo."""
    df = pd.concat(dfs.values(), axis=0, ignore_index=True)
    df = df[VARIABLES_FINALES].copy()
    _registrar(f"df_consolidado: {len(df):,} filas × {df.shape[1]} cols.")
    return df


def persistir(ruta_proyecto: str,
              dfs: Dict[int, pd.DataFrame],
              df_consolidado: pd.DataFrame) -> str:
    """Guarda los df anuales y el consolidado en `procesados/` como CSV."""
    salida = os.path.join(ruta_proyecto, "procesados")
    os.makedirs(salida, exist_ok=True)
    for anio, df in dfs.items():
        df.to_csv(os.path.join(salida, f"df_{anio}.csv"),
                  index=False, encoding="utf-8-sig")
        _registrar(f"Guardado: df_{anio}.csv")
    df_consolidado.to_csv(os.path.join(salida, "df_consolidado.csv"),
                          index=False, encoding="utf-8-sig")
    _registrar(f"Guardado: df_consolidado.csv")
    return salida


# =============================================================================
# 8. ORQUESTADOR
# =============================================================================
def ejecutar_pipeline(
    ruta_proyecto: Optional[str] = None,
    anios: Iterable[int] = ANIOS,
    persistir_disco: bool = True,
) -> Tuple[Dict[int, pd.DataFrame], pd.DataFrame]:
    """Punto de entrada principal del pipeline.

    Parámetros
    ----------
    ruta_proyecto : str, opcional
        Carpeta con los `Examen_Saber_Pro_Genericas_<año>.txt`.
        Si es None y se está en Google Colab, monta Drive y usa
        `/content/drive/MyDrive/IA_EDUCACION_SUPERIOR`.
    anios : iterable de int
        Años a procesar (por defecto 2021-2024).
    persistir_disco : bool
        Si True, escribe los CSV en `<ruta_proyecto>/procesados/`.

    Devuelve
    --------
    (dfs_por_anio, df_consolidado)
        Diccionario {año: DataFrame} y el DataFrame consolidado.
    """
    _registrar("== INICIO DEL PIPELINE ==")
    if ruta_proyecto is None:
        # Modo Colab: monta Drive y usa la ruta por defecto en MyDrive.
        setup_colab()
        ruta_proyecto = RUTA_DEFECTO
    if not os.path.isdir(ruta_proyecto):
        raise FileNotFoundError(
            f"Carpeta no existe: {ruta_proyecto}\n"
            "En Colab: cree 'Mi unidad/IA_EDUCACION_SUPERIOR' y suba allí los .txt."
        )
    dfs: Dict[int, pd.DataFrame] = {}
    for anio in anios:
        _registrar(f"-- Procesando año {anio} --")
        dfs[anio] = procesar_anio(ruta_proyecto, anio)
    df_consolidado = consolidar(dfs)
    if persistir_disco:
        persistir(ruta_proyecto, dfs, df_consolidado)
    _registrar("== FIN DEL PIPELINE ==")
    return dfs, df_consolidado


# =============================================================================
# 9. INTERFAZ DE LÍNEA DE COMANDOS
# =============================================================================
def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pipeline de preparación de datos Saber Pro 2021-2024.",
    )
    parser.add_argument(
        "--ruta", "-r", default=None,
        help="Carpeta con los archivos Examen_Saber_Pro_Genericas_<año>.txt. "
             "Omitir en Colab para usar `Mi unidad/IA_EDUCACION_SUPERIOR`.",
    )
    parser.add_argument(
        "--anios", "-a", nargs="+", type=int, default=ANIOS,
        help="Años a procesar (por defecto: 2021 2022 2023 2024).",
    )
    parser.add_argument(
        "--sin-guardar", action="store_true",
        help="Si se indica, NO escribe los CSV en disco.",
    )
    return parser


if __name__ == "__main__":
    args = _construir_parser().parse_args()
    dfs_anio, df_consolidado = ejecutar_pipeline(
        ruta_proyecto=args.ruta,
        anios=args.anios,
        persistir_disco=not args.sin_guardar,
    )
    # Resumen rápido por cohorte.
    print("\n== Resumen ==")
    print(df_consolidado.groupby("periodo_ia")["puntaje_saberpro_generico"]
          .agg(["count", "mean", "std"]).round(2))
