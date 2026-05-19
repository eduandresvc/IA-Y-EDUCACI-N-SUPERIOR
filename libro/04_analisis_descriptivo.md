# Capítulo 4 — `analisis_descriptivo.py`

> Recorrido palabra por palabra del módulo que implementa la **Parte 1**
> de la investigación (Sección 9 del documento): comparación bivariada
> entre las cohortes 2021–2022 y 2023–2024.

---

## 4.1 Propósito del archivo

Este módulo lee el `df_consolidado.csv` que produce
`preparar_datos.py` y:

1. Compara las dos cohortes para cada variable relevante:
   - **Continuas / ordinales:** media ± DE, n, t de Welch y
     Mann–Whitney.
   - **Dicotómicas:** proporción, diferencia en puntos porcentuales y
     χ² de Pearson con corrección de Yates.
2. Construye la **Tabla 3** del documento y una tabla descriptiva por
   departamento.
3. Genera **seis figuras de calidad publicación** (boxplot, violines
   por módulo, histograma, boxplot por departamento, heatmap y
   dispersión distancia↔puntaje).
4. Persiste todo en `procesados/resultados/` y `procesados/figuras/`.

---

## 4.2 Imports

```python
from __future__ import annotations

import argparse
import os
from typing import Dict, List, Optional, Tuple

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
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
```

| Elemento | Significado |
|---|---|
| `from __future__ import annotations` | Anotaciones diferidas (cap. 1). |
| `from preparar_datos import (...)` | Reutiliza constantes y helpers del primer módulo. |
| `instalar_dependencias_si_aplica((...))` | Bootstrap perezoso: en Colab instala scipy/matplotlib/seaborn antes de importarlos. **Se llama ANTES de los imports pesados.** |
| `from scipy import stats` | Acceso a `stats.ttest_ind`, `stats.mannwhitneyu`, `stats.chi2_contingency`. |
| `matplotlib.use("Agg")` | Backend sin GUI (válido en servidores y Colab). **Debe llamarse antes de importar `pyplot`.** |
| `import matplotlib.pyplot as plt` | Interfaz pyplot estilo MATLAB. |
| `import seaborn as sns` | Construido sobre matplotlib; gráficos estadísticos con tema coherente. |

---

## 4.3 Tema visual global

### `PALETA_COHORTES` y `NOTA_FUENTE`

```python
PALETA_COHORTES: Dict[str, str] = {
    "2021-2022 (pre-IA)":   "#3A6FB0",   # azul sobrio
    "2023-2024 (IA Gen)":   "#E07A3F",   # naranja cálido
}
NOTA_FUENTE: str = "Fuente: DataICFES (2021-2024). Elaboración propia."
```

- **Diccionario etiqueta → color hex.** Garantiza paleta consistente
  entre figuras.
- **`#3A6FB0`** y **`#E07A3F`** son códigos hexadecimales de color
  RGB: `#RRGGBB`. `3A` = 58 (azul oscuro), `6F` = 111 (verde medio),
  `B0` = 176 (azul alto). Resultado: azul sobrio.

### `_aplicar_estilo()`

```python
def _aplicar_estilo() -> None:
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
```

| Elemento | Significado |
|---|---|
| `sns.set_theme(style="whitegrid", ...)` | Aplica un tema de seaborn. `whitegrid` = fondo blanco con cuadrícula gris. |
| `context="paper"` | Tamaños tipográficos pequeños, óptimos para publicación impresa. |
| `font_scale=1.1` | Multiplica todos los tamaños por 1.1. |
| `plt.rcParams.update({...})` | Modifica el diccionario global de configuración de matplotlib. |
| `"figure.facecolor": "white"` | Fondo blanco fuera del eje. |
| `"axes.edgecolor": "#444"` | Color de los bordes del eje (gris oscuro). |
| `"axes.titleweight": "bold"` | Títulos en negrita. |
| `"grid.linestyle": ":"` | Cuadrícula con puntos. |
| `"grid.alpha": 0.55` | Cuadrícula semitransparente. |

