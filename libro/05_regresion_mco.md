# Capítulo 5 — `regresion_mco.py`

> Recorrido palabra por palabra del módulo que implementa la **Parte 2**
> (Sección 8 y 10 del documento): regresión lineal múltiple por MCO.

---

## 5.1 Propósito del archivo

Estima los **18 modelos** del estudio: 6 variables dependientes (el
puntaje genérico agregado + 5 módulos) × 3 especificaciones (base, EF
IES, EF tipo de municipio). Incluye:

- Errores estándar **clusterizados** por IES.
- **Triángulo de colinealidad geográfica** (sólo `departamento`, sólo
  distancia, ambos).
- **Diagnósticos completos**: Shapiro-Wilk/KS, Breusch-Pagan, VIF,
  Durbin-Watson, RESET de Ramsey.
- **Corrección por pruebas múltiples**: Holm y Benjamini–Hochberg.
- **Dos figuras**: forest plot de β_IA y lollipop de coeficientes
  departamentales.

---

## 5.2 Imports

```python
from __future__ import annotations

import argparse
import os
import warnings
from typing import Dict, List, Optional, Tuple

from preparar_datos import (
    MODULOS_GENERICOS, _registrar,
    RUTA_DEFECTO, en_colab, instalar_dependencias_si_aplica,
    montar_drive_si_aplica,
)
instalar_dependencias_si_aplica(("scipy", "statsmodels", "matplotlib", "seaborn"))

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import (het_breuschpagan, linear_reset)
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.multitest import multipletests
from scipy import stats
```

| Importación | Uso |
|---|---|
| `import warnings` | Suprimir avisos benignos de statsmodels. |
| `statsmodels.api as sm` | `sm.add_constant`, tipos base. |
| `statsmodels.formula.api as smf` | `smf.ols(formula, data).fit(...)`. |
| `het_breuschpagan` | Heterocedasticidad. |
| `linear_reset` | RESET de Ramsey (especificación). |
| `variance_inflation_factor` | VIF (multicolinealidad). |
| `durbin_watson` | Autocorrelación. |
| `multipletests` | Holm, Benjamini–Hochberg. |
| `scipy.stats` | `stats.shapiro`, `stats.kstest` para normalidad. |

---

## 5.3 Constantes

```python
DEPENDIENTES: List[str] = [
    "puntaje_saberpro_generico",
    *MODULOS_GENERICOS,
]
CONTROLES: List[str] = [
    "estrato", "genero", "edad", "nivel_educ_padre",
    "estu_trabaja", "estu_cabeza_familia", "jornada",
    "internet", "area_residencia", "naturaleza_ies",
]
ESPECIFICACIONES: Tuple[str, ...] = ("base", "ef_ies", "ef_mun")
ALPHA: float = 0.05
```

- **`DEPENDIENTES`** — 6 variables (agregado + 5 módulos) → 6 modelos
  por especificación.
- **`CONTROLES`** — 10 covariables socioeconómicas, demográficas y
  académicas (Tabla 2 del documento).
- **`ESPECIFICACIONES`** — los 3 modelos por dependiente.

---

## 5.4 Carga y saneamiento

### `cargar_y_preparar(ruta_proyecto)`

```python
def cargar_y_preparar(ruta_proyecto):
    ruta = os.path.join(ruta_proyecto, "procesados", "df_consolidado.csv")
    if not os.path.isfile(ruta):
        raise FileNotFoundError(...)
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    columnas_modelo = [
        *DEPENDIENTES, "periodo_ia", "departamento", "distancia_bogota_km",
        "tipo_municipio", "cod_ies", *CONTROLES,
    ]
    antes = len(df)
    df = df.dropna(subset=columnas_modelo).copy()
    _registrar(f"Listwise: {antes:,} → {len(df):,} ...")
    for col in ["departamento", "tipo_municipio", "cod_ies", "periodo_ia"]:
        df[col] = df[col].astype("int64")
    return df
```

