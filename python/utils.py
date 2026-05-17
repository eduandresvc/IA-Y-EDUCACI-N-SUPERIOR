# =============================================================================
# utils.py — Constantes y funciones auxiliares compartidas
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# Compatible con Google Colab
# =============================================================================

import numpy as np
import pandas as pd
import os

# Ruta del proyecto — se sobreescribe desde el notebook principal si es necesario
RUTA_PROYECTO = os.environ.get(
    "RUTA_PROYECTO",
    "/content/drive/MyDrive/IA-Y-EDUCACION-SUPERIOR"
)

# =============================================================================
# CONSTANTES DEL PROYECTO
# =============================================================================

# Análisis a nivel NACIONAL — sin filtro por IES ni programa

ANOS_PREVIO = [2021, 2022]   # periodo_ia = 0
ANOS_IA     = [2023, 2024]   # periodo_ia = 1

# Departamento de referencia (categoría base en el modelo)
DEPTO_REF = "BOGOTA"

# Distancias a Bogotá D.C. — todos los 33 departamentos + D.C.
# Fuente: IGAC/INVIAS. (*) = distancia aproximada aérea o fluvial.
DISTANCIAS_BOGOTA = {
    "BOGOTA":             0,
    "CUNDINAMARCA":      50,
    "BOYACA":           188,
    "TOLIMA":           210,
    "META":             270,
    "QUINDIO":          300,
    "HUILA":            310,
    "CALDAS":           320,
    "RISARALDA":        330,
    "SANTANDER":        380,
    "CASANARE":         380,
    "ANTIOQUIA":        415,
    "VALLE":            460,
    "CAQUETA":          558,
    "PUTUMAYO":         570,
    "GUAVIARE":         580,
    "CAUCA":            590,
    "NORTE DE SANTANDER": 600,
    "CHOCO":            600,
    "VICHADA":          700,   # *
    "NARINO":           785,
    "CORDOBA":          800,
    "ARAUCA":           900,
    "GUAINIA":          900,   # *
    "CESAR":            920,
    "SUCRE":            950,
    "MAGDALENA":       1000,
    "ATLANTICO":       1005,
    "BOLIVAR":         1050,
    "LA GUAJIRA":      1100,
    "VAUPES":          1100,   # *
    "AMAZONAS":        1200,   # *
    "SAN ANDRES":      2000,   # * aéreo
}

MODULOS_GENERICOS = [
    "punt_lectura_critica",
    "punt_razona_cuant",
    "punt_competen_ciud",
    "punt_comuni_escrita",
    "punt_ingles",
]

MODULOS_ETIQUETAS = {
    "punt_lectura_critica": "Lectura Crítica",
    "punt_razona_cuant":    "Razonamiento Cuantitativo",
    "punt_competen_ciud":   "Competencias Ciudadanas",
    "punt_comuni_escrita":  "Comunicación Escrita",
    "punt_ingles":          "Inglés",
}

CONTROLES = [
    "estrato", "genero", "nivel_educ_padre",
    "estu_trabaja", "estu_cabeza_familia",
    "internet", "area_residencia", "naturaleza_ies",
    "puntaje_saber11",
]

# Las dummies departamentales se crean dinámicamente con pd.get_dummies()
# o con C(depto_ies) en statsmodels — no se listan manualmente.
CONTROLES_LISTA = CONTROLES  # alias de compatibilidad

ALPHA = 0.05

ETIQUETAS_VARS = {
    "puntaje_saberpro_generico": "Puntaje Genérico (promedio 5 módulos)",
    "punt_lectura_critica":      "Lectura Crítica",
    "punt_razona_cuant":         "Razonamiento Cuantitativo",
    "punt_competen_ciud":        "Competencias Ciudadanas",
    "punt_comuni_escrita":       "Comunicación Escrita",
    "punt_ingles":               "Inglés",
    "periodo_ia":                "Período IA (2023-2024 = 1)",
    "estrato":                   "Estrato socioeconómico",
    "genero":                    "Género (Masculino = 1)",
    "nivel_educ_padre":          "Nivel educativo del padre",
    "estu_trabaja":              "Trabaja (Sí = 1)",
    "estu_cabeza_familia":       "Cabeza de familia",
    "jornada":                   "Jornada nocturna (= 1)",
    "internet":                  "Acceso a internet (Sí = 1)",
    "area_residencia":           "Área urbana (= 1)",
    "naturaleza_ies":            "IES privada (= 1)",
    "puntaje_saber11":           "Puntaje Saber 11",
    "distancia_bogota_km":       "Distancia a Bogotá (km)",
    "depto_ies":                 "Departamento IES (ref. Bogotá D.C.)",
}

COLORES_DEPTO = {
    "BOGOTA":    "#1A237E",
    "ANTIOQUIA": "#388E3C",
    "VALLE":     "#F57C00",
    "HUILA":     "#7B1FA2",
    "NARINO":    "#C62828",
    "TOLIMA":    "#00838F",
}

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def stars(p):
    """Devuelve estrellas de significancia para un p-valor."""
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    elif p < 0.10:
        return "."
    return ""


def fmt_pval(p):
    """Formatea p-valor con estrellas."""
    if pd.isna(p):
        return "NA"
    s = stars(p)
    if p < 0.001:
        return f"< 0.001{s}"
    return f"{p:.3f}{s}"


def calcular_puntaje_generico(df):
    """Calcula el promedio de los 5 módulos genéricos disponibles."""
    cols = [c for c in MODULOS_GENERICOS if c in df.columns]
    df = df.copy()
    df["puntaje_saberpro_generico"] = df[cols].mean(axis=1, skipna=True)
    return df


def guardar_tabla(df, nombre, directorio="outputs/tablas"):
    """Guarda DataFrame como CSV."""
    import os
    os.makedirs(directorio, exist_ok=True)
    ruta = os.path.join(directorio, f"{nombre}.csv")
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"  Tabla guardada: {ruta}")


def guardar_figura(fig, nombre, directorio="outputs/figuras",
                   ancho=12, alto=7, dpi=300):
    """Guarda figura matplotlib/seaborn."""
    import os
    os.makedirs(directorio, exist_ok=True)
    ruta = os.path.join(directorio, f"{nombre}.png")
    fig.savefig(ruta, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"  Figura guardada: {ruta}")


def instalar_paquetes():
    """Instala paquetes necesarios en Colab."""
    import subprocess, sys
    paquetes = [
        "statsmodels", "linearmodels", "pyreadstat",
        "pingouin", "openpyxl", "plotnine",
    ]
    for p in paquetes:
        try:
            __import__(p)
        except ImportError:
            print(f"Instalando {p}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   p, "-q"])
    print("Todos los paquetes disponibles.")
