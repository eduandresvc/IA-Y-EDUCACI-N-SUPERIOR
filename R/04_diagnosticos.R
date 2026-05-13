# =============================================================================
# 04_diagnosticos.R — Pruebas de diagnóstico para los modelos MCO
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# =============================================================================
# Diagnósticos (Wooldridge, 2020):
#   1. Normalidad de residuales: Shapiro-Wilk / Kolmogorov-Smirnov
#   2. Homocedasticidad: Breusch-Pagan
#   3. Multicolinealidad: VIF (umbral > 10)
#   4. Autocorrelación: Durbin-Watson
#   5. Especificación: RESET de Ramsey
#   6. Corrección por pruebas múltiples (Holm / Benjamini-Hochberg)
# =============================================================================

source("R/utils.R")
cargar_paquetes()

# =============================================================================
# 1. NORMALIDAD DE RESIDUALES
# =============================================================================

prueba_normalidad <- function(modelo, n_umbral = 5000) {
  if (is.null(modelo)) return(NULL)

  res <- if (inherits(modelo, "fixest")) {
    residuals(modelo)
  } else {
    residuals(modelo)
  }
  res <- res[!is.na(res)]
  n   <- length(res)

  if (n < n_umbral) {
    # Shapiro-Wilk (recomendado para n < 5000)
    sw <- tryCatch(shapiro.test(res), error = function(e) NULL)
    tibble::tibble(
      prueba    = "Shapiro-Wilk",
      estadistico = if (!is.null(sw)) round(sw$statistic, 4) else NA,
      p_valor   = if (!is.null(sw)) round(sw$p.value, 4) else NA,
      n         = n,
      conclusion = if (!is.null(sw) && sw$p.value >= ALPHA)
                     "No se rechaza normalidad" else "Se rechaza normalidad"
    )
  } else {
    # Kolmogorov-Smirnov para muestras grandes
    ks  <- tryCatch(
      ks.test(scale(res), "pnorm"),
      error = function(e) NULL
    )
    tibble::tibble(
      prueba    = "Kolmogorov-Smirnov",
      estadistico = if (!is.null(ks)) round(ks$statistic, 4) else NA,
      p_valor   = if (!is.null(ks)) round(ks$p.value, 4) else NA,
      n         = n,
      conclusion = if (!is.null(ks) && ks$p.value >= ALPHA)
                     "No se rechaza normalidad" else "Se rechaza normalidad"
    )
  }
}

# =============================================================================
# 2. HOMOCEDASTICIDAD: BREUSCH-PAGAN
# =============================================================================

prueba_homocedasticidad <- function(modelo) {
  if (is.null(modelo) || !inherits(modelo, "lm")) return(NULL)

  bp <- tryCatch(lmtest::bptest(modelo), error = function(e) NULL)

  tibble::tibble(
    prueba      = "Breusch-Pagan",
    estadistico = if (!is.null(bp)) round(bp$statistic, 4) else NA,
    df          = if (!is.null(bp)) bp$parameter else NA,
    p_valor     = if (!is.null(bp)) round(bp$p.value, 4) else NA,
    conclusion  = if (!is.null(bp) && bp$p.value >= ALPHA)
                    "Homocedasticidad (no se rechaza)" else "Heterocedasticidad detectada"
  )
}

# =============================================================================
# 3. FACTOR DE INFLACIÓN DE VARIANZA (FIV / VIF)
# =============================================================================

prueba_multicolinealidad <- function(modelo) {
  if (is.null(modelo) || !inherits(modelo, "lm")) return(NULL)

  vif_vals <- tryCatch(car::vif(modelo), error = function(e) NULL)
  if (is.null(vif_vals)) return(NULL)

  # Si vif devuelve matrix (cuando hay factores), tomar la columna GVIF^(1/(2*Df))
  if (is.matrix(vif_vals)) {
    vif_df <- tibble::as_tibble(vif_vals, rownames = "variable") %>%
      dplyr::rename(vif = `GVIF^(1/(2*Df))`) %>%
      dplyr::mutate(vif = vif^2)
  } else {
    vif_df <- tibble::enframe(vif_vals, name = "variable", value = "vif")
  }

  vif_df %>%
    dplyr::mutate(
      vif      = round(vif, 3),
      tolerancia = round(1 / vif, 3),
      alerta   = vif > 10,
      nivel    = dplyr::case_when(
        vif > 10 ~ "ALTA (> 10): problema grave",
        vif > 5  ~ "MODERADA (5-10): revisar",
        TRUE     ~ "Aceptable (< 5)"
      )
    ) %>%
    dplyr::arrange(dplyr::desc(vif))
}