---

## 4.4 Constantes — variables a comparar

```python
VARS_CONTINUAS: List[str] = [
    "puntaje_saberpro_generico",
    *MODULOS_GENERICOS,
    "estrato", "edad", "nivel_educ_padre",
    "distancia_bogota_km",
]
VARS_DICOTOMICAS: List[str] = [
    "genero", "estu_trabaja", "estu_cabeza_familia",
    "jornada", "internet", "area_residencia",
    "naturaleza_ies",
]
ALPHA: float = 0.05
```

- **`*MODULOS_GENERICOS`** — *unpack*: desempaqueta la lista
  importada de `preparar_datos.py` dentro del literal. Resultado:
  `[puntaje_saberpro_generico, punt_lectura_critica, ...]`.
- **`VARS_CONTINUAS`** — variables que se prueban con t-Welch y
  Mann–Whitney.
- **`VARS_DICOTOMICAS`** — variables que se prueban con χ². Aunque
  algunas (estrato, nivel_educ_padre) son ordinales, se tratan como
  continuas en el reporte.
- **`ALPHA = 0.05`** — umbral de significancia estadística estándar.

---

## 4.5 Carga del consolidado

### `cargar_consolidado(ruta_proyecto)`

```python
def cargar_consolidado(ruta_proyecto: str) -> pd.DataFrame:
    ruta = os.path.join(ruta_proyecto, "procesados", "df_consolidado.csv")
    if not os.path.isfile(ruta):
        raise FileNotFoundError(...)
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    _registrar(f"Consolidado cargado: {len(df):,} filas × {df.shape[1]} cols.")
    return df
```

| Elemento | Significado |
|---|---|
| `os.path.join(ruta, "procesados", "df_consolidado.csv")` | Combina componentes de ruta. |
| `os.path.isfile(ruta)` | `True` si existe y es archivo. |
| `raise FileNotFoundError(...)` | Mensaje claro si no se ejecutó preparar_datos. |
| `pd.read_csv(ruta, encoding="utf-8-sig")` | Lee CSV; `utf-8-sig` decodifica el BOM si lo tiene. |

---

## 4.6 Pruebas estadísticas

### `_fmt_p(p)` — formateo de p-valores

```python
def _fmt_p(p: float) -> str:
    if pd.isna(p):
        return "NA"
    return "< 0.001" if p < 0.001 else f"{p:.3f}"
```

| Elemento | Significado |
|---|---|
| `pd.isna(p)` | True si `p` es faltante. |
| Ternario `"< 0.001" if p < 0.001 else f"{p:.3f}"` | Convención: p-valores muy pequeños se muestran como "< 0.001". |
| `f"{p:.3f}"` | F-string con formato: 3 decimales. |

### `_resumen_continua(serie_0, serie_1)`

```python
def _resumen_continua(serie_0, serie_1):
    s0 = pd.to_numeric(serie_0, errors="coerce").dropna()
    s1 = pd.to_numeric(serie_1, errors="coerce").dropna()
    if len(s0) < 2 or len(s1) < 2:
        return {"n_0": len(s0), ...}
    t, p_t = stats.ttest_ind(s0, s1, equal_var=False, nan_policy="omit")
    u, p_mw = stats.mannwhitneyu(s0, s1, alternative="two-sided")
    return {
        "n_0": int(len(s0)),  "n_1": int(len(s1)),
        "media_0": float(s0.mean()), "media_1": float(s1.mean()),
        "sd_0": float(s0.std(ddof=1)), "sd_1": float(s1.std(ddof=1)),
        "delta": float(s1.mean() - s0.mean()),
        "t_welch": float(t), "p_t": float(p_t),
        "U_mw": float(u), "p_mw": float(p_mw),
    }
```

