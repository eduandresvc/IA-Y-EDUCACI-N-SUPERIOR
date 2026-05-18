"""
==============================================================================
analisis_descriptivo.py
==============================================================================
Parte 1 de la investigación: análisis bivariado / descriptivo entre las
cohortes 2021–2022 (periodo_ia = 0) y 2023–2024 (periodo_ia = 1).

Corresponde a la Sección 9 del documento (Tabla 3 y figuras recomendadas):

  • Variables continuas: media ± DE, n por cohorte, diferencia, prueba t
    de Welch y prueba no paramétrica Mann–Whitney como contraparte robusta.
  • Variables ordinales (estrato, nivel_educ_padre): se reportan como
    continuas en t-test y como categóricas en χ².
  • Variables dicotómicas (% por cohorte): diferencia en puntos
    porcentuales y prueba χ² de Pearson.
  • Tabla descriptiva por departamento: medias del puntaje genérico y de
    cada módulo por cohorte.
  • Cuatro figuras: boxplot por cohorte, boxplot por departamento,
    histograma comparativo y dispersión distancia–puntaje.

Salidas (en `<ruta>/procesados/resultados/` y `<ruta>/procesados/figuras/`):

    tabla3_descriptivo.csv          Tabla 3 completa con estadísticos y p.
    tabla3_por_departamento.csv     Medias por (departamento × cohorte).
    fig_boxplot_periodo.png         Boxplot del puntaje genérico por cohorte.
    fig_boxplot_departamento.png    Boxplot del puntaje genérico por dpto.
    fig_histograma_cohortes.png     Histograma comparativo entre cohortes.
    fig_dispersion_distancia.png    Dispersión distancia ↔ puntaje promedio.
==============================================================================
"""

from __future__ import annotations

import argparse
import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")              # backend sin GUI (válido en servidores).
import matplotlib.pyplot as plt    # noqa: E402  (import después de use)

from preparar_datos import (
    MODULOS_GENERICOS, _registrar, ANIOS_PREVIO, ANIOS_IA,
)


# =============================================================================
# 1. CONSTANTES — variables a comparar entre cohortes (Tabla 3 del documento)
# =============================================================================
# Continuas / ordinales que se prueban con t-Welch + Mann–Whitney.
VARS_CONTINUAS: List[str] = [
    "puntaje_saberpro_generico",
    *MODULOS_GENERICOS,
    "estrato",                  # ordinal tratada como continua
    "edad",
    "nivel_educ_padre",         # ordinal tratada como continua
    "distancia_bogota_km",
]

# Dicotómicas que se prueban con χ² (% por cohorte).
VARS_DICOTOMICAS: List[str] = [
    "genero",                   # 1 = masculino
    "estu_trabaja",
    "estu_cabeza_familia",
    "jornada",
    "internet",
    "area_residencia",
    "naturaleza_ies",           # 1 = privada
]

ALPHA: float = 0.05


# =============================================================================
# 2. CARGA DEL CONSOLIDADO
# =============================================================================
def cargar_consolidado(ruta_proyecto: str) -> pd.DataFrame:
    """Lee `<ruta>/procesados/df_consolidado.csv` que produce el pipeline."""
    ruta = os.path.join(ruta_proyecto, "procesados", "df_consolidado.csv")
    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"No existe {ruta}.\n"
            "Ejecute primero `python preparar_datos.py --ruta <carpeta>`."
        )
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    _registrar(f"Consolidado cargado: {len(df):,} filas × {df.shape[1]} cols.")
    return df