# =============================================================================
# 4. AUTOCORRELACIÓN: DURBIN-WATSON
# =============================================================================

prueba_autocorrelacion <- function(modelo) {
  if (is.null(modelo) || !inherits(modelo, "lm")) return(NULL)

  dw <- tryCatch(lmtest::dwtest(modelo), error = function(e) NULL)
  if (is.null(dw)) return(NULL)

  tibble::tibble(
    prueba      = "Durbin-Watson",
    estadistico = round(dw$statistic, 4),
    p_valor     = round(dw$p.value, 4),
    conclusion  = dplyr::case_when(
      dw$statistic < 1.5 ~ "Posible autocorrelación positiva",
      dw$statistic > 2.5 ~ "Posible autocorrelación negativa",
      TRUE               ~ "Sin evidencia de autocorrelación"
    )
  )
}

# =============================================================================
# 5. ESPECIFICACIÓN: RESET DE RAMSEY
# =============================================================================

prueba_especificacion <- function(modelo) {
  if (is.null(modelo) || !inherits(modelo, "lm")) return(NULL)

  rst <- tryCatch(lmtest::resettest(modelo, power = 2:3, type = "fitted"),
                  error = function(e) NULL)
  if (is.null(rst)) return(NULL)

  tibble::tibble(
    prueba      = "RESET de Ramsey",
    estadistico = round(rst$statistic, 4),
    df1         = rst$parameter[1],
    df2         = rst$parameter[2],
    p_valor     = round(rst$p.value, 4),
    conclusion  = if (rst$p.value >= ALPHA)
                    "Sin evidencia de mala especificación" else "Posible mala especificación"
  )
}

# =============================================================================
# 6. DIAGNÓSTICO COMPLETO PARA UN MODELO
# =============================================================================

diagnostico_modelo <- function(resultado, nombre_modelo = "") {
  if (is.null(resultado)) return(NULL)
  modelo <- resultado$modelo

  if (!inherits(modelo, "lm") && !inherits(modelo, "fixest")) return(NULL)

  # Para fixest, los diagnósticos de lmtest no aplican directamente
  if (inherits(modelo, "fixest")) {
    message("  Diagnósticos limitados para modelo fixest (", nombre_modelo, ")")
    return(list(nombre = nombre_modelo, limitado = TRUE))
  }

  list(
    nombre            = nombre_modelo,
    normalidad        = prueba_normalidad(modelo),
    homocedasticidad  = prueba_homocedasticidad(modelo),
    multicolinealidad = prueba_multicolinealidad(modelo),
    autocorrelacion   = prueba_autocorrelacion(modelo),
    especificacion    = prueba_especificacion(modelo)
  )
}

# =============================================================================
# 7. TABLA CONSOLIDADA DE DIAGNÓSTICOS
# =============================================================================