| Elemento | Significado |
|---|---|
| `pd.to_numeric(..., errors="coerce")` | Conversión defensiva: no-numéricos → NaN. |
| `.dropna()` | Elimina los NaN. |
| `if len(s0) < 2 or len(s1) < 2` | Defensivo: las pruebas requieren al menos 2 observaciones por grupo. |
| `stats.ttest_ind(a, b, equal_var=False)` | **t de Welch** (no asume varianzas iguales). Retorna `(t, p)`. |
| `nan_policy="omit"` | Ignora NaN en el cálculo. |
| `stats.mannwhitneyu(a, b, alternative="two-sided")` | **Mann–Whitney U**: no paramétrica, robusta a no-normalidad. |
| `s0.std(ddof=1)` | Desviación estándar **muestral** (denominador n-1). `ddof=1` es estándar en estadística. |
| `int(...)`, `float(...)` | Conversión explícita para evitar tipos numpy en el JSON resultante. |

### `_resumen_dicotomica(serie_0, serie_1)`

```python
def _resumen_dicotomica(serie_0, serie_1):
    s0 = pd.to_numeric(serie_0, errors="coerce").dropna()
    s1 = pd.to_numeric(serie_1, errors="coerce").dropna()
    if len(s0) < 2 or len(s1) < 2:
        return {...}
    tabla = pd.crosstab(
        pd.concat([pd.Series(0, index=s0.index), pd.Series(1, index=s1.index)]),
        pd.concat([s0, s1]),
    )
    chi2, p, *_ = stats.chi2_contingency(tabla, correction=True)
    return {
        "n_0": int(len(s0)),  "n_1": int(len(s1)),
        "prop_0": float(s0.mean()), "prop_1": float(s1.mean()),
        "delta_pp": float((s1.mean() - s0.mean()) * 100),
        "chi2": float(chi2),  "p_chi2": float(p),
    }
```

| Elemento | Significado |
|---|---|
| `pd.Series(0, index=s0.index)` | Crea una Series rellena con ceros con un índice dado. |
| `pd.concat([s0_zeros, s1_ones])` | Apila las dos cohortes etiquetadas (0/1). |
| `pd.crosstab(a, b)` | Tabla de contingencia (frecuencias) entre dos variables. |
| `stats.chi2_contingency(tabla, correction=True)` | **χ² de Pearson** con **corrección de Yates** en 2×2. |
| `chi2, p, *_ = ...` | Desempaquetado: `*_` captura el resto en una lista anónima. |
| `s0.mean()` | Para una serie 0/1, la media = proporción de unos. |
| `* 100` | Convierte proporción en puntos porcentuales. |

### `tabla3_descriptivo(df)`

```python
def tabla3_descriptivo(df):
    pre = df[df["periodo_ia"] == 0]
    pos = df[df["periodo_ia"] == 1]
    filas: List[Dict[str, object]] = []

    for var in VARS_CONTINUAS:
        if var not in df.columns:
            continue
        r = _resumen_continua(pre[var], pos[var])
        filas.append({
            "variable": var, "tipo": "continua/ordinal",
            "n_2021_22": r["n_0"], ...
        })

    for var in VARS_DICOTOMICAS:
        if var not in df.columns:
            continue
        r = _resumen_dicotomica(pre[var], pos[var])
        filas.append({...})

    return pd.DataFrame(filas)
```

| Elemento | Significado |
|---|---|
| `df[df["periodo_ia"] == 0]` | Filtra filas de la cohorte pre-IA. |
| `for var in VARS_CONTINUAS:` | Bucle sobre cada variable. |
| `if var not in df.columns: continue` | Defensivo: si la variable no existe, salta. |
| `filas.append({...})` | Construcción incremental de una lista de dicts. |
| `pd.DataFrame(filas)` | Convierte la lista de dicts en DataFrame. |

---

## 4.7 Tabla por departamento

### `tabla_por_departamento(df)`

```python
def tabla_por_departamento(df):
    cols_valor = ["puntaje_saberpro_generico", *MODULOS_GENERICOS]
    grupo = (df.groupby(["departamento", "departamento_nombre", "periodo_ia"])
               [cols_valor].mean().round(2).reset_index())
    pivot = grupo.pivot_table(
        index=["departamento", "departamento_nombre"],
        columns="periodo_ia", values=cols_valor,
    )
    pivot.columns = [f"{var}__periodo_{p}" for var, p in pivot.columns]
    pivot = pivot.reset_index().sort_values("departamento")
    return pivot
```

