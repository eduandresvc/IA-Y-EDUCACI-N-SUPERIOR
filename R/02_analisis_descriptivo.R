# =============================================================================
# 02_analisis_descriptivo.R — PARTE 1: Análisis descriptivo comparativo
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# =============================================================================
# Compara 2021-2022 (periodo_ia=0) vs 2023-2024 (periodo_ia=1)
# Reporta: medias, DEs, frecuencias, pruebas t de Welch, χ², Mann-Whitney
# =============================================================================

source("R/utils.R")
cargar_paquetes()

# =============================================================================
# 1. ESTADÍSTICOS DESCRIPTIVOS GENERALES
# =============================================================================

#' Genera tabla descriptiva Tabla 3 del documento
#' @param df Data frame con datos procesados
#' @return Data frame con estadísticos por período
tabla_descriptiva_periodo <- function(df) {

  vars_continuas <- c(
    "puntaje_saberpro_generico",
    MODULOS_GENERICOS,
    "puntaje_saber11",
    "estrato",
    "nivel_educ_padre",
    "distancia_bogota_km"
  )

  vars_dicotomicas <- c(
    "genero", "estu_trabaja", "estu_cabeza_familia",
    "internet", "area_residencia", "naturaleza_ies",
    "periodo_ia"
  )

  # --- Variables continuas ---
  tbl_continuas <- purrr::map_dfr(
    intersect(vars_continuas, names(df)),
    function(v) {
      d0 <- df %>% dplyr::filter(periodo_ia == 0) %>% dplyr::pull(v) %>% na.omit()
      d1 <- df %>% dplyr::filter(periodo_ia == 1) %>% dplyr::pull(v) %>% na.omit()

      # t-test de Welch
      tt  <- tryCatch(t.test(d0, d1, var.equal = FALSE), error = function(e) NULL)
      # Mann-Whitney
      mw  <- tryCatch(wilcox.test(d0, d1, exact = FALSE), error = function(e) NULL)

      tibble::tibble(
        variable   = v,
        tipo       = "continua",
        media_p0   = round(mean(d0), 2),
        de_p0      = round(sd(d0), 2),
        n_p0       = length(d0),
        media_p1   = round(mean(d1), 2),
        de_p1      = round(sd(d1), 2),
        n_p1       = length(d1),
        delta      = round(mean(d1) - mean(d0), 2),
        t_stat     = if (!is.null(tt)) round(tt$statistic, 3) else NA_real_,
        p_ttest    = if (!is.null(tt)) round(tt$p.value, 4) else NA_real_,
        p_mw       = if (!is.null(mw)) round(mw$p.value, 4) else NA_real_,
        sig_ttest  = if (!is.null(tt)) stars(tt$p.value) else ""
      )
    }
  )

  # --- Variables dicotómicas ---
  tbl_dicot <- purrr::map_dfr(
    intersect(vars_dicotomicas, names(df)),
    function(v) {
      x0 <- df %>% dplyr::filter(periodo_ia == 0) %>% dplyr::pull(v) %>% na.omit()
      x1 <- df %>% dplyr::filter(periodo_ia == 1) %>% dplyr::pull(v) %>% na.omit()

      prop0 <- mean(x0)
      prop1 <- mean(x1)

      # χ² con corrección de Yates
      tbl2x2 <- table(df[[v]], df$periodo_ia)
      chi2 <- tryCatch(chisq.test(tbl2x2, correct = TRUE), error = function(e) NULL)

      tibble::tibble(
        variable   = v,
        tipo       = "dicotomica",
        media_p0   = round(prop0 * 100, 1),
        de_p0      = NA_real_,
        n_p0       = length(x0),
        media_p1   = round(prop1 * 100, 1),
        de_p1      = NA_real_,
        n_p1       = length(x1),
        delta      = round((prop1 - prop0) * 100, 1),
        t_stat     = if (!is.null(chi2)) round(chi2$statistic, 3) else NA_real_,
        p_ttest    = if (!is.null(chi2)) round(chi2$p.value, 4) else NA_real_,
        p_mw       = NA_real_,
        sig_ttest  = if (!is.null(chi2)) stars(chi2$p.value) else ""
      )
    }
  )

  dplyr::bind_rows(tbl_continuas, tbl_dicot) %>%
    dplyr::mutate(
      etiqueta = dplyr::recode(variable, !!!ETIQUETAS_VARS, .default = variable)
    ) %>%
    dplyr::select(etiqueta, tipo, media_p0, de_p0, n_p0,
                  media_p1, de_p1, n_p1, delta, t_stat, p_ttest, p_mw, sig_ttest)
}