| Elemento | Significado |
|---|---|
| `*DEPENDIENTES, ..., *CONTROLES` | Unpack: desempaqueta dos listas dentro de una mayor. |
| `df.dropna(subset=cols)` | Elimina filas con NaN en CUALQUIERA de esas columnas. |
| **Listwise deletion** | Criterio estándar de MCO: sólo filas completas. |
| `.copy()` | Copia para evitar warnings. |
| `.astype("int64")` | Entero **no nullable** (sin `pd.NA`). Necesario porque `smf.ols` con `C(...)` no acepta `Int64`. |

---

## 5.5 Fórmulas de las tres especificaciones

### `_formula(dependiente, especificacion)`

```python
def _formula(dependiente, especificacion):
    controles_str = " + ".join(CONTROLES)
    if especificacion == "base":
        return (
            f"{dependiente} ~ periodo_ia "
            f"+ C(departamento, Treatment(reference=0)) "
            f"+ distancia_bogota_km + {controles_str}"
        )
    if especificacion == "ef_ies":
        return (
            f"{dependiente} ~ periodo_ia + C(cod_ies) + {controles_str}"
        )
    if especificacion == "ef_mun":
        return (
            f"{dependiente} ~ periodo_ia "
            f"+ C(departamento, Treatment(reference=0)) "
            f"+ distancia_bogota_km "
            f"+ C(tipo_municipio, Treatment(reference=0)) + {controles_str}"
        )
    raise ValueError(f"Especificación desconocida: {especificacion}")
```

| Elemento | Significado |
|---|---|
| `" + ".join(CONTROLES)` | Une la lista con ` + ` entre cada par, produciendo `"estrato + genero + edad + ..."`. |
| `f"{var} ~ x1 + x2"` | F-string que construye la fórmula. |
| `~` | Separador "depende de" en fórmulas estilo R. |
| `C(col)` | Declara `col` como categórica; patsy genera dummies automáticamente. |
| `Treatment(reference=0)` | Fija el nivel `0` como categoría base. En `departamento`, eso es Bogotá. En `tipo_municipio`, también Bogotá (código 0). |
| Spec **base** | `periodo_ia + dummies_dpto + distancia + 10 controles` |
| Spec **ef_ies** | `periodo_ia + dummies_IES + 10 controles`. Como cada IES está en un solo dpto, `departamento` y `distancia` quedan absorbidos. |
| Spec **ef_mun** | base + dummies de `tipo_municipio` (Bogotá/capital/resto). |

---

## 5.6 Estimación de un modelo

### `estimar_modelo(df, dependiente, especificacion)`

```python
def estimar_modelo(df, dependiente, especificacion):
    formula = _formula(dependiente, especificacion)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        modelo = smf.ols(formula, data=df).fit(
            cov_type="cluster",
            cov_kwds={"groups": df["cod_ies"].values},
        )
    return modelo
```

| Elemento | Significado |
|---|---|
| `with warnings.catch_warnings():` | Context manager: guarda el estado actual de warnings, lo restaura al salir. |
| `warnings.simplefilter("ignore")` | Suprime TODOS los avisos dentro del bloque. |
| `smf.ols(formula, data=df)` | Crea el modelo (todavía no estima). |
| `.fit(cov_type, cov_kwds)` | Estima por MCO. |
| `cov_type="cluster"` | Matriz de covarianza robusta + clusterizada. |
| `cov_kwds={"groups": ...}` | Identificador del cluster (IES). |
| `df["cod_ies"].values` | Array numpy con los códigos de IES (uno por observación). |

---

## 5.7 Diagnósticos

### `_normalidad(residuos)`

