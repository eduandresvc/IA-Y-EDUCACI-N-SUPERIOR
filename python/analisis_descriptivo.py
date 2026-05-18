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
from typing import Dict, List, Optional, Tuple

# Bootstrap perezoso: si estamos en Colab y faltan scipy/matplotlib,
# se instalan antes de importarlos. En entornos locales se asume que el
# usuario ya los tiene; en Colab estos paquetes vienen preinstalados.
from preparar_datos import (
    MODULOS_GENERICOS, _registrar, ANIOS_PREVIO, ANIOS_IA,
    RUTA_DEFECTO, en_colab, instalar_dependencias_si_aplica,
    montar_drive_si_aplica,
)
instalar_dependencias_si_aplica(("scipy", "matplotlib", "seaborn"))

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")              # backend sin GUI (válido en servidores).
import matplotlib.pyplot as plt    # noqa: E402
import seaborn as sns              # noqa: E402

# Paleta y estilo global de las figuras (publicación, fondo blanco limpio).
PALETA_COHORTES: Dict[str, str] = {
    "2021-2022 (pre-IA)":   "#3A6FB0",  # azul sobrio
    "2023-2024 (IA Gen)":   "#E07A3F",  # naranja cálido
}
NOTA_FUENTE: str = "Fuente: DataICFES (2021-2024). Elaboración propia."


def _aplicar_estilo() -> None:
    """Aplica un tema global coherente para las figuras."""
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor":   "white",
        "axes.edgecolor":   "#444",
        "axes.linewidth":   0.9,
        "axes.titleweight": "bold",
        "axes.titlepad":    14,
        "axes.titlesize":   13,
        "axes.labelsize":   11,
        "xtick.labelsize":  9.5,
        "ytick.labelsize":  9.5,
        "legend.frameon":   True,
        "legend.framealpha": 0.95,
        "legend.edgecolor": "#ccc",
        "grid.linestyle":   ":",
        "grid.alpha":       0.55,
        "savefig.facecolor": "white",
    })


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
# 5. FIGURAS — estilo publicación con seaborn
# =============================================================================
def _anotar_fuente(fig: "plt.Figure", texto: str = NOTA_FUENTE) -> None:
    """Pie de figura con la fuente de los datos."""
    fig.text(0.995, 0.005, texto, ha="right", va="bottom",
             fontsize=8.2, style="italic", color="#666")


def figura_boxplot_periodo(df: pd.DataFrame, ruta_out: str) -> None:
    """Violin + box del puntaje genérico por cohorte, con prueba t anotada."""
    _aplicar_estilo()
    d = df.copy()
    d["Cohorte"] = d["periodo_ia"].map(
        {0: "2021-2022 (pre-IA)", 1: "2023-2024 (IA Gen)"}
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.violinplot(
        data=d, x="Cohorte", y="puntaje_saberpro_generico",
        hue="Cohorte", palette=PALETA_COHORTES, inner=None,
        linewidth=0, alpha=0.42, legend=False, ax=ax,
    )
    sns.boxplot(
        data=d, x="Cohorte", y="puntaje_saberpro_generico",
        hue="Cohorte", palette=PALETA_COHORTES, width=0.18,
        fliersize=0, linewidth=1.3, legend=False, ax=ax,
    )

    # Marcadores de media (diamantes blancos con borde negro).
    medias = d.groupby("Cohorte", observed=True)["puntaje_saberpro_generico"].mean()
    for i, (_, mu) in enumerate(medias.items()):
        ax.scatter(i, mu, marker="D", s=70, color="white",
                   edgecolor="black", linewidth=1.5, zorder=10)

    # Prueba t de Welch.
    s0 = d.loc[d["periodo_ia"] == 0, "puntaje_saberpro_generico"].dropna()
    s1 = d.loc[d["periodo_ia"] == 1, "puntaje_saberpro_generico"].dropna()
    t, p = stats.ttest_ind(s0, s1, equal_var=False)
    delta = s1.mean() - s0.mean()
    p_str = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"

    ax.set_title("Distribución del puntaje genérico Saber Pro por cohorte temporal")
    ax.set_xlabel("")
    ax.set_ylabel("Puntaje genérico (escala 0-300)")
    ax.text(
        0.5, 0.97,
        f"Δ medias = {delta:+.2f}   |   t de Welch = {t:.2f}, {p_str}   |   "
        f"n₁ = {len(s0):,}, n₂ = {len(s1):,}",
        transform=ax.transAxes, ha="center", va="top",
        fontsize=9.5, style="italic", color="#333",
        bbox=dict(boxstyle="round,pad=0.45", fc="white",
                  ec="#bbb", lw=0.7, alpha=0.95),
    )
    _anotar_fuente(fig)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=200, bbox_inches="tight")
    plt.close(fig)


