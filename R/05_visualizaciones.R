# =============================================================================
# 05_visualizaciones.R — Figuras del análisis descriptivo y regresión
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# =============================================================================
# Figuras recomendadas en el documento:
#   Fig 1: Boxplot puntaje genérico por período y departamento (12 cajas)
#   Fig 2: Histograma comparativo del puntaje genérico por período
#   Fig 3: Dispersión distancia_bogota_km vs puntaje promedio por IES
#   Fig 4: Coeficientes β_IA (coef plot) por módulo y especificación
#   Fig 5: Coeficientes departamentales (brechas condicionales vs Bogotá)
#   Fig 6: Mapa de calor de correlaciones entre variables continuas
# =============================================================================

source("R/utils.R")
cargar_paquetes()

# Paleta de colores por período
COLORES_PERIODO <- c("0" = "#2196F3", "1" = "#F44336")
NOMBRES_PERIODO <- c("0" = "2021-2022 (pre-IA)", "1" = "2023-2024 (IA)")

# Paleta departamentos
COLORES_DEPTO <- c(
  "BOGOTA"    = "#1A237E",
  "ANTIOQUIA" = "#388E3C",
  "VALLE"     = "#F57C00",
  "HUILA"     = "#7B1FA2",
  "NARINO"    = "#C62828",
  "TOLIMA"    = "#00838F"
)

# =============================================================================
# Fig 1: Boxplot 12 cajas (2 períodos × 6 departamentos)
# =============================================================================

fig1_boxplot_periodo_depto <- function(df) {

  df_plot <- df %>%
    dplyr::filter(!is.na(puntaje_saberpro_generico), !is.na(depto_ies)) %>%
    dplyr::mutate(
      periodo_lbl = factor(periodo_ia, levels = c(0, 1),
                           labels = c("2021-2022", "2023-2024")),
      depto_lbl   = factor(depto_ies, levels = names(COLORES_DEPTO))
    )

  # Estadístico: n por celda
  n_etiq <- df_plot %>%
    dplyr::group_by(depto_lbl, periodo_lbl) %>%
    dplyr::summarise(n = dplyr::n(), .groups = "drop") %>%
    dplyr::mutate(etiq = paste0("n=", n))

  ggplot2::ggplot(df_plot,
                  ggplot2::aes(x = depto_lbl, y = puntaje_saberpro_generico,
                               fill = periodo_lbl)) +
    ggplot2::geom_boxplot(outlier.size = 0.5, outlier.alpha = 0.3,
                           position = ggplot2::position_dodge(width = 0.8),
                           width = 0.7) +
    ggplot2::geom_text(
      data = n_etiq,
      ggplot2::aes(x = depto_lbl, y = 85, label = etiq, group = periodo_lbl),
      position = ggplot2::position_dodge(width = 0.8),
      size = 2.5, vjust = 0, color = "gray40"
    ) +
    ggplot2::scale_fill_manual(values = c("2021-2022" = "#90CAF9",
                                           "2023-2024" = "#EF9A9A"),
                                name = "Período") +
    ggplot2::labs(
      title    = "Figura 1. Distribución del puntaje Saber Pro genérico",
      subtitle = "Por departamento y período (2021-2022 vs 2023-2024)",
      x = "Departamento de la IES",
      y = "Puntaje genérico (promedio 5 módulos)",
      caption = "Fuente: DataICFES. Bogotá D.C. = categoría de referencia del modelo."
    ) +
    tema_investigacion() +
    ggplot2::theme(axis.text.x = ggplot2::element_text(angle = 30, hjust = 1))
}

# =============================================================================
# Fig 2: Histograma comparativo por período
# =============================================================================

fig2_histograma_periodos <- function(df) {

  df_plot <- df %>%
    dplyr::filter(!is.na(puntaje_saberpro_generico)) %>%
    dplyr::mutate(
      periodo_lbl = factor(periodo_ia, levels = c(0, 1),
                           labels = c("2021-2022", "2023-2024"))
    )

  medias <- df_plot %>%
    dplyr::group_by(periodo_lbl) %>%
    dplyr::summarise(media = mean(puntaje_saberpro_generico), .groups = "drop")

  ggplot2::ggplot(df_plot,
                  ggplot2::aes(x = puntaje_saberpro_generico, fill = periodo_lbl)) +
    ggplot2::geom_histogram(
      ggplot2::aes(y = ggplot2::after_stat(density)),
      bins = 40, alpha = 0.55, position = "identity"
    ) +
    ggplot2::geom_density(ggplot2::aes(color = periodo_lbl),
                           linewidth = 0.9, fill = NA) +
    ggplot2::geom_vline(
      data = medias,
      ggplot2::aes(xintercept = media, color = periodo_lbl),
      linetype = "dashed", linewidth = 1
    ) +
    ggplot2::geom_text(
      data = medias,
      ggplot2::aes(x = media, y = 0.025, label = round(media, 1),
                   color = periodo_lbl),
      vjust = -1, size = 3.5
    ) +
    ggplot2::scale_fill_manual(values  = c("2021-2022" = "#1565C0",
                                            "2023-2024" = "#B71C1C"),
                                name = "Período") +
    ggplot2::scale_color_manual(values = c("2021-2022" = "#1565C0",
                                            "2023-2024" = "#B71C1C"),
                                 guide = "none") +
    ggplot2::labs(
      title    = "Figura 2. Distribución del puntaje genérico Saber Pro por período",
      subtitle = "Líneas punteadas = media por período",
      x = "Puntaje genérico", y = "Densidad",
      caption = "Fuente: DataICFES."
    ) +
    tema_investigacion()
}