# =============================================================================
# 2. TABLA DESCRIPTIVA POR DEPARTAMENTO
# =============================================================================

tabla_descriptiva_depto <- function(df) {

  vars_puntajes <- c("puntaje_saberpro_generico", MODULOS_GENERICOS)
  vars_puntajes <- intersect(vars_puntajes, names(df))

  df %>%
    dplyr::group_by(depto_ies, periodo_ia) %>%
    dplyr::summarise(
      n = dplyr::n(),
      dplyr::across(
        dplyr::all_of(vars_puntajes),
        list(
          media = ~ round(mean(.x, na.rm = TRUE), 2),
          de    = ~ round(sd(.x, na.rm = TRUE), 2)
        ),
        .names = "{.col}_{.fn}"
      ),
      .groups = "drop"
    ) %>%
    dplyr::arrange(depto_ies, periodo_ia)
}

# =============================================================================
# 3. ESTADÍSTICOS DESCRIPTIVOS GENERALES (Tabla resumen)
# =============================================================================

resumen_univariado <- function(df) {
  vars_num <- df %>%
    dplyr::select(where(is.numeric)) %>%
    names()

  df %>%
    dplyr::select(dplyr::all_of(vars_num)) %>%
    tidyr::pivot_longer(everything(), names_to = "variable", values_to = "valor") %>%
    dplyr::group_by(variable) %>%
    dplyr::summarise(
      n       = sum(!is.na(valor)),
      media   = round(mean(valor, na.rm = TRUE), 3),
      de      = round(sd(valor, na.rm = TRUE), 3),
      min     = round(min(valor, na.rm = TRUE), 3),
      p25     = round(quantile(valor, 0.25, na.rm = TRUE), 3),
      mediana = round(median(valor, na.rm = TRUE), 3),
      p75     = round(quantile(valor, 0.75, na.rm = TRUE), 3),
      max     = round(max(valor, na.rm = TRUE), 3),
      pct_na  = round(mean(is.na(valor)) * 100, 1),
      .groups = "drop"
    ) %>%
    dplyr::filter(variable %in% c(
      "puntaje_saberpro_generico", MODULOS_GENERICOS,
      "estrato", "nivel_educ_padre", "puntaje_saber11", "distancia_bogota_km"
    ))
}

# =============================================================================
# 4. FRECUENCIAS DE VARIABLES CATEGÓRICAS
# =============================================================================

frecuencias_categoricas <- function(df) {
  vars_cat <- c("periodo_ia", "depto_ies", "programa_academico",
                "naturaleza_ies", "genero", "internet", "area_residencia",
                "estu_trabaja")
  vars_cat <- intersect(vars_cat, names(df))

  purrr::map(vars_cat, function(v) {
    df %>%
      dplyr::count(!!rlang::sym(v), name = "n") %>%
      dplyr::mutate(pct = round(n / sum(n) * 100, 1)) %>%
      dplyr::rename(categoria = 1)
  }) %>%
    purrr::set_names(vars_cat)
}

# =============================================================================
# 5. PRUEBAS DE HIPÓTESIS ADICIONALES
# =============================================================================