```python
def _normalidad(residuos):
    n = len(residuos)
    if n < 5000:
        st, p = stats.shapiro(residuos)
        return "Shapiro-Wilk", float(st), float(p)
    residuos_z = (residuos - residuos.mean()) / residuos.std(ddof=1)
    st, p = stats.kstest(residuos_z, "norm")
    return "Kolmogorov-Smirnov", float(st), float(p)
```

| Elemento | Significado |
|---|---|
| `if n < 5000:` | Umbral del documento. Shapiro-Wilk tiene buena potencia hasta ~5000. |
| `stats.shapiro(arr)` | Test de **Shapiro–Wilk**: H₀ = los datos son normales. |
| `(residuos - residuos.mean()) / residuos.std(ddof=1)` | Estandarización: media 0, desviación 1. |
| `stats.kstest(arr_z, "norm")` | **Kolmogorov–Smirnov** contra la normal estándar N(0,1). |
| `return "...", float(st), float(p)` | Retorna **tupla de 3 elementos**. |

### `_vif_variables_continuas(df)`

```python
def _vif_variables_continuas(df):
    cols = ["periodo_ia", "distancia_bogota_km",
            "estrato", "edad", "nivel_educ_padre",
            "estu_trabaja", "estu_cabeza_familia", "jornada",
            "internet", "area_residencia", "naturaleza_ies", "genero"]
    X = sm.add_constant(df[cols].astype(float).values)
    vifs = [variance_inflation_factor(X, i + 1) for i in range(len(cols))]
    return pd.DataFrame({"variable": cols, "vif": np.round(vifs, 3)})
```

| Elemento | Significado |
|---|---|
| `sm.add_constant(X)` | Añade columna de unos para el intercepto. |
| `.astype(float).values` | Convierte a array de float (statsmodels requiere numéricos). |
| `variance_inflation_factor(X, i)` | VIF de la columna i. |
| `i + 1` | Salta la columna de unos (índice 0). |
| Comprensión de lista | Calcula el VIF de cada variable de control continua. |
| `np.round(vifs, 3)` | Redondea cada elemento a 3 decimales. |

**Interpretación del VIF**:
- VIF = 1: no hay colinealidad.
- VIF entre 1 y 5: colinealidad moderada (aceptable).
- VIF > 10: colinealidad severa (problemática).

### `diagnosticos(modelo, df_modelo, especificacion)`

```python
def diagnosticos(modelo, df_modelo, especificacion):
    res = np.asarray(modelo.resid)
    fitted = np.asarray(modelo.fittedvalues)
    n = int(modelo.nobs)

    nombre_norm, est_norm, p_norm = _normalidad(res)
    bp_lm, bp_p, *_ = het_breuschpagan(res, modelo.model.exog)
    dw = float(durbin_watson(res))
    try:
        reset = linear_reset(modelo, power=2, use_f=True)
        reset_F, reset_p = float(reset.fvalue), float(reset.pvalue)
    except Exception:
        reset_F, reset_p = np.nan, np.nan

    diag = {
        "n_observaciones": n,
        "r2": round(float(modelo.rsquared), 4),
        "r2_ajustado": round(float(modelo.rsquared_adj), 4),
        ...
    }
    if especificacion == "base":
        vif_df = _vif_variables_continuas(df_modelo)
        diag["VIF_max"] = float(vif_df["vif"].max())
        diag["VIF_supera_10"] = bool((vif_df["vif"] > 10).any())
    return diag
```