# =============================================================================
# 3. ESTADÍSTICOS POR COHORTE
# =============================================================================
def _fmt_p(p: float) -> str:
    """Formatea p-valores con la convención '< 0.001' y truncamiento."""
    if pd.isna(p):
        return "NA"
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def _resumen_continua(serie_0: pd.Series, serie_1: pd.Series) -> Dict[str, float]:
    """Estadísticos para variable continua: media, DE, n, Δ, t-Welch y MW."""
    s0 = pd.to_numeric(serie_0, errors="coerce").dropna()
    s1 = pd.to_numeric(serie_1, errors="coerce").dropna()
    if len(s0) < 2 or len(s1) < 2:
        return {"n_0": len(s0), "n_1": len(s1), "media_0": np.nan,
                "media_1": np.nan, "sd_0": np.nan, "sd_1": np.nan,
                "delta": np.nan, "t_welch": np.nan, "p_t": np.nan,
                "U_mw": np.nan, "p_mw": np.nan}
    t, p_t = stats.ttest_ind(s0, s1, equal_var=False, nan_policy="omit")
    u, p_mw = stats.mannwhitneyu(s0, s1, alternative="two-sided")
    return {
        "n_0":   int(len(s0)),     "n_1":   int(len(s1)),
        "media_0": float(s0.mean()), "media_1": float(s1.mean()),
        "sd_0":  float(s0.std(ddof=1)),  "sd_1": float(s1.std(ddof=1)),
        "delta": float(s1.mean() - s0.mean()),
        "t_welch": float(t),   "p_t":  float(p_t),
        "U_mw":   float(u),    "p_mw": float(p_mw),
    }


def _resumen_dicotomica(serie_0: pd.Series, serie_1: pd.Series) -> Dict[str, float]:
    """Estadísticos para variable dicotómica: % por cohorte y χ²."""
    s0 = pd.to_numeric(serie_0, errors="coerce").dropna()
    s1 = pd.to_numeric(serie_1, errors="coerce").dropna()
    if len(s0) < 2 or len(s1) < 2:
        return {"n_0": len(s0), "n_1": len(s1), "prop_0": np.nan,
                "prop_1": np.nan, "delta_pp": np.nan,
                "chi2": np.nan, "p_chi2": np.nan}
    # Tabla de contingencia 2 × 2: (cohorte) × (valor binario).
    tabla = pd.crosstab(
        pd.concat([pd.Series(0, index=s0.index), pd.Series(1, index=s1.index)]),
        pd.concat([s0, s1]),
    )
    chi2, p, *_ = stats.chi2_contingency(tabla, correction=True)
    return {
        "n_0":      int(len(s0)),         "n_1":      int(len(s1)),
        "prop_0":   float(s0.mean()),     "prop_1":   float(s1.mean()),
        "delta_pp": float((s1.mean() - s0.mean()) * 100),
        "chi2":     float(chi2),          "p_chi2":   float(p),
    }


def tabla3_descriptivo(df: pd.DataFrame) -> pd.DataFrame:
    """Construye la Tabla 3 con todas las variables y todas las pruebas."""
    pre = df[df["periodo_ia"] == 0]
    pos = df[df["periodo_ia"] == 1]
    filas: List[Dict[str, object]] = []

    for var in VARS_CONTINUAS:
        if var not in df.columns:
            continue
        r = _resumen_continua(pre[var], pos[var])
        filas.append({
            "variable":            var,
            "tipo":                "continua/ordinal",
            "n_2021_22":           r["n_0"],
            "n_2023_24":           r["n_1"],
            "media_2021_22":       round(r["media_0"], 3),
            "sd_2021_22":          round(r["sd_0"], 3),
            "media_2023_24":       round(r["media_1"], 3),
            "sd_2023_24":          round(r["sd_1"], 3),
            "delta_o_pp":          round(r["delta"], 3),
            "estadistico_t":       round(r["t_welch"], 3),
            "p_t_welch":           _fmt_p(r["p_t"]),
            "estadistico_chi2":    None,
            "p_chi2":              None,
            "estadistico_U_mw":    round(r["U_mw"], 1),
            "p_mw":                _fmt_p(r["p_mw"]),
            "significativo_5pct":  (r["p_t"] < ALPHA) if not pd.isna(r["p_t"]) else None,
        })

    for var in VARS_DICOTOMICAS:
        if var not in df.columns:
            continue
        r = _resumen_dicotomica(pre[var], pos[var])
        filas.append({
            "variable":            var,
            "tipo":                "dicotomica",
            "n_2021_22":           r["n_0"],
            "n_2023_24":           r["n_1"],
            "media_2021_22":       round(r["prop_0"] * 100, 2),  # %
            "sd_2021_22":          None,
            "media_2023_24":       round(r["prop_1"] * 100, 2),
            "sd_2023_24":          None,
            "delta_o_pp":          round(r["delta_pp"], 2),
            "estadistico_t":       None,
            "p_t_welch":           None,
            "estadistico_chi2":    round(r["chi2"], 3),
            "p_chi2":              _fmt_p(r["p_chi2"]),
            "estadistico_U_mw":    None,
            "p_mw":                None,
            "significativo_5pct":  (r["p_chi2"] < ALPHA) if not pd.isna(r["p_chi2"]) else None,
        })

    return pd.DataFrame(filas)