# =============================================================================
# Fig 3: Dispersión distancia_bogota_km vs puntaje promedio por IES
# =============================================================================

fig3_dispersion_distancia <- function(df) {

  df_ies <- df %>%
    dplyr::filter(!is.na(puntaje_saberpro_generico),
                  !is.na(distancia_bogota_km)) %>%
    dplyr::group_by(nombre_ies, depto_ies, distancia_bogota_km, periodo_ia) %>%
    dplyr::summarise(
      puntaje_medio = mean(puntaje_saberpro_generico, na.rm = TRUE),
      n = dplyr::n(),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      periodo_lbl = factor(periodo_ia, levels = c(0, 1),
                           labels = c("2021-2022", "2023-2024"))
    )

  ggplot2::ggplot(df_ies,
                  ggplot2::aes(x = distancia_bogota_km, y = puntaje_medio,
                               color = depto_ies, size = n, shape = periodo_lbl)) +
    ggplot2::geom_point(alpha = 0.8) +
    ggplot2::geom_smooth(
      ggplot2::aes(group = 1),
      method = "lm", se = TRUE,
      color = "black", linewidth = 0.8, linetype = "dashed"
    ) +
    ggplot2::geom_text(
      ggplot2::aes(label = stringr::str_wrap(nombre_ies, 20)),
      vjust = -1, size = 2.2, show.legend = FALSE
    ) +
    ggplot2::scale_color_manual(values = COLORES_DEPTO, name = "Departamento") +
    ggplot2::scale_size_continuous(name = "N estudiantes", range = c(3, 10)) +
    ggplot2::scale_shape_manual(values = c(16, 17), name = "Período") +
    ggplot2::scale_x_continuous(breaks = c(0, 210, 310, 415, 460, 785),
                                  labels = c("Bogotá\n(0)", "Tolima\n(210)",
                                             "Huila\n(310)", "Antioquia\n(415)",
                                             "Valle\n(460)", "Nariño\n(785)")) +
    ggplot2::labs(
      title    = "Figura 3. Puntaje Saber Pro vs Distancia a Bogotá por IES",
      subtitle = "Línea de tendencia OLS (sin controles). Centralización geográfica.",
      x = "Distancia a Bogotá D.C. (km por vía terrestre)",
      y = "Puntaje genérico promedio por IES",
      caption = "Fuente: DataICFES + IGAC/INVIAS."
    ) +
    tema_investigacion()
}

# =============================================================================
# Fig 4: Coefplot de β_IA por módulo y especificación
# =============================================================================

fig4_coefplot_beta_ia <- function(tabla4) {
  if (is.null(tabla4) || nrow(tabla4) == 0) return(NULL)

  df_plot <- tabla4 %>%
    dplyr::filter(grepl("periodo_ia", etiqueta, ignore.case = TRUE)) %>%
    dplyr::mutate(
      modulo_lbl = dplyr::recode(var_dep, !!!ETIQUETAS_VARS, .default = var_dep),
      modulo_lbl = factor(modulo_lbl, levels = rev(unique(modulo_lbl))),
      spec_lbl   = dplyr::recode(spec,
        base   = "Especificación base",
        ef_ies = "+ EF por IES",
        ef_mun = "+ EF por municipio"
      ),
      ic_l = coef - 1.96 * se,
      ic_u = coef + 1.96 * se,
      sig  = p_valor < ALPHA
    )

  ggplot2::ggplot(df_plot,
                  ggplot2::aes(x = coef, y = modulo_lbl, color = spec_lbl,
                               shape = sig)) +
    ggplot2::geom_vline(xintercept = 0, linetype = "dashed", color = "gray50") +
    ggplot2::geom_errorbarh(
      ggplot2::aes(xmin = ic_l, xmax = ic_u),
      height = 0.2, linewidth = 0.8,
      position = ggplot2::position_dodge(width = 0.5)
    ) +
    ggplot2::geom_point(
      size = 3,
      position = ggplot2::position_dodge(width = 0.5)
    ) +
    ggplot2::scale_color_brewer(palette = "Set1", name = "Especificación") +
    ggplot2::scale_shape_manual(
      values = c("TRUE" = 16, "FALSE" = 1),
      labels = c("TRUE" = "p < 0.05", "FALSE" = "p ≥ 0.05"),
      name = "Significancia"
    ) +
    ggplot2::labs(
      title    = "Figura 4. Coeficiente β_IA por módulo y especificación",
      subtitle = "Intervalo de confianza 95% (errores clusterizados por IES)",
      x = "β_IA (diferencia condicional de puntaje, período IA vs pre-IA)",
      y = NULL,
      caption = "Línea punteada = β_IA = 0 (sin asociación). Bogotá D.C. = categoría de referencia.\nFuente: DataICFES."
    ) +
    tema_investigacion()
}