| Elemento | Significado |
|---|---|
| `.groupby([col1, col2, col3])` | Agrupa por varias columnas. |
| `[cols_valor]` | Selecciona las columnas a agregar. |
| `.mean()` | Promedio de cada grupo. |
| `.round(2)` | Redondea a 2 decimales. |
| `.reset_index()` | Convierte el MultiIndex de grupos en columnas normales. |
| `pivot_table(index, columns, values)` | Reordena a formato ancho: una fila por departamento, columnas por (variable, cohorte). |
| `pivot.columns` | Aquí es un MultiIndex con tuplas `(variable, periodo)`. |
| `[f"{var}__periodo_{p}" for var, p in pivot.columns]` | Aplana el MultiIndex en nombres simples como `puntaje_saberpro_generico__periodo_0`. |
| `.sort_values("departamento")` | Ordena por código de departamento. |

---

## 4.8 Figuras

### `_anotar_fuente(fig, texto)`

```python
def _anotar_fuente(fig, texto=NOTA_FUENTE):
    fig.text(0.995, 0.005, texto,
             ha="right", va="bottom",
             fontsize=8.2, style="italic", color="#666")
```

| Elemento | Significado |
|---|---|
| `fig.text(x, y, texto, ...)` | Añade texto a la figura en coordenadas (0..1, 0..1) relativas al lienzo. |
| `ha="right"` | Alineación horizontal a la derecha. |
| `va="bottom"` | Alineación vertical abajo. |
| `style="italic"` | Cursiva. |
| `color="#666"` | Gris medio. |

### Patrón general de las funciones de figura

Cada función sigue este patrón:

```python
def figura_X(df, ruta_out):
    _aplicar_estilo()
    # Preparar datos
    ...
    fig, ax = plt.subplots(figsize=(ancho, alto))
    # Pintar con sns o ax
    ...
    # Títulos y etiquetas
    ax.set_title("...")
    ax.set_xlabel("...")
    ax.set_ylabel("...")
    # Anotación de fuente
    _anotar_fuente(fig)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=200, bbox_inches="tight")
    plt.close(fig)
```

### `figura_boxplot_periodo(df, ruta_out)` — violín + box

```python
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

medias = d.groupby("Cohorte", observed=True)["puntaje_saberpro_generico"].mean()
for i, (_, mu) in enumerate(medias.items()):
    ax.scatter(i, mu, marker="D", s=70, color="white",
               edgecolor="black", linewidth=1.5, zorder=10)

t, p = stats.ttest_ind(s0, s1, equal_var=False)
ax.text(0.5, 0.97, f"...{t:.2f}, {p_str}, ...",
        transform=ax.transAxes, ha="center", va="top",
        fontsize=9.5, style="italic", color="#333",
        bbox=dict(boxstyle="round,pad=0.45",
                  fc="white", ec="#bbb", lw=0.7, alpha=0.95))
```

| Elemento | Significado |
|---|---|
| `sns.violinplot(data, x, y, hue, ...)` | Dibuja un violín. `inner=None` quita el boxplot interior. |
| `sns.boxplot(width=0.18, fliersize=0)` | Box estrecho superpuesto, sin outliers visibles. |
| `legend=False` | No mostrar leyenda (el `hue` la generaría). |
| `enumerate(medias.items())` | Itera pares `(índice, (clave, valor))`. |
| `(_, mu)` | Desempaqueta `(clave, valor)`, ignorando la clave. |
| `ax.scatter(i, mu, marker="D", zorder=10)` | Diamante blanco para marcar la media. `zorder=10` lo dibuja por encima. |
| `transform=ax.transAxes` | Coordenadas relativas al axes (0..1), no a los datos. |
| `bbox=dict(boxstyle="round,pad=0.45", ...)` | Caja redondeada alrededor del texto. |