| Elemento | Significado |
|---|---|
| `np.asarray(x)` | Convierte a array numpy sin copiar si ya lo es. |
| `modelo.resid` | Residuos (y - ŷ). |
| `modelo.fittedvalues` | Valores predichos. |
| `modelo.nobs` | Número de observaciones. |
| `het_breuschpagan(res, X)` | Devuelve `(LM, p, F, p_F)`. Sólo guardamos los dos primeros. |
| `*_` | Captura los demás valores en una lista anónima (4 elementos retornados, 2 asignados, 2 ignorados). |
| `linear_reset(modelo, power=2, use_f=True)` | RESET de Ramsey: añade `ŷ²` y testea si es significativo. `use_f=True` retorna estadístico F. |
| `try / except Exception` | RESET puede fallar (matrices singulares); capturamos cualquier error. |
| `modelo.rsquared`, `modelo.rsquared_adj` | R² y R² ajustado. |
| `if especificacion == "base":` | Sólo calcula VIF en la spec base (es la que tiene todas las continuas + dummies). |
| `(vif_df["vif"] > 10).any()` | Máscara > 10, `.any()` = True si **alguno** lo cumple. |
| `bool(...)` | Conversión explícita (numpy bool → Python bool). |

---

## 5.8 Triángulo de colinealidad geográfica

### `colinealidad_geografica(df)`

```python
def colinealidad_geografica(df):
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
    filas = []
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
            "version": nombre,
            "beta_IA": round(beta_ia, 3),
            ...
        })
    return pd.DataFrame(filas)
```

| Elemento | Significado |
|---|---|
| Diccionario `versiones` | Tres modelos con diferentes términos geográficos. |
| `modelo.params["periodo_ia"]` | Coeficiente estimado de `periodo_ia`. |
| `modelo.bse["periodo_ia"]` | Error estándar. |
| `modelo.pvalues["periodo_ia"]` | p-valor. |
| Ternario `if "x" in modelo.params else np.nan` | Defensivo: no todas las versiones tienen `distancia_bogota_km`. |
| `for nombre, formula in versiones.items()` | Itera pares clave–valor del dict. |

**Por qué importa**: §10 del documento advierte que `departamento` y
`distancia_bogota_km` están altamente correlacionadas (cada dpto tiene
una sola distancia). Las tres versiones diagnostican cuánto cambia β_IA
según qué instrumento geográfico se incluya.

---

## 5.9 Tabla 4 por modelo

### `tabla4_un_modelo(modelo, dependiente, especificacion)`

```python
def tabla4_un_modelo(modelo, dependiente, especificacion):
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
```

| Elemento | Significado |
|---|---|
| `modelo.params` | Series con coeficientes indexados por nombre de término. |
| `coef.index` | Nombres de los términos del modelo. |
| `coef.values` | Array numpy con los valores. |
| `(coef.values / se.values).round(3)` | Estadístico t = coef / SE. División vectorial. |
| Constante en columna | Pandas difunde el escalar a todas las filas. |

---

## 5.10 Figuras (forest plot y lollipop)

### `_estilo_pub()`

Análogo a `_aplicar_estilo()` del módulo descriptivo (cap. 4).

### `figura_forest_beta_ia(beta_ia_df, ruta_out)`

```python
def figura_forest_beta_ia(beta_ia_df, ruta_out):
    _estilo_pub()
    etiquetas_dep = {
        "puntaje_saberpro_generico": "Genérico\n(agregado)",
        "punt_lectura_critica":      "Lectura\ncrítica",
        ...
    }
    etiquetas_spec = {"base": "Base", "ef_ies": "EF IES",
                      "ef_mun": "EF tipo de municipio"}
    paleta = {"Base": "#3A6FB0", "EF IES": "#4FA869",
              "EF tipo de municipio": "#E07A3F"}

    d = beta_ia_df.copy()
    d["dep_label"] = d["dependiente"].map(etiquetas_dep)
    d["spec_label"] = d["especificacion"].map(etiquetas_spec)
    d["ci_low"]  = d["beta_IA"] - 1.96 * d["se_IA"]
    d["ci_high"] = d["beta_IA"] + 1.96 * d["se_IA"]

    deps = list(etiquetas_dep.values())
    specs = list(etiquetas_spec.values())
    offset = 0.26

    fig, ax = plt.subplots(figsize=(11, 7))
    for i, spec in enumerate(specs):
        sub = (d[d["spec_label"] == spec]
               .set_index("dep_label").reindex(deps))
        y = np.arange(len(deps)) + (i - 1) * offset
        ax.errorbar(
            sub["beta_IA"].values, y,
            xerr=1.96 * sub["se_IA"].values,
            fmt="o", markersize=8, capsize=4,
            color=paleta[spec], ecolor=paleta[spec],
            alpha=0.9, linewidth=1.8, label=spec,
        )

    ax.axvline(0, color="#cc3a3a", linewidth=1.0,
               linestyle="--", alpha=0.55, zorder=0)
    ax.set_yticks(np.arange(len(deps)))
    ax.set_yticklabels(deps, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Coeficiente β_IA (puntos Saber Pro)  —  IC 95%")
    ax.set_title("Asociación condicional del período de IA Gen con el puntaje Saber Pro")
    ax.legend(title="Especificación", loc="best")
    ax.grid(True, axis="x", linestyle=":", alpha=0.55)
    ...
```