def figura_boxplot_departamento(df: pd.DataFrame, ruta_out: str) -> None:
    """Boxplot agrupado: puntaje por departamento × cohorte."""
    _aplicar_estilo()
    d = df.copy()
    d["Cohorte"] = d["periodo_ia"].map({0: "2021-2022", 1: "2023-2024"})

    # Ordenar departamentos por la mediana global del puntaje.
    orden = (
        df.groupby("departamento_nombre")["puntaje_saberpro_generico"]
        .median().sort_values(ascending=False).index.tolist()
    )

    paleta_short = {"2021-2022": "#3A6FB0", "2023-2024": "#E07A3F"}

    fig, ax = plt.subplots(figsize=(15, 7))
    sns.boxplot(
        data=d, x="departamento_nombre", y="puntaje_saberpro_generico",
        hue="Cohorte", order=orden, palette=paleta_short,
        fliersize=2, linewidth=0.9, ax=ax,
    )

    # Línea vertical para señalar a Bogotá como referencia.
    if "BOGOTA" in orden:
        ax.axvline(orden.index("BOGOTA"), color="#cc3a3a",
                   linewidth=1.0, linestyle="--", alpha=0.45, zorder=0)
        ax.text(orden.index("BOGOTA"), ax.get_ylim()[1], " Bogotá (ref.)",
                color="#cc3a3a", fontsize=9, fontweight="bold", va="top")

    ax.set_title("Puntaje genérico Saber Pro por departamento de la IES y cohorte")
    ax.set_xlabel("Departamento de la IES (ordenado por mediana)")
    ax.set_ylabel("Puntaje genérico (0-300)")
    ax.tick_params(axis="x", rotation=70, labelsize=8.5)
    ax.legend(title="Cohorte", loc="upper right")

    _anotar_fuente(fig)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=200, bbox_inches="tight")
    plt.close(fig)


def figura_histograma_cohortes(df: pd.DataFrame, ruta_out: str) -> None:
    """Histograma + KDE comparativo entre cohortes con líneas de media."""
    _aplicar_estilo()
    d = df.copy()
    d["Cohorte"] = d["periodo_ia"].map(
        {0: "2021-2022 (pre-IA)", 1: "2023-2024 (IA Gen)"}
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(
        data=d, x="puntaje_saberpro_generico", hue="Cohorte",
        bins=50, palette=PALETA_COHORTES, alpha=0.55, kde=True,
        edgecolor="white", linewidth=0.5, ax=ax,
    )

    # Líneas verticales en las medias.
    medias = d.groupby("Cohorte", observed=True)["puntaje_saberpro_generico"].mean()
    for cohorte, mu in medias.items():
        color = PALETA_COHORTES[cohorte]
        ax.axvline(mu, color=color, linestyle="--", linewidth=1.6, alpha=0.85)
        ax.text(mu, ax.get_ylim()[1] * 0.95, f"  μ = {mu:.1f}",
                color=color, fontweight="bold", fontsize=9.5,
                rotation=90, va="top", ha="left")

    ax.set_title("Distribución del puntaje genérico Saber Pro por cohorte")
    ax.set_xlabel("Puntaje genérico (0-300)")
    ax.set_ylabel("Frecuencia")
    _anotar_fuente(fig)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=200, bbox_inches="tight")
    plt.close(fig)