### `figura_boxplot_departamento(df, ruta_out)`

```python
orden = (
    df.groupby("departamento_nombre")["puntaje_saberpro_generico"]
    .median().sort_values(ascending=False).index.tolist()
)
sns.boxplot(data=d, x="departamento_nombre", y="puntaje_saberpro_generico",
            hue="Cohorte", order=orden, ...)

if "BOGOTA" in orden:
    ax.axvline(orden.index("BOGOTA"), color="#cc3a3a",
               linewidth=1.0, linestyle="--", alpha=0.45, zorder=0)
```

| Elemento | Significado |
|---|---|
| `.index.tolist()` | Convierte el índice (lista de nombres de dpto) a lista Python. |
| `order=orden` | Fija el orden de las categorías en el eje x. |
| `ax.axvline(x, color, linestyle)` | Línea vertical en `x`. |
| `orden.index("BOGOTA")` | Posición (entera) de "BOGOTA" en la lista. |

### `figura_histograma_cohortes(df, ruta_out)`

```python
sns.histplot(
    data=d, x="puntaje_saberpro_generico", hue="Cohorte",
    bins=50, palette=PALETA_COHORTES, alpha=0.55, kde=True,
    edgecolor="white", linewidth=0.5, ax=ax,
)
medias = d.groupby("Cohorte", observed=True)["puntaje_saberpro_generico"].mean()
for cohorte, mu in medias.items():
    color = PALETA_COHORTES[cohorte]
    ax.axvline(mu, color=color, linestyle="--", linewidth=1.6, alpha=0.85)
    ax.text(mu, ax.get_ylim()[1] * 0.95, f"  μ = {mu:.1f}",
            color=color, fontweight="bold", fontsize=9.5,
            rotation=90, va="top", ha="left")
```

| Elemento | Significado |
|---|---|
| `sns.histplot(kde=True)` | Histograma + estimación KDE superpuesta. |
| `bins=50` | Número de barras. |
| `ax.get_ylim()` | Devuelve `(min, max)` del eje y. |
| `[1] * 0.95` | 95 % del máximo (posiciona la etiqueta cerca del techo). |
| `rotation=90` | Texto vertical. |

### `figura_dispersion_distancia(df, ruta_out)`

```python
agg = (
    df.groupby(["departamento_nombre", "distancia_bogota_km"])
    .agg(puntaje_medio=("puntaje_saberpro_generico", "mean"),
         n_estudiantes=("puntaje_saberpro_generico", "count"))
    .reset_index()
)
tamanos = (agg["n_estudiantes"] / agg["n_estudiantes"].max() * 600 + 50).values
sc = ax.scatter(
    agg["distancia_bogota_km"], agg["puntaje_medio"],
    s=tamanos, c=agg["distancia_bogota_km"],
    cmap="viridis_r", alpha=0.78,
    edgecolor="white", linewidth=1.2, zorder=3,
)

coef = np.polyfit(x, y, deg=1, w=np.sqrt(agg["n_estudiantes"].values))
xs = np.linspace(0, x.max() * 1.05, 100)
ax.plot(xs, np.polyval(coef, xs), linestyle="--", color="#222", ...)

cbar = fig.colorbar(sc, ax=ax, shrink=0.75, pad=0.02)
cbar.set_label("Distancia (km)", fontsize=9.5)
```

| Elemento | Significado |
|---|---|
| `.agg(nombre=(col, "mean"))` | Sintaxis "named aggregation" de pandas. |
| `tamanos` | Tamaños proporcionales al `n` de estudiantes (escalados 50-650). |
| `s=tamanos` | Tamaño del marcador en `scatter`. |
| `c=valor`, `cmap="viridis_r"` | Color por valor + mapa de color. `_r` = reversed. |
| `np.polyfit(x, y, deg=1, w=...)` | OLS **ponderada** por `w`. Aquí pesos = √n para reflejar precisión. |
| `np.linspace(0, x.max()*1.05, 100)` | 100 puntos equidistantes. |
| `np.polyval(coef, xs)` | Evalúa el polinomio. |
| `fig.colorbar(scatter, ax)` | Barra de color adjunta. |