| Elemento | Significado |
|---|---|
| `1.96 * se` | IC 95 % aproximado bajo normalidad asintótica (n grande). |
| `enumerate(specs)` | Itera `(índice, valor)`. |
| `sub.set_index("dep_label").reindex(deps)` | Asegura que las dependientes estén en el orden definido. |
| `np.arange(len(deps)) + (i-1)*offset` | Posiciones verticales **descentradas** por cada especificación (para no solapar). |
| `ax.errorbar(x, y, xerr, fmt="o", capsize=4)` | Barras de error horizontales con marcador circular. |
| `ax.axvline(0)` | Línea vertical en x=0 (línea de no-efecto). |
| `ax.invert_yaxis()` | Invierte el eje y para que el primer elemento quede arriba. |

### `figura_coeficientes_departamento(tabla4_df, ruta_out)`

```python
def figura_coeficientes_departamento(tabla4_df, ruta_out):
    _estilo_pub()
    from preparar_datos import DEPARTAMENTOS

    sub = tabla4_df[
        (tabla4_df["dependiente"] == "puntaje_saberpro_generico")
        & (tabla4_df["especificacion"] == "base")
        & (tabla4_df["termino"].astype(str).str.contains("departamento"))
    ].copy()
    sub["cod"] = (
        sub["termino"].astype(str)
        .str.extract(r"\[T\.(\d+)\]")[0]
        .astype(float)
    )
    sub = sub.dropna(subset=["cod"]).copy()
    cod_a_nombre = {c: n.title() for n, (c, _) in DEPARTAMENTOS.items()}
    sub["depto"] = sub["cod"].astype(int).map(cod_a_nombre)
    sub["ci_low"]  = sub["coef"] - 1.96 * sub["error_est"]
    sub["ci_high"] = sub["coef"] + 1.96 * sub["error_est"]
    sub["sig"] = sub["p_valor"] < 0.05
    sub = sub.sort_values("coef")

    fig, ax = plt.subplots(figsize=(9, max(8, 0.30 * len(sub))))
    for _, r in sub.iterrows():
        color = "#3A6FB0" if r["coef"] >= 0 else "#E07A3F"
        alpha_pt = 1.0 if r["sig"] else 0.45
        ax.hlines(r["depto"], r["ci_low"], r["ci_high"],
                  color=color, alpha=alpha_pt * 0.55, linewidth=2)
        ax.scatter(r["coef"], r["depto"], color=color,
                   s=85 if r["sig"] else 50, alpha=alpha_pt,
                   edgecolor="white", linewidth=1.1, zorder=10)
    ax.axvline(0, color="black", linewidth=0.9,
               linestyle="-", alpha=0.55, zorder=0)
    ...
```