def figura_dispersion_distancia(df: pd.DataFrame, ruta_out: str) -> None:
    """Dispersión distancia ↔ puntaje medio por departamento.

    El tamaño del marcador es proporcional al número de estudiantes
    y el color codifica la distancia a Bogotá.
    """
    _aplicar_estilo()
    agg = (
        df.groupby(["departamento_nombre", "distancia_bogota_km"])
        .agg(puntaje_medio=("puntaje_saberpro_generico", "mean"),
             n_estudiantes=("puntaje_saberpro_generico", "count"))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(11, 7))
    tamanos = (agg["n_estudiantes"] / agg["n_estudiantes"].max() * 600 + 50).values
    sc = ax.scatter(
        agg["distancia_bogota_km"], agg["puntaje_medio"],
        s=tamanos, c=agg["distancia_bogota_km"],
        cmap="viridis_r", alpha=0.78,
        edgecolor="white", linewidth=1.2, zorder=3,
    )

    # Recta de ajuste OLS (ponderada por raíz de n para reflejar precisión).
    x = agg["distancia_bogota_km"].values.astype(float)
    y = agg["puntaje_medio"].values.astype(float)
    if len(x) >= 2:
        w = np.sqrt(agg["n_estudiantes"].values)
        coef = np.polyfit(x, y, deg=1, w=w)
        xs = np.linspace(0, x.max() * 1.05, 100)
        ax.plot(xs, np.polyval(coef, xs), linestyle="--", color="#222",
                linewidth=2.0, alpha=0.78, zorder=2,
                label=f"OLS ponderada: y = {coef[0]:+.4f}·dist + {coef[1]:.1f}")

    # Etiquetas para departamentos destacados.
    destacados = {"BOGOTA", "ANTIOQUIA", "VALLE", "HUILA", "AMAZONAS",
                  "SAN ANDRES", "ATLANTICO", "NARINO", "VAUPES", "GUAINIA"}
    for _, r in agg.iterrows():
        if r["departamento_nombre"] in destacados:
            ax.annotate(
                r["departamento_nombre"].title()[:11],
                (r["distancia_bogota_km"], r["puntaje_medio"]),
                xytext=(8, 8), textcoords="offset points",
                fontsize=8.6, fontweight="bold", color="#222",
                bbox=dict(boxstyle="round,pad=0.2",
                          fc="white", ec="none", alpha=0.75),
            )

    cbar = fig.colorbar(sc, ax=ax, shrink=0.75, pad=0.02)
    cbar.set_label("Distancia (km)", fontsize=9.5)

    ax.set_xlabel("Distancia terrestre a Bogotá D.C. (km)")
    ax.set_ylabel("Puntaje genérico medio por departamento")
    ax.set_title("Centralización geográfica: distancia ↔ desempeño Saber Pro")
    ax.legend(loc="lower left")
    _anotar_fuente(
        fig,
        "Tamaño del marcador ∝ n estudiantes.  " + NOTA_FUENTE,
    )
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=200, bbox_inches="tight")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figuras adicionales sugeridas para el manuscrito
# -----------------------------------------------------------------------------
def figura_heatmap_dpto_cohorte(df: pd.DataFrame, ruta_out: str) -> None:
    """Heatmap del puntaje medio por departamento × cohorte (ordenado)."""
    _aplicar_estilo()
    pivot = (
        df.pivot_table(values="puntaje_saberpro_generico",
                       index="departamento_nombre",
                       columns="periodo_ia", aggfunc="mean")
    )
    pivot.columns = ["2021-2022 (pre-IA)", "2023-2024 (IA Gen)"]
    pivot["Δ (post − pre)"] = pivot["2023-2024 (IA Gen)"] - pivot["2021-2022 (pre-IA)"]
    pivot = pivot.sort_values("2023-2024 (IA Gen)", ascending=False)

    fig, ax = plt.subplots(figsize=(8, max(6, 0.32 * len(pivot))))
    centro = pivot[["2021-2022 (pre-IA)", "2023-2024 (IA Gen)"]].mean().mean()
    sns.heatmap(
        pivot, annot=True, fmt=".1f", cmap="RdYlBu_r", center=centro,
        linewidths=0.5, linecolor="white",
        cbar_kws={"label": "Puntaje medio"}, ax=ax,
    )
    ax.set_title("Puntaje genérico medio por departamento y cohorte")
    ax.set_xlabel("")
    ax.set_ylabel("Departamento")
    _anotar_fuente(fig)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=200, bbox_inches="tight")
    plt.close(fig)