prueba_diferencia_puntajes <- function(df) {
  vars_puntajes <- c("puntaje_saberpro_generico", MODULOS_GENERICOS)
  vars_puntajes <- intersect(vars_puntajes, names(df))

  purrr::map_dfr(vars_puntajes, function(v) {
    d0 <- df %>% dplyr::filter(periodo_ia == 0) %>% dplyr::pull(v) %>% na.omit()
    d1 <- df %>% dplyr::filter(periodo_ia == 1) %>% dplyr::pull(v) %>% na.omit()

    tt <- t.test(d0, d1, var.equal = FALSE)
    mw <- wilcox.test(d0, d1, exact = FALSE, conf.int = TRUE)

    tibble::tibble(
      modulo      = ETIQUETAS_VARS[v] %||% v,
      media_2122  = round(mean(d0), 2),
      media_2324  = round(mean(d1), 2),
      diferencia  = round(mean(d1) - mean(d0), 2),
      ic_95_inf   = round(tt$conf.int[1], 2),
      ic_95_sup   = round(tt$conf.int[2], 2),
      t_stat      = round(tt$statistic, 3),
      gl          = round(tt$parameter, 1),
      p_ttest     = round(tt$p.value, 4),
      W_stat      = round(mw$statistic, 0),
      p_mw        = round(mw$p.value, 4),
      significativo = p_ttest < ALPHA
    )
  })
}

# Operador %||% (si no está disponible)
`%||%` <- function(a, b) if (!is.null(a) && !is.na(a)) a else b

# =============================================================================
# 6. CORRECCIÓN POR PRUEBAS MÚLTIPLES (Holm / Benjamini-Hochberg)
# =============================================================================

corregir_p_multiplas <- function(tbl, col_p = "p_ttest") {
  tbl %>%
    dplyr::mutate(
      p_holm = stats::p.adjust(.data[[col_p]], method = "holm"),
      p_bh   = stats::p.adjust(.data[[col_p]], method = "BH"),
      sig_holm = p_holm < ALPHA,
      sig_bh   = p_bh   < ALPHA
    )
}

# =============================================================================
# 7. FUNCIÓN PRINCIPAL
# =============================================================================

analisis_descriptivo <- function(df,
                                  guardar = TRUE,
                                  dir_tablas = "outputs/tablas") {

  message("=== PARTE 1: Análisis Descriptivo ===\n")

  # 7.1 Resumen univariado general
  message("7.1 Resumen univariado...")
  tbl_resumen <- resumen_univariado(df)
  if (guardar) guardar_tabla(tbl_resumen, "T0_resumen_univariado", dir_tablas)

  # 7.2 Tabla 3: Comparación descriptiva entre períodos
  message("7.2 Tabla 3: Comparación entre períodos...")
  tbl3 <- tabla_descriptiva_periodo(df)
  if (guardar) guardar_tabla(tbl3, "T3_descriptivo_periodos", dir_tablas)

  # 7.3 Prueba de diferencia de puntajes con IC
  message("7.3 Pruebas de diferencia de medias en puntajes...")
  tbl_puntajes <- prueba_diferencia_puntajes(df) %>%
    corregir_p_multiplas()
  if (guardar) guardar_tabla(tbl_puntajes, "T3b_prueba_puntajes", dir_tablas)

  # 7.4 Tabla descriptiva por departamento
  message("7.4 Descriptivo por departamento...")
  tbl_depto <- tabla_descriptiva_depto(df)
  if (guardar) guardar_tabla(tbl_depto, "T_descriptivo_departamento", dir_tablas)

  # 7.5 Frecuencias de variables categóricas
  message("7.5 Frecuencias categóricas...")
  freqs <- frecuencias_categoricas(df)

  # Imprimir resultados clave
  message("\n--- RESULTADOS CLAVE (Parte 1) ---")
  message("Diferencia de medias en puntaje genérico:")
  print(tbl_puntajes %>%
          dplyr::filter(grepl("Genérico", modulo)) %>%
          dplyr::select(modulo, media_2122, media_2324, diferencia,
                        ic_95_inf, ic_95_sup, p_ttest, sig_holm))

  message("\nDiferencia por módulo:")
  print(tbl_puntajes %>%
          dplyr::select(modulo, diferencia, p_ttest, p_holm, sig_holm))

  list(
    resumen       = tbl_resumen,
    tabla3        = tbl3,
    puntajes      = tbl_puntajes,
    por_depto     = tbl_depto,
    frecuencias   = freqs
  )
}

# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================
if (!interactive()) {
  df <- readRDS("data/processed/datos_analisis.rds")
  resultados_desc <- analisis_descriptivo(df)
}