consolidar_diagnosticos <- function(lista_diag) {
  # Extraer una fila por modelo con las pruebas clave
  purrr::map_dfr(lista_diag, function(d) {
    if (is.null(d) || isTRUE(d$limitado)) {
      return(tibble::tibble(modelo = d$nombre %||% "desconocido",
                            nota = "diagnóstico no disponible"))
    }

    tibble::tibble(
      modelo        = d$nombre,
      # Normalidad
      norm_prueba   = d$normalidad$prueba %||% NA_character_,
      norm_p        = d$normalidad$p_valor %||% NA_real_,
      norm_ok       = (d$normalidad$p_valor %||% 0) >= ALPHA,
      # Homocedasticidad
      bp_p          = d$homocedasticidad$p_valor %||% NA_real_,
      bp_ok         = (d$homocedasticidad$p_valor %||% 0) >= ALPHA,
      # Multicolinealidad (max VIF)
      max_vif       = if (!is.null(d$multicolinealidad))
                        max(d$multicolinealidad$vif, na.rm = TRUE) else NA_real_,
      vif_ok        = (max(d$multicolinealidad$vif %||% 0, na.rm = TRUE)) <= 10,
      # Autocorrelación
      dw_stat       = d$autocorrelacion$estadistico %||% NA_real_,
      dw_ok         = dplyr::between(d$autocorrelacion$estadistico %||% 2, 1.5, 2.5),
      # Especificación
      reset_p       = d$especificacion$p_valor %||% NA_real_,
      reset_ok      = (d$especificacion$p_valor %||% 1) >= ALPHA
    )
  })
}

# =============================================================================
# 8. GRÁFICOS DE DIAGNÓSTICO
# =============================================================================

graficos_diagnostico <- function(resultado, nombre = "modelo",
                                  directorio = "outputs/figuras") {
  if (is.null(resultado) || !inherits(resultado$modelo, "lm")) return(invisible(NULL))

  modelo <- resultado$modelo
  res    <- residuals(modelo)
  ajust  <- fitted(modelo)

  # Panel de 4 gráficos clásicos
  p_list <- list(
    # 1. Residuales vs Ajustados
    p1 = ggplot2::ggplot(
      tibble::tibble(ajustados = ajust, residuales = res),
      ggplot2::aes(x = ajustados, y = residuales)
    ) +
      ggplot2::geom_point(alpha = 0.3, size = 0.8) +
      ggplot2::geom_hline(yintercept = 0, color = "red", linetype = "dashed") +
      ggplot2::geom_smooth(method = "loess", se = FALSE, color = "blue", linewidth = 0.7) +
      ggplot2::labs(title = "Residuales vs Ajustados",
                    x = "Valores ajustados", y = "Residuales") +
      tema_investigacion(),

    # 2. QQ-plot
    p2 = ggplot2::ggplot(
      tibble::tibble(res = res),
      ggplot2::aes(sample = res)
    ) +
      ggplot2::stat_qq(alpha = 0.4, size = 0.8) +
      ggplot2::stat_qq_line(color = "red") +
      ggplot2::labs(title = "QQ-plot de residuales",
                    x = "Cuantiles teóricos", y = "Cuantiles muestrales") +
      tema_investigacion(),

    # 3. Escala-Localización (sqrt |residuales estandarizados| vs ajustados)
    p3 = ggplot2::ggplot(
      tibble::tibble(ajustados = ajust,
                     sqrt_res_std = sqrt(abs(rstandard(modelo)))),
      ggplot2::aes(x = ajustados, y = sqrt_res_std)
    ) +
      ggplot2::geom_point(alpha = 0.3, size = 0.8) +
      ggplot2::geom_smooth(method = "loess", se = FALSE, color = "blue", linewidth = 0.7) +
      ggplot2::labs(title = "Escala-Localización",
                    x = "Valores ajustados",
                    y = expression(sqrt("|Residuales estandarizados|"))) +
      tema_investigacion(),

    # 4. Histograma de residuales
    p4 = ggplot2::ggplot(tibble::tibble(res = res), ggplot2::aes(x = res)) +
      ggplot2::geom_histogram(aes(y = ggplot2::after_stat(density)),
                               bins = 30, fill = "steelblue", alpha = 0.7) +
      ggplot2::geom_density(color = "darkblue", linewidth = 0.8) +
      ggplot2::stat_function(fun = dnorm,
                              args = list(mean = mean(res), sd = sd(res)),
                              color = "red", linetype = "dashed", linewidth = 0.8) +
      ggplot2::labs(title = "Distribución de residuales",
                    x = "Residual", y = "Densidad") +
      tema_investigacion()
  )

  panel <- patchwork::wrap_plots(p_list, ncol = 2) +
    patchwork::plot_annotation(
      title = paste("Diagnósticos:", nombre),
      theme = ggplot2::theme(plot.title = ggplot2::element_text(face = "bold"))
    )

  guardar_figura(panel, paste0("diag_", nombre), ancho = 12, alto = 9, directorio)
  invisible(panel)
}