| Elemento | Significado |
|---|---|
| Import perezoso `from preparar_datos import DEPARTAMENTOS` | Evita una dependencia cíclica si se importan en otro orden. |
| `tabla4_df[mask1 & mask2 & mask3]` | Filtro compuesto. |
| `mask3 = ...str.contains("departamento")` | Selecciona términos como `C(departamento, ...)[T.5]`. |
| `.str.extract(r"\[T\.(\d+)\]")[0]` | Regex que captura el dígito del código entre `[T.` y `]`. `[0]` toma la primera coincidencia. |
| `{c: n.title() for n, (c, _) in DEPARTAMENTOS.items()}` | Mapeo inverso código → nombre legible. |
| `.title()` | Capitaliza primera letra. |
| `figsize=(9, max(8, 0.30 * len(sub)))` | Alto adaptativo según número de dptos. |
| `ax.hlines(y, xmin, xmax)` | Línea horizontal para la barra de IC. |
| `s=85 if r["sig"] else 50` | Tamaño mayor para puntos significativos. |
| `alpha_pt = 1.0 if r["sig"] else 0.45` | Opacidad mayor para significativos. |

---

## 5.11 Orquestación de los 18 modelos

### `estimar_18_modelos(df)`

```python
def estimar_18_modelos(df):
    tabla4_partes = []
    diag_filas = []
    beta_ia_filas = []

    for dep in DEPENDIENTES:
        for spec in ESPECIFICACIONES:
            _registrar(f"  Ajustando {dep} × {spec} ...")
            modelo = estimar_modelo(df, dep, spec)
            tabla4_partes.append(tabla4_un_modelo(modelo, dep, spec))
            diag = diagnosticos(modelo, df, spec)
            diag.update({"dependiente": dep, "especificacion": spec})
            diag_filas.append(diag)
            beta_ia_filas.append({
                "dependiente": dep, "especificacion": spec,
                "beta_IA": round(float(modelo.params["periodo_ia"]), 4),
                "se_IA":   round(float(modelo.bse["periodo_ia"]), 4),
                "p_IA":    float(modelo.pvalues["periodo_ia"]),
                "n":       int(modelo.nobs),
                "r2_ajustado": round(float(modelo.rsquared_adj), 4),
            })

    tabla4 = pd.concat(tabla4_partes, ignore_index=True)
    diag_df = pd.DataFrame(diag_filas)
    beta_ia_df = pd.DataFrame(beta_ia_filas)
    return tabla4, diag_df, beta_ia_df
```

| Elemento | Significado |
|---|---|
| Bucle anidado | `6 × 3 = 18` iteraciones. |
| `diag.update({...})` | Añade dos claves al dict diag. |
| `pd.concat([dfs], ignore_index=True)` | Apila los 18 dataframes de coeficientes. |
| Retorno triple | `(tabla4, diag_df, beta_ia_df)`. |

---

## 5.12 Corrección por pruebas múltiples

### `aplicar_correcciones(beta_ia_df)`

```python
def aplicar_correcciones(beta_ia_df):
    partes = []
    for spec in ESPECIFICACIONES:
        sub = beta_ia_df[beta_ia_df["especificacion"] == spec].copy()
        if sub.empty:
            continue
        _, p_holm, _, _ = multipletests(sub["p_IA"].values, alpha=ALPHA,
                                        method="holm")
        _, p_bh, _, _ = multipletests(sub["p_IA"].values, alpha=ALPHA,
                                      method="fdr_bh")
        sub["p_IA_holm"] = np.round(p_holm, 5)
        sub["p_IA_bh"]   = np.round(p_bh, 5)
        sub["sig_5pct_bruto"] = sub["p_IA"] < ALPHA
        sub["sig_5pct_holm"]  = sub["p_IA_holm"] < ALPHA
        sub["sig_5pct_bh"]    = sub["p_IA_bh"] < ALPHA
        sub["p_IA"] = np.round(sub["p_IA"].astype(float), 5)
        partes.append(sub)
    return pd.concat(partes, ignore_index=True)
```