def figura_violines_por_modulo(df: pd.DataFrame, ruta_out: str) -> None:
    """Violines partidos comparando cohortes en los cinco módulos genéricos."""
    _aplicar_estilo()
    etiquetas = {
        "punt_lectura_critica":  "Lectura\nCrítica",
        "punt_razona_cuant":     "Razonamiento\nCuantitativo",
        "punt_competen_ciud":    "Competencias\nCiudadanas",
        "punt_comuni_escrita":   "Comunicación\nEscrita",
        "punt_ingles":           "Inglés",
    }
    largo = df.melt(
        id_vars=["periodo_ia"], value_vars=list(etiquetas),
        var_name="modulo_raw", value_name="puntaje",
    )
    largo["Módulo"] = largo["modulo_raw"].map(etiquetas)
    largo["Cohorte"] = largo["periodo_ia"].map(
        {0: "2021-2022 (pre-IA)", 1: "2023-2024 (IA Gen)"}
    )

    fig, ax = plt.subplots(figsize=(12, 6.5))
    sns.violinplot(
        data=largo, x="Módulo", y="puntaje", hue="Cohorte",
        split=True, palette=PALETA_COHORTES,
        inner="quart", linewidth=1.0, order=list(etiquetas.values()),
        ax=ax,
    )
    ax.set_title("Distribución por módulo genérico y cohorte temporal")
    ax.set_xlabel("Módulo de competencias genéricas")
    ax.set_ylabel("Puntaje (0-300)")
    ax.legend(title="Cohorte", loc="upper right")
    _anotar_fuente(fig)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=200, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# 6. ORQUESTADOR
# =============================================================================
def ejecutar_analisis_descriptivo(
    ruta_proyecto: Optional[str] = None,
) -> Dict[str, object]:
    """Pipeline completo de la Parte 1. Devuelve dict con tablas y rutas.

    Si `ruta_proyecto` es None y se está en Colab, monta Drive y usa
    `/content/drive/MyDrive/IA_EDUCACION_SUPERIOR`.
    """
    _registrar("== INICIO ANÁLISIS DESCRIPTIVO (Parte 1) ==")
    if ruta_proyecto is None:
        montar_drive_si_aplica()
        ruta_proyecto = RUTA_DEFECTO
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

    # Figuras (6 en total — estilo publicación)
    figura_boxplot_periodo(df,        os.path.join(dir_figuras, "fig_01_boxplot_periodo.png"))
    figura_histograma_cohortes(df,    os.path.join(dir_figuras, "fig_02_histograma_cohortes.png"))
    figura_violines_por_modulo(df,    os.path.join(dir_figuras, "fig_03_modulos_cohorte.png"))
    figura_boxplot_departamento(df,   os.path.join(dir_figuras, "fig_04_boxplot_departamento.png"))
    figura_heatmap_dpto_cohorte(df,   os.path.join(dir_figuras, "fig_05_heatmap_departamento.png"))
    figura_dispersion_distancia(df,   os.path.join(dir_figuras, "fig_06_dispersion_distancia.png"))
    _registrar("  Seis figuras de calidad publicación guardadas.")

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
    p.add_argument("--ruta", "-r", default=None,
                   help="Carpeta del proyecto. Omitir en Colab para usar "
                        "`Mi unidad/IA_EDUCACION_SUPERIOR`.")
    return p


if __name__ == "__main__":
    args = _parser().parse_args()
    resultado = ejecutar_analisis_descriptivo(args.ruta)
    print("\n== Vista previa de Tabla 3 ==")
    print(resultado["tabla3"].to_string(index=False))
