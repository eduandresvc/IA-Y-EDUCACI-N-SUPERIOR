"""
==============================================================================
regresion_mco.py
==============================================================================
Parte 2 de la investigación: regresión lineal múltiple por Mínimos
Cuadrados Ordinarios (MCO). Corresponde a las Secciones 8 y 10 del
documento.

Modelos estimados
-----------------
Se estiman 6 dependientes × 3 especificaciones = 18 modelos.

  Dependientes (k):
    1. puntaje_saberpro_generico  (agregado: promedio de 5 módulos)
    2. punt_lectura_critica
    3. punt_razona_cuant
    4. punt_competen_ciud
    5. punt_comuni_escrita
    6. punt_ingles

  Especificaciones (s):
    1. "base"     — periodo_ia + dummies de departamento + distancia_bogota_km
                    + 10 controles socioeconómicos / académicos.
    2. "ef_ies"   — periodo_ia + EF por IES + 10 controles.
                    (Departamento y distancia quedan absorbidos por las IES.)
    3. "ef_mun"   — base + EF por tipo_municipio (Bogotá / capital / resto).

Para todas las especificaciones se reportan errores estándar
clusterizados a nivel de IES (cov_type='cluster'), tal como exige
§8.10 del documento.

Adicionalmente, sólo para el agregado `puntaje_saberpro_generico`,
se reporta el triángulo de colinealidad geográfica (§10): tres
versiones del modelo base con (a) sólo departamento, (b) sólo
distancia, (c) ambos, con cálculo de VIF en (c).

Diagnósticos (§8.10)
--------------------
Para cada uno de los 18 modelos se calculan:

  • Shapiro–Wilk (n < 5 000) o Kolmogorov–Smirnov (n ≥ 5 000)
    sobre los residuos.
  • Prueba de Breusch–Pagan (homocedasticidad).
  • Durbin–Watson (autocorrelación).
  • RESET de Ramsey (especificación).
  • VIF de las variables continuas (multicolinealidad; sólo Spec 1).

Corrección por pruebas múltiples (§12)
--------------------------------------
Los seis β_IA se corrigen por Holm y Benjamini–Hochberg.

Salidas
-------
    procesados/resultados/tabla4_<dep>__<spec>.csv     coeficientes
    procesados/resultados/diagnosticos.csv             diagnósticos
    procesados/resultados/beta_ia_resumen.csv          β_IA + correcciones
    procesados/resultados/colinealidad_geografica.csv  (a)/(b)/(c) + VIF
==============================================================================
"""

from __future__ import annotations

import argparse
import os
import warnings
from typing import Dict, List, Optional, Tuple

# Bootstrap perezoso: en Colab instala statsmodels/scipy si faltan
# antes de importarlos. En Colab moderno ya vienen preinstalados.
from preparar_datos import (
    MODULOS_GENERICOS, _registrar,
    RUTA_DEFECTO, en_colab, instalar_dependencias_si_aplica,
    montar_drive_si_aplica,
)
instalar_dependencias_si_aplica(("scipy", "statsmodels"))

import numpy as np
import pandas as pd

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import (het_breuschpagan,
                                          linear_reset)
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.multitest import multipletests
from scipy import stats


# =============================================================================
# 1. CONSTANTES
# =============================================================================
DEPENDIENTES: List[str] = [
    "puntaje_saberpro_generico",
    *MODULOS_GENERICOS,
]

# Controles socioeconómicos / académicos del modelo (Tabla 2 del documento).
CONTROLES: List[str] = [
    "estrato", "genero", "edad", "nivel_educ_padre",
    "estu_trabaja", "estu_cabeza_familia", "jornada",
    "internet", "area_residencia", "naturaleza_ies",
]

ESPECIFICACIONES: Tuple[str, ...] = ("base", "ef_ies", "ef_mun")

ALPHA: float = 0.05


# =============================================================================
# 2. CARGA Y SANEAMIENTO DEL CONSOLIDADO
# =============================================================================
def cargar_y_preparar(ruta_proyecto: str) -> pd.DataFrame:
    """Carga `df_consolidado.csv` y elimina filas con faltantes en el modelo."""
    ruta = os.path.join(ruta_proyecto, "procesados", "df_consolidado.csv")
    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"No existe {ruta}.\n"
            "Ejecute primero `python preparar_datos.py --ruta <carpeta>`."
        )
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    columnas_modelo = [
        *DEPENDIENTES, "periodo_ia", "departamento", "distancia_bogota_km",
        "tipo_municipio", "cod_ies", *CONTROLES,
    ]
    # Listwise deletion: se conservan sólo filas completas en todas las
    # columnas del modelo, criterio estándar en MCO.
    antes = len(df)
    df = df.dropna(subset=columnas_modelo).copy()
    _registrar(f"Listwise: {antes:,} → {len(df):,} filas con datos completos.")
    # statsmodels formula necesita tipos Python nativos para `C(...)`.
    for col in ["departamento", "tipo_municipio", "cod_ies", "periodo_ia"]:
        df[col] = df[col].astype("int64")
    return df