### Anotación selectiva de departamentos

```python
destacados = {"BOGOTA", "ANTIOQUIA", "VALLE", "HUILA", ...}
for _, r in agg.iterrows():
    if r["departamento_nombre"] in destacados:
        ax.annotate(
            r["departamento_nombre"].title()[:11],
            (r["distancia_bogota_km"], r["puntaje_medio"]),
            xytext=(8, 8), textcoords="offset points",
            fontsize=8.6, fontweight="bold", color="#222",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.75),
        )
```

| Elemento | Significado |
|---|---|
| `{"a", "b", ...}` | Literal de **conjunto** (set). |
| `agg.iterrows()` | Iterador `(índice, Series)` por fila del DataFrame. |
| `_` | Convención: "índice que no uso". |
| `.title()` | Capitaliza primera letra de cada palabra. |
| `[:11]` | Slice: los primeros 11 caracteres. |
| `xytext=(8, 8), textcoords="offset points"` | Posiciona el texto 8 puntos a la derecha y arriba del punto. |
| `bbox=dict(...)` | Caja decorativa alrededor del texto. |

### `figura_heatmap_dpto_cohorte(df, ruta_out)`

```python
pivot = (
    df.pivot_table(values="puntaje_saberpro_generico",
                   index="departamento_nombre",
                   columns="periodo_ia", aggfunc="mean")
)
pivot.columns = ["2021-2022 (pre-IA)", "2023-2024 (IA Gen)"]
pivot["Δ (post − pre)"] = pivot["2023-2024 (IA Gen)"] - pivot["2021-2022 (pre-IA)"]
pivot = pivot.sort_values("2023-2024 (IA Gen)", ascending=False)

centro = pivot[["2021-2022 (pre-IA)", "2023-2024 (IA Gen)"]].mean().mean()
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlBu_r", center=centro,
            linewidths=0.5, linecolor="white",
            cbar_kws={"label": "Puntaje medio"}, ax=ax)
```

| Elemento | Significado |
|---|---|
| `pivot_table(values, index, columns, aggfunc)` | Crea tabla cruzada. |
| `pivot["Δ"] = a - b` | Nueva columna calculada. |
| `centro = ....mean().mean()` | Doble `.mean()`: primer mean por columna, segundo entre columnas. |
| `sns.heatmap(annot=True, fmt=".1f")` | Muestra el valor numérico en cada celda con 1 decimal. |
| `cmap="RdYlBu_r"` | Mapa divergente Red-Yellow-Blue invertido (azul = alto). |
| `center=centro` | Centra la escala de color en este valor. |
| `cbar_kws={"label": "..."}` | Argumentos para la barra de color. |

### `figura_violines_por_modulo(df, ruta_out)`

```python
etiquetas = {
    "punt_lectura_critica":  "Lectura\nCrítica",
    "punt_razona_cuant":     "Razonamiento\nCuantitativo",
    ...
}
largo = df.melt(
    id_vars=["periodo_ia"], value_vars=list(etiquetas),
    var_name="modulo_raw", value_name="puntaje",
)
largo["Módulo"] = largo["modulo_raw"].map(etiquetas)
largo["Cohorte"] = largo["periodo_ia"].map({0: "...", 1: "..."})

sns.violinplot(
    data=largo, x="Módulo", y="puntaje", hue="Cohorte",
    split=True, palette=PALETA_COHORTES,
    inner="quart", linewidth=1.0, order=list(etiquetas.values()),
    ax=ax,
)
```

| Elemento | Significado |
|---|---|
| `"Lectura\nCrítica"` | El `\n` es salto de línea: pone "Lectura" sobre "Crítica" en la etiqueta. |
| `df.melt(id_vars, value_vars, var_name, value_name)` | Convierte de formato **ancho a largo**: muchas columnas → una columna de variable + una de valor. |
| `split=True` | Violines **partidos** mostrando ambas cohortes con espejo. Muy útil para comparar. |
| `inner="quart"` | Muestra los cuartiles como líneas dentro del violín. |