# =============================================================================
# Fig 5: Coeficientes departamentales (brechas vs Bogotá)
# =============================================================================

fig5_brechas_departamentales <- function(tabla4) {
  if (is.null(tabla4) || nrow(tabla4) == 0) return(NULL)

  etiq_deptos <- c(
    "d_antioquia" = "Antioquia",
    "d_valle"     = "Valle del Cauca",
    "d_huila"     = "Huila",
    "d_narino"    = "Nariño",
    "d_tolima"    = "Tolima"
  )

  df_plot <- tabla4 %>%
    dplyr::filter(spec == "base") %>%
    dplyr::filter(grepl("^d_", etiqueta) |
                    etiqueta %in% names(ETIQUETAS_VARS[grepl("^d_", names(ETIQUETAS_VARS))])) %>%
    dplyr::filter(var_dep == "puntaje_saberpro_generico" |
                    var_dep %in% MODULOS_GENERICOS) %>%
    dplyr::mutate(
      depto_lbl  = dplyr::recode(etiqueta,
        "Dpto. Antioquia (ref. Bogotá)"   = "Antioquia",
        "Dpto. Valle del Cauca (ref. Bogotá)" = "Valle del Cauca",
        "Dpto. Huila (ref. Bogotá)"       = "Huila",
        "Dpto. Nariño (ref. Bogotá)"      = "Nariño",
        "Dpto. Tolima (ref. Bogotá)"      = "Tolima",
        .default = etiqueta
      ),
      modulo_lbl = dplyr::recode(var_dep, !!!ETIQUETAS_VARS, .default = var_dep),
      ic_l = coef - 1.96 * se,
      ic_u = coef + 1.96 * se,
      sig  = p_valor < ALPHA
    )

  ggplot2::ggplot(df_plot,
                  ggplot2::aes(x = coef, y = reorder(depto_lbl, coef),
                               color = modulo_lbl, shape = sig)) +
    ggplot2::geom_vline(xintercept = 0, linetype = "dashed", color = "gray50") +
    ggplot2::geom_errorbarh(
      ggplot2::aes(xmin = ic_l, xmax = ic_u),
      height = 0.25, linewidth = 0.7,
      position = ggplot2::position_dodge(width = 0.6)
    ) +
    ggplot2::geom_point(
      size = 2.5,
      position = ggplot2::position_dodge(width = 0.6)
    ) +
    ggplot2::scale_color_viridis_d(name = "Módulo/Puntaje") +
    ggplot2::scale_shape_manual(
      values = c("TRUE" = 16, "FALSE" = 1),
      labels = c("TRUE" = "p < 0.05", "FALSE" = "p ≥ 0.05"),
      name = "Significancia"
    ) +
    ggplot2::labs(
      title    = "Figura 5. Brechas departamentales condicionales vs Bogotá D.C.",
      subtitle = "Especificación base — Bogotá D.C. = 0 (categoría de referencia omitida)",
      x = "Diferencia condicional en puntaje respecto a Bogotá D.C.",
      y = NULL,
      caption = "IC 95% con errores clusterizados por IES. Fuente: DataICFES."
    ) +
    tema_investigacion()
}

# =============================================================================
# Fig 6: Mapa de calor de correlaciones
# =============================================================================

fig6_correlaciones <- function(df) {
  vars_num <- c(
    "puntaje_saberpro_generico", MODULOS_GENERICOS,
    "puntaje_saber11", "estrato", "nivel_educ_padre",
    "distancia_bogota_km", "genero", "internet", "estu_trabaja"
  )
  vars_num <- intersect(vars_num, names(df))

  mat_cor <- df %>%
    dplyr::select(dplyr::all_of(vars_num)) %>%
    stats::cor(use = "pairwise.complete.obs")

  # Renombrar para gráfico
  rownames(mat_cor) <- colnames(mat_cor) <-
    dplyr::recode(rownames(mat_cor), !!!ETIQUETAS_VARS, .default = rownames(mat_cor))

  corrplot::corrplot(
    mat_cor,
    method  = "color",
    type    = "upper",
    tl.cex  = 0.65,
    addCoef.col = "black",
    number.cex  = 0.45,
    title   = "Figura 6. Correlaciones entre variables del modelo",
    mar     = c(0, 0, 2, 0)
  )

  invisible(mat_cor)
}