# =============================================================================
# 9. CORRECCIÓN POR PRUEBAS MÚLTIPLES (sobre los β_IA)
# =============================================================================

correccion_multiples_modelos <- function(tabla4) {
  # Extraer p-valores de periodo_ia en todos los modelos
  pvals_ia <- tabla4 %>%
    dplyr::filter(grepl("periodo_ia", etiqueta, ignore.case = TRUE)) %>%
    dplyr::select(var_dep, spec, p_valor)

  pvals_ia %>%
    dplyr::mutate(
      p_holm = stats::p.adjust(p_valor, method = "holm"),
      p_bh   = stats::p.adjust(p_valor, method = "BH"),
      sig_original = p_valor < ALPHA,
      sig_holm     = p_holm  < ALPHA,
      sig_bh       = p_bh    < ALPHA
    )
}

# =============================================================================
# 10. FUNCIÓN PRINCIPAL
# =============================================================================

ejecutar_diagnosticos <- function(lista_modelos, tabla4 = NULL,
                                   guardar = TRUE,
                                   dir_tablas = "outputs/tablas",
                                   dir_figuras = "outputs/figuras") {

  message("=== Diagnósticos de los modelos MCO ===\n")

  # Solo diagnosticar modelos base (lm) en la spec "base"
  modelos_base <- lista_modelos[grepl("_base$", names(lista_modelos))]

  lista_diag <- purrr::imap(modelos_base, function(res, nombre) {
    message("  Diagnosticando: ", nombre)
    diagnostico_modelo(res, nombre)
  })

  # Tabla consolidada
  message("\nConsolidando resultados de diagnóstico...")
  tbl_diag <- consolidar_diagnosticos(lista_diag)
  if (guardar) guardar_tabla(tbl_diag, "T_diagnosticos_resumen", dir_tablas)

  # Gráficos de diagnóstico (solo modelos genérico y módulos)
  message("\nGenerando gráficos de diagnóstico...")
  purrr::iwalk(modelos_base, function(res, nombre) {
    graficos_diagnostico(res, nombre, dir_figuras)
  })

  # Corrección por pruebas múltiples
  if (!is.null(tabla4)) {
    message("\nAplicando corrección por pruebas múltiples (Holm & BH)...")
    tbl_corr <- correccion_multiples_modelos(tabla4)
    if (guardar) guardar_tabla(tbl_corr, "T_correccion_multiplas", dir_tablas)
    message("\n--- Corrección por pruebas múltiples (β_IA) ---")
    print(tbl_corr)
  } else {
    tbl_corr <- NULL
  }

  # Imprimir resumen
  message("\n--- Resumen de diagnósticos ---")
  print(tbl_diag)

  list(
    diagnosticos_detalle = lista_diag,
    tabla_resumen        = tbl_diag,
    correccion_multiplas = tbl_corr
  )
}

# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================
if (!interactive()) {
  df <- readRDS("data/processed/datos_analisis.rds")

  if (file.exists("outputs/modelos/puntaje_saberpro_generico_base.rds")) {
    # Cargar modelos guardados
    archivos_modelos <- list.files("outputs/modelos", pattern = "\\.rds$",
                                    full.names = TRUE)
    lista_modelos <- purrr::map(archivos_modelos, readRDS) %>%
      purrr::set_names(tools::file_path_sans_ext(basename(archivos_modelos)))

    tabla4 <- readRDS("outputs/tablas/T4_coeficientes_todos_modelos.rds")
    diag_res <- ejecutar_diagnosticos(lista_modelos, tabla4)
  } else {
    message("Ejecute primero 03_regresion_ols.R para generar los modelos.")
  }
}