---

## 4.9 Orquestador

### `ejecutar_analisis_descriptivo(ruta_proyecto)`

```python
def ejecutar_analisis_descriptivo(
    ruta_proyecto: Optional[str] = None,
) -> Dict[str, object]:
    _registrar("== INICIO ANÁLISIS DESCRIPTIVO (Parte 1) ==")
    if ruta_proyecto is None:
        montar_drive_si_aplica()
        ruta_proyecto = RUTA_DEFECTO
    df = cargar_consolidado(ruta_proyecto)

    dir_tablas  = os.path.join(ruta_proyecto, "procesados", "resultados")
    dir_figuras = os.path.join(ruta_proyecto, "procesados", "figuras")
    os.makedirs(dir_tablas, exist_ok=True)
    os.makedirs(dir_figuras, exist_ok=True)

    tab3 = tabla3_descriptivo(df)
    tab3.to_csv(os.path.join(dir_tablas, "tabla3_descriptivo.csv"),
                index=False, encoding="utf-8-sig")
    tab_dep = tabla_por_departamento(df)
    tab_dep.to_csv(os.path.join(dir_tablas, "tabla3_por_departamento.csv"),
                   index=False, encoding="utf-8-sig")

    figura_boxplot_periodo(df,        os.path.join(dir_figuras, "fig_01_boxplot_periodo.png"))
    figura_histograma_cohortes(df,    os.path.join(dir_figuras, "fig_02_histograma_cohortes.png"))
    figura_violines_por_modulo(df,    os.path.join(dir_figuras, "fig_03_modulos_cohorte.png"))
    figura_boxplot_departamento(df,   os.path.join(dir_figuras, "fig_04_boxplot_departamento.png"))
    figura_heatmap_dpto_cohorte(df,   os.path.join(dir_figuras, "fig_05_heatmap_departamento.png"))
    figura_dispersion_distancia(df,   os.path.join(dir_figuras, "fig_06_dispersion_distancia.png"))

    return {
        "tabla3":             tab3,
        "tabla_departamento": tab_dep,
        "dir_tablas":         dir_tablas,
        "dir_figuras":        dir_figuras,
    }
```

| Elemento | Significado |
|---|---|
| `Optional[str] = None` | Si `None`, comportamiento Colab. |
| `montar_drive_si_aplica()` | Importado de preparar_datos.py. |
| `ruta_proyecto = RUTA_DEFECTO` | Reasigna a la ruta por defecto. |
| `Dict[str, object]` | Diccionario con claves `str` y valores de cualquier tipo. |

---

## 4.10 CLI

```python
def _parser():
    p = argparse.ArgumentParser(description="...")
    p.add_argument("--ruta", "-r", default=None, help="...")
    return p

if __name__ == "__main__":
    args = _parser().parse_args()
    resultado = ejecutar_analisis_descriptivo(args.ruta)
    print(resultado["tabla3"].to_string(index=False))
```

- **`default=None`** — opcional; cuando no se pasa, usa el modo Colab.
- **`.to_string(index=False)`** — convierte el DataFrame en cadena
  formateada sin la columna de índice.

---

## 4.11 Recapitulación

Al terminar este capítulo deberías poder:

1. Explicar cuándo se usa **t-Welch** vs **Mann–Whitney** vs **χ²**.
2. Describir el flujo de cada una de las **6 figuras**.
3. Modificar la paleta o el tema de las figuras editando
   `_aplicar_estilo` y `PALETA_COHORTES`.
4. Añadir una variable nueva al análisis: agregarla a
   `VARS_CONTINUAS` o `VARS_DICOTOMICAS`.

Pasa al [Capítulo 5 — `regresion_mco.py`](./05_regresion_mco.md) para
entender los 18 modelos de regresión.