# =============================================================================
# 4. TABLA DESCRIPTIVA POR DEPARTAMENTO
# =============================================================================
def tabla_por_departamento(df: pd.DataFrame) -> pd.DataFrame:
    """Medias del puntaje genérico y módulos por (departamento × cohorte)."""
    cols_valor = ["puntaje_saberpro_generico", *MODULOS_GENERICOS]
    grupo = (df.groupby(["departamento", "departamento_nombre", "periodo_ia"])
               [cols_valor].mean().round(2).reset_index())
    # Pivot: una fila por departamento, una columna por (variable, cohorte).
    pivot = grupo.pivot_table(
        index=["departamento", "departamento_nombre"],
        columns="periodo_ia", values=cols_valor,
    )
    pivot.columns = [f"{var}__periodo_{p}" for var, p in pivot.columns]
    pivot = pivot.reset_index().sort_values("departamento")
    return pivot


# =============================================================================
# 5. FIGURAS
# =============================================================================
def figura_boxplot_periodo(df: pd.DataFrame, ruta_out: str) -> None:
    """Boxplot del puntaje genérico por cohorte temporal."""
    fig, ax = plt.subplots(figsize=(7, 5))
    datos = [df.loc[df["periodo_ia"] == p, "puntaje_saberpro_generico"].dropna()
             for p in (0, 1)]
    ax.boxplot(datos, labels=["2021-2022\n(pre-IA)", "2023-2024\n(IA Gen)"])
    ax.set_ylabel("Puntaje Saber Pro genérico (0-300)")
    ax.set_title("Distribución del puntaje genérico por cohorte")
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def figura_boxplot_departamento(df: pd.DataFrame, ruta_out: str) -> None:
    """Boxplot del puntaje genérico por departamento (ordenado por mediana)."""
    fig, ax = plt.subplots(figsize=(14, 6))
    grupos = (df.groupby("departamento_nombre")["puntaje_saberpro_generico"]
                .median().sort_values(ascending=False))
    datos = [df.loc[df["departamento_nombre"] == d, "puntaje_saberpro_generico"].dropna()
             for d in grupos.index]
    ax.boxplot(datos, labels=grupos.index, showfliers=False)
    ax.set_ylabel("Puntaje Saber Pro genérico (0-300)")
    ax.set_title("Puntaje genérico por departamento de la IES")
    ax.tick_params(axis="x", rotation=75, labelsize=8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def figura_histograma_cohortes(df: pd.DataFrame, ruta_out: str) -> None:
    """Histograma comparativo del puntaje genérico entre cohortes."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for p, etiqueta, alpha in [(0, "2021-2022", 0.55), (1, "2023-2024", 0.55)]:
        ax.hist(df.loc[df["periodo_ia"] == p, "puntaje_saberpro_generico"].dropna(),
                bins=40, alpha=alpha, label=etiqueta, edgecolor="white", linewidth=0.4)
    ax.set_xlabel("Puntaje Saber Pro genérico")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de puntajes por cohorte")
    ax.legend()
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def figura_dispersion_distancia(df: pd.DataFrame, ruta_out: str) -> None:
    """Dispersión: distancia a Bogotá vs puntaje medio por departamento."""
    medias = (df.groupby(["departamento_nombre", "distancia_bogota_km"])
                ["puntaje_saberpro_generico"].mean().reset_index())
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(medias["distancia_bogota_km"], medias["puntaje_saberpro_generico"],
               s=50, alpha=0.85)
    # Línea de tendencia simple (regresión lineal univariada por OLS).
    x = medias["distancia_bogota_km"].values
    y = medias["puntaje_saberpro_generico"].values
    if len(x) >= 2:
        coef = np.polyfit(x, y, deg=1)
        xs = np.linspace(x.min(), x.max(), 100)
        ax.plot(xs, np.polyval(coef, xs), linestyle="--", linewidth=1.2,
                label=f"OLS: y = {coef[0]:.3f}·x + {coef[1]:.1f}")
    for _, row in medias.iterrows():
        ax.annotate(row["departamento_nombre"][:6],
                    (row["distancia_bogota_km"], row["puntaje_saberpro_generico"]),
                    fontsize=7, alpha=0.7)
    ax.set_xlabel("Distancia a Bogotá D.C. (km)")
    ax.set_ylabel("Puntaje genérico medio por departamento")
    ax.set_title("Centralización geográfica: distancia ↔ puntaje")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=150, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# 6. ORQUESTADOR
# =============================================================================
def ejecutar_analisis_descriptivo(
    ruta_proyecto: str,
) -> Dict[str, object]:
    """Pipeline completo de la Parte 1. Devuelve dict con tablas y rutas."""
    _registrar("== INICIO ANÁLISIS DESCRIPTIVO (Parte 1) ==")
    df = cargar_consolidado(ruta_proyecto)

    dir_tablas = os.path.join(ruta_proyecto, "procesados", "resultados")
    dir_figuras = os.path.join(ruta_proyecto, "procesados", "figuras")
    os.makedirs(dir_tablas, exist_ok=True)
    os.makedirs(dir_figuras, exist_ok=True)

    # Tabla 3 completa
    tab3 = tabla3_descriptivo(df)
    tab3.to_csv(os.path.join(dir_tablas, "tabla3_descriptivo.csv"),
                index=False, encoding="utf-8-sig")
    _registrar(f"  Tabla 3 guardada ({len(tab3)} filas).")

    # Tabla por departamento
    tab_dep = tabla_por_departamento(df)
    tab_dep.to_csv(os.path.join(dir_tablas, "tabla3_por_departamento.csv"),
                   index=False, encoding="utf-8-sig")
    _registrar(f"  Tabla por departamento guardada ({len(tab_dep)} dptos).")

    # Figuras
    figura_boxplot_periodo(df, os.path.join(dir_figuras, "fig_boxplot_periodo.png"))
    figura_boxplot_departamento(df, os.path.join(dir_figuras, "fig_boxplot_departamento.png"))
    figura_histograma_cohortes(df, os.path.join(dir_figuras, "fig_histograma_cohortes.png"))
    figura_dispersion_distancia(df, os.path.join(dir_figuras, "fig_dispersion_distancia.png"))
    _registrar("  Cuatro figuras guardadas.")

    _registrar("== FIN ANÁLISIS DESCRIPTIVO ==")
    return {
        "tabla3":              tab3,
        "tabla_departamento":  tab_dep,
        "dir_tablas":          dir_tablas,
        "dir_figuras":         dir_figuras,
    }


# =============================================================================
# 7. CLI
# =============================================================================
def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Parte 1: análisis bivariado / descriptivo Saber Pro.",
    )
    p.add_argument("--ruta", "-r", required=True,
                   help="Carpeta del proyecto que contiene `procesados/`.")
    return p


if __name__ == "__main__":
    args = _parser().parse_args()
    resultado = ejecutar_analisis_descriptivo(args.ruta)
    print("\n== Vista previa de Tabla 3 ==")
    print(resultado["tabla3"].to_string(index=False))