| Elemento | Significado |
|---|---|
| `multipletests(pvals, alpha, method)` | Retorna `(rechazos, p_ajustados, alfa_sidak, alfa_bonf)`. |
| `_, p_holm, _, _ = ...` | Desempaquetado: sólo nos interesa el segundo. |
| `method="holm"` | Controla FWER (probabilidad de **algún** falso positivo). |
| `method="fdr_bh"` | Controla FDR (proporción esperada de falsos positivos entre los rechazos). |
| `sub["p_IA"] < ALPHA` | Comparación vectorial → columna booleana. |

**Cuándo usar Holm vs BH**:
- **Holm**: si te importa NO tener ningún falso positivo (conservador).
- **BH**: si aceptas que un cierto porcentaje de tus rechazos sean
  falsos positivos pero quieres más potencia (estándar en biomédica).

---

## 5.13 Orquestador

### `ejecutar_regresion(ruta_proyecto)`

```python
def ejecutar_regresion(ruta_proyecto: Optional[str] = None):
    _registrar("== INICIO REGRESIÓN MCO (Parte 2) ==")
    if ruta_proyecto is None:
        montar_drive_si_aplica()
        ruta_proyecto = RUTA_DEFECTO
    df = cargar_y_preparar(ruta_proyecto)

    dir_tablas  = os.path.join(ruta_proyecto, "procesados", "resultados")
    dir_figuras = os.path.join(ruta_proyecto, "procesados", "figuras")
    os.makedirs(dir_tablas, exist_ok=True)
    os.makedirs(dir_figuras, exist_ok=True)

    tabla4, diag, beta_ia = estimar_18_modelos(df)
    beta_ia_corr = aplicar_correcciones(beta_ia)
    colinealidad = colinealidad_geografica(df)

    tabla4.to_csv(os.path.join(dir_tablas, "tabla4_coeficientes.csv"),
                  index=False, encoding="utf-8-sig")
    diag.to_csv(os.path.join(dir_tablas, "diagnosticos.csv"),
                index=False, encoding="utf-8-sig")
    beta_ia_corr.to_csv(os.path.join(dir_tablas, "beta_ia_resumen.csv"),
                        index=False, encoding="utf-8-sig")
    colinealidad.to_csv(os.path.join(dir_tablas, "colinealidad_geografica.csv"),
                        index=False, encoding="utf-8-sig")

    figura_forest_beta_ia(
        beta_ia_corr,
        os.path.join(dir_figuras, "fig_07_forest_beta_ia.png"),
    )
    figura_coeficientes_departamento(
        tabla4,
        os.path.join(dir_figuras, "fig_08_coef_departamento.png"),
    )
    return {
        "tabla4":       tabla4,
        "diagnosticos": diag,
        "beta_ia":      beta_ia_corr,
        "colinealidad": colinealidad,
    }
```

Estructura idéntica al orquestador del módulo descriptivo (cap. 4).

---

## 5.14 CLI

```python
def _parser():
    p = argparse.ArgumentParser(description="...")
    p.add_argument("--ruta", "-r", default=None, help="...")
    return p

if __name__ == "__main__":
    args = _parser().parse_args()
    res = ejecutar_regresion(args.ruta)
    print(res["beta_ia"].to_string(index=False))
    print(res["colinealidad"].to_string(index=False))
```

---

## 5.15 Recapitulación

Al terminar este capítulo deberías poder:

1. Explicar cada **especificación** y por qué `departamento` se absorbe
   con EF IES.
2. Interpretar el **triángulo de colinealidad**: cuándo β_IA cambia
   drásticamente entre versiones, hay colinealidad.
3. Distinguir entre **Holm** (FWER) y **Benjamini–Hochberg** (FDR).
4. Leer el **forest plot**: si la barra cruza el 0, no hay
   significancia al 5 %.

Pasa al [Capítulo 6 — `main.py`](./06_main.md) para conocer el
orquestador del proyecto.