# =============================================================================
# 3. FÓRMULAS DE LAS TRES ESPECIFICACIONES
# =============================================================================
def _formula(dependiente: str, especificacion: str) -> str:
    """Construye la fórmula tipo R (patsy) según la especificación."""
    controles_str = " + ".join(CONTROLES)
    if especificacion == "base":
        # Treatment: nivel 0 (Bogotá) es la referencia omitida.
        return (
            f"{dependiente} ~ periodo_ia "
            f"+ C(departamento, Treatment(reference=0)) "
            f"+ distancia_bogota_km + {controles_str}"
        )
    if especificacion == "ef_ies":
        # EF por IES absorbe el departamento y la distancia.
        return (
            f"{dependiente} ~ periodo_ia + C(cod_ies) + {controles_str}"
        )
    if especificacion == "ef_mun":
        # 0 = Bogotá actúa como referencia del tipo de municipio.
        return (
            f"{dependiente} ~ periodo_ia "
            f"+ C(departamento, Treatment(reference=0)) "
            f"+ distancia_bogota_km "
            f"+ C(tipo_municipio, Treatment(reference=0)) + {controles_str}"
        )
    raise ValueError(f"Especificación desconocida: {especificacion}")


# =============================================================================
# 4. ESTIMACIÓN DE UN MODELO
# =============================================================================
def estimar_modelo(
    df: pd.DataFrame,
    dependiente: str,
    especificacion: str,
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """Ajusta el MCO con errores estándar clusterizados por IES."""
    formula = _formula(dependiente, especificacion)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        modelo = smf.ols(formula, data=df).fit(
            cov_type="cluster",
            cov_kwds={"groups": df["cod_ies"].values},
        )
    return modelo


# =============================================================================
# 5. DIAGNÓSTICOS
# =============================================================================
def _normalidad(residuos: np.ndarray) -> Tuple[str, float, float]:
    """Shapiro–Wilk si n < 5 000; Kolmogorov–Smirnov si no."""
    n = len(residuos)
    if n < 5000:
        st, p = stats.shapiro(residuos)
        return "Shapiro-Wilk", float(st), float(p)
    # KS contra la normal estandarizada con la misma media y varianza.
    residuos_z = (residuos - residuos.mean()) / residuos.std(ddof=1)
    st, p = stats.kstest(residuos_z, "norm")
    return "Kolmogorov-Smirnov", float(st), float(p)


def _vif_variables_continuas(df: pd.DataFrame) -> pd.DataFrame:
    """VIF para las variables continuas/ordinales del modelo base."""
    cols = ["periodo_ia", "distancia_bogota_km",
            "estrato", "edad", "nivel_educ_padre",
            "estu_trabaja", "estu_cabeza_familia", "jornada",
            "internet", "area_residencia", "naturaleza_ies", "genero"]
    X = sm.add_constant(df[cols].astype(float).values)
    vifs = [variance_inflation_factor(X, i + 1) for i in range(len(cols))]
    return pd.DataFrame({"variable": cols, "vif": np.round(vifs, 3)})


def diagnosticos(
    modelo: sm.regression.linear_model.RegressionResultsWrapper,
    df_modelo: pd.DataFrame,
    especificacion: str,
) -> Dict[str, object]:
    """Pruebas estándar de §8.10 sobre los residuos."""
    res = np.asarray(modelo.resid)
    fitted = np.asarray(modelo.fittedvalues)
    n = int(modelo.nobs)

    # Normalidad
    nombre_norm, est_norm, p_norm = _normalidad(res)

    # Breusch–Pagan (heterocedasticidad)
    bp_lm, bp_p, *_ = het_breuschpagan(res, modelo.model.exog)

    # Durbin–Watson (autocorrelación)
    dw = float(durbin_watson(res))

    # RESET de Ramsey (especificación)
    try:
        reset = linear_reset(modelo, power=2, use_f=True)
        reset_F, reset_p = float(reset.fvalue), float(reset.pvalue)
    except Exception:
        reset_F, reset_p = np.nan, np.nan

    diag = {
        "n_observaciones":  n,
        "r2":               round(float(modelo.rsquared), 4),
        "r2_ajustado":      round(float(modelo.rsquared_adj), 4),
        "test_normalidad":  nombre_norm,
        "stat_normalidad":  round(est_norm, 4),
        "p_normalidad":     round(p_norm, 5),
        "BP_LM":            round(float(bp_lm), 3),
        "p_BP":             round(float(bp_p), 5),
        "durbin_watson":    round(dw, 3),
        "RESET_F":          round(reset_F, 3) if not np.isnan(reset_F) else None,
        "p_RESET":          round(reset_p, 5) if not np.isnan(reset_p) else None,
    }
    if especificacion == "base":
        vif_df = _vif_variables_continuas(df_modelo)
        diag["VIF_max"] = float(vif_df["vif"].max())
        diag["VIF_supera_10"] = bool((vif_df["vif"] > 10).any())
    return diag


# =============================================================================
# 6. COLINEALIDAD GEOGRÁFICA — Versiones (a) sólo dpto, (b) sólo dist, (c) ambas
# =============================================================================
def colinealidad_geografica(df: pd.DataFrame) -> pd.DataFrame:
    """Triángulo (a)/(b)/(c) sobre el puntaje genérico (§10 del documento)."""
    controles_str = " + ".join(CONTROLES)
    versiones = {
        "a_solo_departamento": (
            f"puntaje_saberpro_generico ~ periodo_ia "
            f"+ C(departamento, Treatment(reference=0)) + {controles_str}"
        ),
        "b_solo_distancia": (
            f"puntaje_saberpro_generico ~ periodo_ia "
            f"+ distancia_bogota_km + {controles_str}"
        ),
        "c_ambas": (
            f"puntaje_saberpro_generico ~ periodo_ia "
            f"+ C(departamento, Treatment(reference=0)) "
            f"+ distancia_bogota_km + {controles_str}"
        ),
    }
    filas: List[Dict[str, object]] = []
    for nombre, formula in versiones.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            modelo = smf.ols(formula, data=df).fit(
                cov_type="cluster", cov_kwds={"groups": df["cod_ies"].values},
            )
        beta_ia = float(modelo.params["periodo_ia"])
        se_ia = float(modelo.bse["periodo_ia"])
        p_ia = float(modelo.pvalues["periodo_ia"])
        beta_dist = (float(modelo.params["distancia_bogota_km"])
                     if "distancia_bogota_km" in modelo.params else np.nan)
        p_dist = (float(modelo.pvalues["distancia_bogota_km"])
                  if "distancia_bogota_km" in modelo.params else np.nan)
        filas.append({
            "version":            nombre,
            "beta_IA":            round(beta_ia, 3),
            "se_IA":              round(se_ia, 3),
            "p_IA":               round(p_ia, 5),
            "beta_distancia":     None if pd.isna(beta_dist) else round(beta_dist, 4),
            "p_distancia":        None if pd.isna(p_dist) else round(p_dist, 5),
            "r2_ajustado":        round(float(modelo.rsquared_adj), 4),
        })
    return pd.DataFrame(filas)


# =============================================================================
# 7. EXTRACCIÓN DE LA TABLA 4 PARA UN MODELO
# =============================================================================
def tabla4_un_modelo(
    modelo: sm.regression.linear_model.RegressionResultsWrapper,
    dependiente: str,
    especificacion: str,
) -> pd.DataFrame:
    """Coeficientes + errores estándar + p para todos los términos."""
    coef = modelo.params
    se = modelo.bse
    pvals = modelo.pvalues
    tabla = pd.DataFrame({
        "dependiente":   dependiente,
        "especificacion": especificacion,
        "termino":       coef.index,
        "coef":          coef.values.round(4),
        "error_est":     se.values.round(4),
        "estadistico_t": (coef.values / se.values).round(3),
        "p_valor":       pvals.values.round(5),
    })
    return tabla


# =============================================================================
# 8. ORQUESTACIÓN DE LOS 18 MODELOS
# =============================================================================
def estimar_18_modelos(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Devuelve (tabla4 completa, diagnósticos, resumen β_IA por modelo)."""
    tabla4_partes: List[pd.DataFrame] = []
    diag_filas: List[Dict[str, object]] = []
    beta_ia_filas: List[Dict[str, object]] = []

    for dep in DEPENDIENTES:
        for spec in ESPECIFICACIONES:
            _registrar(f"  Ajustando {dep} × {spec} ...")
            modelo = estimar_modelo(df, dep, spec)
            tabla4_partes.append(tabla4_un_modelo(modelo, dep, spec))
            diag = diagnosticos(modelo, df, spec)
            diag.update({"dependiente": dep, "especificacion": spec})
            diag_filas.append(diag)
            beta_ia_filas.append({
                "dependiente":   dep,
                "especificacion": spec,
                "beta_IA":       round(float(modelo.params["periodo_ia"]), 4),
                "se_IA":         round(float(modelo.bse["periodo_ia"]), 4),
                "p_IA":          float(modelo.pvalues["periodo_ia"]),
                "n":             int(modelo.nobs),
                "r2_ajustado":   round(float(modelo.rsquared_adj), 4),
            })

    tabla4 = pd.concat(tabla4_partes, ignore_index=True)
    diag_df = pd.DataFrame(diag_filas)
    beta_ia_df = pd.DataFrame(beta_ia_filas)
    return tabla4, diag_df, beta_ia_df


# =============================================================================
# 9. CORRECCIÓN POR PRUEBAS MÚLTIPLES (Holm + BH)
# =============================================================================
def aplicar_correcciones(beta_ia_df: pd.DataFrame) -> pd.DataFrame:
    """Aplica Holm y Benjamini–Hochberg sobre los 6 β_IA, por cada spec."""
    partes: List[pd.DataFrame] = []
    for spec in ESPECIFICACIONES:
        sub = beta_ia_df[beta_ia_df["especificacion"] == spec].copy()
        if sub.empty:
            continue
        _, p_holm, _, _ = multipletests(sub["p_IA"].values, alpha=ALPHA,
                                        method="holm")
        _, p_bh, _, _ = multipletests(sub["p_IA"].values, alpha=ALPHA,
                                      method="fdr_bh")
        sub["p_IA_holm"] = np.round(p_holm, 5)
        sub["p_IA_bh"] = np.round(p_bh, 5)
        sub["sig_5pct_bruto"] = sub["p_IA"] < ALPHA
        sub["sig_5pct_holm"] = sub["p_IA_holm"] < ALPHA
        sub["sig_5pct_bh"]   = sub["p_IA_bh"] < ALPHA
        sub["p_IA"] = np.round(sub["p_IA"].astype(float), 5)
        partes.append(sub)
    return pd.concat(partes, ignore_index=True)


# =============================================================================
# 10. ORQUESTADOR PRINCIPAL
# =============================================================================
def ejecutar_regresion(
    ruta_proyecto: Optional[str] = None,
) -> Dict[str, pd.DataFrame]:
    """Pipeline completo de la Parte 2.

    Si `ruta_proyecto` es None y se está en Colab, monta Drive y usa
    `/content/drive/MyDrive/IA_EDUCACION_SUPERIOR`.
    """
    _registrar("== INICIO REGRESIÓN MCO (Parte 2) ==")
    if ruta_proyecto is None:
        montar_drive_si_aplica()
        ruta_proyecto = RUTA_DEFECTO
    df = cargar_y_preparar(ruta_proyecto)

    dir_tablas = os.path.join(ruta_proyecto, "procesados", "resultados")
    os.makedirs(dir_tablas, exist_ok=True)

    # 18 modelos
    tabla4, diag, beta_ia = estimar_18_modelos(df)
    beta_ia_corr = aplicar_correcciones(beta_ia)

    # Triángulo de colinealidad geográfica (sólo para el agregado).
    colinealidad = colinealidad_geografica(df)

    # Persistencia
    tabla4.to_csv(os.path.join(dir_tablas, "tabla4_coeficientes.csv"),
                  index=False, encoding="utf-8-sig")
    diag.to_csv(os.path.join(dir_tablas, "diagnosticos.csv"),
                index=False, encoding="utf-8-sig")
    beta_ia_corr.to_csv(os.path.join(dir_tablas, "beta_ia_resumen.csv"),
                        index=False, encoding="utf-8-sig")
    colinealidad.to_csv(os.path.join(dir_tablas, "colinealidad_geografica.csv"),
                        index=False, encoding="utf-8-sig")
    _registrar(f"  Tablas guardadas en {dir_tablas}.")
    _registrar("== FIN REGRESIÓN MCO ==")
    return {
        "tabla4":        tabla4,
        "diagnosticos":  diag,
        "beta_ia":       beta_ia_corr,
        "colinealidad":  colinealidad,
    }


# =============================================================================
# 11. CLI
# =============================================================================
def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Parte 2: regresión lineal múltiple MCO (18 modelos).",
    )
    p.add_argument("--ruta", "-r", default=None,
                   help="Carpeta del proyecto. Omitir en Colab para usar "
                        "`Mi unidad/IA_EDUCACION_SUPERIOR`.")
    return p


if __name__ == "__main__":
    args = _parser().parse_args()
    res = ejecutar_regresion(args.ruta)
    print("\n== β_IA corregidos ==")
    print(res["beta_ia"].to_string(index=False))
    print("\n== Triángulo de colinealidad geográfica ==")
    print(res["colinealidad"].to_string(index=False))