# =============================================================================
# Fig 7: Serie de tiempo — puntaje medio por año
# =============================================================================

fig7_serie_anual <- function(df) {
  df_anual <- df %>%
    dplyr::filter(!is.na(puntaje_saberpro_generico), !is.na(ANIO_APLICACION)) %>%
    dplyr::group_by(ANIO_APLICACION, depto_ies) %>%
    dplyr::summarise(
      media = mean(puntaje_saberpro_generico, na.rm = TRUE),
      n     = dplyr::n(),
      .groups = "drop"
    )

  ggplot2::ggplot(df_anual,
                  ggplot2::aes(x = ANIO_APLICACION, y = media,
                               color = depto_ies, group = depto_ies)) +
    ggplot2::geom_line(linewidth = 1) +
    ggplot2::geom_point(ggplot2::aes(size = n), alpha = 0.9) +
    ggplot2::geom_vline(xintercept = 2022.5, linetype = "dotted",
                         color = "black", linewidth = 1) +
    ggplot2::annotate("text", x = 2022.6, y = Inf,
                       label = "Adopción masiva\nIA Gen →",
                       hjust = 0, vjust = 1.5, size = 3, color = "black") +
    ggplot2::scale_color_manual(values = COLORES_DEPTO, name = "Departamento") +
    ggplot2::scale_x_continuous(breaks = 2021:2024) +
    ggplot2::labs(
      title    = "Figura 7. Evolución del puntaje Saber Pro genérico por departamento (2021-2024)",
      subtitle = "La línea vertical marca el umbral de adopción masiva de IA generativa (nov-2022)",
      x = "Año de aplicación",
      y = "Puntaje genérico promedio",
      caption = "Fuente: DataICFES."
    ) +
    tema_investigacion()
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

generar_visualizaciones <- function(df, tabla4 = NULL,
                                     guardar = TRUE,
                                     dir_figuras = "outputs/figuras") {

  message("=== Generando visualizaciones ===\n")

  # Fig 1
  message("Fig 1: Boxplot período × departamento...")
  p1 <- fig1_boxplot_periodo_depto(df)
  if (guardar) guardar_figura(p1, "F1_boxplot_periodo_depto", directorio = dir_figuras)

  # Fig 2
  message("Fig 2: Histograma comparativo por período...")
  p2 <- fig2_histograma_periodos(df)
  if (guardar) guardar_figura(p2, "F2_histograma_periodos", directorio = dir_figuras)

  # Fig 3
  message("Fig 3: Dispersión distancia vs puntaje por IES...")
  p3 <- fig3_dispersion_distancia(df)
  if (guardar) guardar_figura(p3, "F3_dispersion_distancia", directorio = dir_figuras)

  # Fig 7
  message("Fig 7: Serie temporal por departamento...")
  p7 <- fig7_serie_anual(df)
  if (guardar) guardar_figura(p7, "F7_serie_anual_depto", directorio = dir_figuras)

  # Figs que requieren tabla4
  p4 <- p5 <- NULL
  if (!is.null(tabla4)) {
    message("Fig 4: Coefplot β_IA...")
    p4 <- fig4_coefplot_beta_ia(tabla4)
    if (!is.null(p4) && guardar)
      guardar_figura(p4, "F4_coefplot_beta_ia", directorio = dir_figuras)

    message("Fig 5: Brechas departamentales...")
    p5 <- fig5_brechas_departamentales(tabla4)
    if (!is.null(p5) && guardar)
      guardar_figura(p5, "F5_brechas_departamentales", directorio = dir_figuras)
  }

  # Fig 6 (corrplot — genera su propio gráfico)
  message("Fig 6: Mapa de calor de correlaciones...")
  if (guardar) {
    png(file.path(dir_figuras, "F6_correlaciones.png"),
        width = 2800, height = 2400, res = 300)
    fig6_correlaciones(df)
    dev.off()
  } else {
    fig6_correlaciones(df)
  }

  message("Visualizaciones completadas.")
  invisible(list(p1 = p1, p2 = p2, p3 = p3, p4 = p4, p5 = p5, p7 = p7))
}

# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================
if (!interactive()) {
  df <- readRDS("data/processed/datos_analisis.rds")
  tabla4 <- tryCatch(
    readRDS("outputs/tablas/T4_coeficientes_todos_modelos.rds"),
    error = function(e) NULL
  )
  generar_visualizaciones(df, tabla4)
}
