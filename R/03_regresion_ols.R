# =============================================================================
# 03_regresion_ols.R — PARTE 2: Modelos de Regresión Lineal Múltiple (MCO)
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# =============================================================================
# Estima 6 modelos (puntaje genérico + 5 módulos) x 3 especificaciones:
#   Spec 1 (base): sin efectos fijos
#   Spec 2 (ef_ies): efectos fijos por institución
#   Spec 3 (ef_mun): efectos fijos por tipo de municipio
# Errores estándar: HC3 robustos y clusterizados a nivel de IES
# =============================================================================

source("R/utils.R")
cargar_paquetes()

# =============================================================================
# 1. ESPECIFICACIÓN DE LAS ECUACIONES
# =============================================================================

# Variables de control socioeconómicas, académicas e institucionales
CONTROLES <- c(
  "estrato", "genero", "nivel_educ_padre",
  "estu_trabaja", "estu_cabeza_familia",
  "internet", "area_residencia", "naturaleza_ies",
  "puntaje_saber11"
)

# Dummies departamentales (Bogotá = referencia, omitida)
DUMMIES_DEPTO <- c("d_antioquia", "d_valle", "d_huila", "d_narino", "d_tolima")

#' Construye la fórmula para cada modelo
#' @param var_dep  Variable dependiente
#' @param spec     Especificación: "base", "ef_ies", "ef_mun"
#' @param incluir_dist  Incluir distancia_bogota_km
#' @param incluir_dummies Incluir dummies departamentales
construir_formula <- function(var_dep,
                               spec = c("base", "ef_ies", "ef_mun"),
                               incluir_dist   = TRUE,
                               incluir_dummies = TRUE) {
  spec <- match.arg(spec)

  vars_rhs <- c(
    "periodo_ia",
    if (incluir_dummies) DUMMIES_DEPTO,
    if (incluir_dist)    "distancia_bogota_km",
    CONTROLES
  )

  ef <- switch(spec,
    base   = "",
    ef_ies = "| nombre_ies",
    ef_mun = "| area_residencia"
  )

  if (spec == "base") {
    as.formula(paste(var_dep, "~", paste(vars_rhs, collapse = " + ")))
  } else {
    # fixest::feols usa sintaxis con |
    as.formula(paste(var_dep, "~", paste(vars_rhs, collapse = " + "), ef))
  }
}

# =============================================================================
# 2. ESTIMACIÓN MCO CON ERRORES ROBUSTOS
# =============================================================================

#' Estima un modelo OLS con errores HC3 y clusterizados
#' @param df        Data frame
#' @param var_dep   Variable dependiente
#' @param formula   Fórmula del modelo
#' @param spec      "base" | "ef_ies" | "ef_mun"
#' @return Lista con modelo, errores robustos y tabla de coeficientes
estimar_modelo <- function(df, var_dep, formula, spec = "base") {

  # Eliminar NAs en variables del modelo
  vars_modelo <- all.vars(formula)
  vars_modelo <- intersect(vars_modelo, names(df))
  df_limpio   <- df %>% tidyr::drop_na(dplyr::all_of(vars_modelo))

  n_obs <- nrow(df_limpio)
  if (n_obs < 30) {
    warning("Muestra muy pequeña (n=", n_obs, ") para: ", deparse(formula))
    return(NULL)
  }

  resultado <- list(n = n_obs, var_dep = var_dep, spec = spec)

  if (spec == "base") {
    # lm() estándar
    mod <- lm(formula, data = df_limpio)

    # Errores HC3 robustos
    vcov_hc3  <- sandwich::vcovHC(mod, type = "HC3")
    # Errores clusterizados por IES (si la variable está disponible)
    if ("nombre_ies" %in% names(df_limpio)) {
      vcov_cl <- tryCatch(
        sandwich::vcovCL(mod, cluster = ~ nombre_ies),
        error = function(e) vcov_hc3
      )
    } else {
      vcov_cl <- vcov_hc3
    }

    resultado$modelo     <- mod
    resultado$vcov_hc3   <- vcov_hc3
    resultado$vcov_cl    <- vcov_cl
    resultado$coef_hc3   <- lmtest::coeftest(mod, vcov. = vcov_hc3)
    resultado$coef_cl    <- lmtest::coeftest(mod, vcov. = vcov_cl)
    resultado$r2_adj     <- summary(mod)$adj.r.squared
    resultado$aic        <- AIC(mod)
    resultado$bic        <- BIC(mod)

  } else {
    # fixest::feols para modelos con efectos fijos
    if (!requireNamespace("fixest", quietly = TRUE)) {
      stop("Instale el paquete 'fixest' para efectos fijos.")
    }

    # fixest usa su propio manejo de SE
    cluster_var <- if ("nombre_ies" %in% names(df_limpio)) ~ nombre_ies else NULL
    mod <- tryCatch(
      fixest::feols(formula, data = df_limpio,
                    vcov = if (!is.null(cluster_var)) cluster_var else "HC1"),
      error = function(e) {
        warning("Error en feols (", spec, "): ", conditionMessage(e))
        NULL
      }
    )

    if (!is.null(mod)) {
      resultado$modelo   <- mod
      resultado$r2_adj   <- fixest::r2(mod, "ar2")
      resultado$coef_cl  <- summary(mod)
    }
  }

  resultado
}

# =============================================================================
# 3. TABLA DE COEFICIENTES (Tabla 4 del documento)
# =============================================================================

#' Extrae coeficientes y estadísticos en formato Tabla 4
extraer_coeficientes <- function(resultado) {
  if (is.null(resultado)) return(NULL)

  if (resultado$spec == "base") {
    ct <- resultado$coef_cl  # usar errores clusterizados como principal
    tbl <- as.data.frame(ct) %>%
      tibble::rownames_to_column("variable") %>%
      dplyr::rename(
        coef     = Estimate,
        se       = `Std. Error`,
        t_stat   = `t value`,
        p_valor  = `Pr(>|t|)`
      ) %>%
      dplyr::mutate(
        sig      = stars(p_valor),
        ic_95_l  = coef - 1.96 * se,
        ic_95_u  = coef + 1.96 * se,
        var_dep  = resultado$var_dep,
        spec     = resultado$spec,
        n        = resultado$n,
        r2_adj   = round(resultado$r2_adj, 4)
      )
  } else {
    if (!inherits(resultado$modelo, "fixest")) return(NULL)
    tbl <- broom::tidy(resultado$modelo) %>%
      dplyr::rename(
        variable = term,
        coef     = estimate,
        se       = std.error,
        t_stat   = statistic,
        p_valor  = p.value
      ) %>%
      dplyr::mutate(
        sig      = stars(p_valor),
        ic_95_l  = coef - 1.96 * se,
        ic_95_u  = coef + 1.96 * se,
        var_dep  = resultado$var_dep,
        spec     = resultado$spec,
        n        = resultado$n,
        r2_adj   = round(resultado$r2_adj, 4)
      )
  }
  tbl
}

# =============================================================================
# 4. VERSIONES DEL MODELO PARA COLINEALIDAD DIST ~ DUMMIES
# =============================================================================
# La investigación requiere 3 sub-versiones para analizar la colinealidad:
#   (a) solo dummies departamentales (sin distancia)
#   (b) solo distancia_bogota_km (sin dummies)
#   (c) ambas (con diagnóstico FIV)

estimar_tres_versiones_geograficas <- function(df, var_dep) {

  df_limpio <- df %>% tidyr::drop_na(periodo_ia, dplyr::all_of(
    intersect(c(CONTROLES, DUMMIES_DEPTO, "distancia_bogota_km"), names(df))
  ))

  base_rhs <- paste(c("periodo_ia", CONTROLES), collapse = " + ")

  formulas <- list(
    solo_dummies   = as.formula(paste(var_dep, "~", base_rhs, "+",
                                       paste(DUMMIES_DEPTO, collapse = " + "))),
    solo_distancia = as.formula(paste(var_dep, "~", base_rhs,
                                       "+ distancia_bogota_km")),
    ambas          = as.formula(paste(var_dep, "~", base_rhs, "+",
                                       paste(DUMMIES_DEPTO, collapse = " + "),
                                       "+ distancia_bogota_km"))
  )

  purrr::imap(formulas, function(f, nombre) {
    mod <- lm(f, data = df_limpio)
    list(
      nombre   = nombre,
      modelo   = mod,
      vcov_cl  = tryCatch(sandwich::vcovCL(mod, ~ nombre_ies),
                          error = function(e) sandwich::vcovHC(mod, "HC3")),
      vif      = tryCatch(car::vif(mod), error = function(e) NULL),
      r2_adj   = summary(mod)$adj.r.squared
    )
  })
}

# =============================================================================
# 5. TABLA RESUMEN CONSOLIDADA (Tabla 4 completa)
# =============================================================================

construir_tabla4 <- function(lista_modelos) {

  purrr::map_dfr(lista_modelos, function(res) {
    if (is.null(res)) return(NULL)
    extraer_coeficientes(res) %>%
      dplyr::filter(variable %in% c(
        "periodo_ia", "distancia_bogota_km",
        DUMMIES_DEPTO, CONTROLES, "(Intercept)"
      ))
  }) %>%
    dplyr::mutate(
      etiqueta = dplyr::recode(variable, !!!ETIQUETAS_VARS, .default = variable),
      coef_fmt = sprintf("%.3f%s", coef, sig),
      se_fmt   = sprintf("(%.3f)", se)
    ) %>%
    dplyr::select(var_dep, spec, etiqueta, coef, se, t_stat, p_valor,
                  sig, ic_95_l, ic_95_u, n, r2_adj)
}

# =============================================================================
# 6. TABLA PIVOTE: coef β_IA por módulo y especificación
# =============================================================================

tabla_beta_ia <- function(tabla4) {
  tabla4 %>%
    dplyr::filter(grepl("periodo_ia", etiqueta) |
                    etiqueta == "Período IA (2023-2024 = 1)") %>%
    dplyr::select(var_dep, spec, coef, se, t_stat, p_valor, sig, n, r2_adj) %>%
    dplyr::mutate(
      modulo = dplyr::recode(var_dep, !!!ETIQUETAS_VARS, .default = var_dep),
      coef_ic = sprintf("%.3f [%.3f, %.3f]%s",
                        coef,
                        coef - 1.96 * se,
                        coef + 1.96 * se,
                        sig)
    ) %>%
    dplyr::select(modulo, spec, coef_ic, p_valor, n, r2_adj)
}

# =============================================================================
# 7. FUNCIÓN PRINCIPAL
# =============================================================================

regresion_ols <- function(df,
                           guardar = TRUE,
                           dir_tablas = "outputs/tablas",
                           dir_modelos = "outputs/modelos") {

  message("=== PARTE 2: Regresión Lineal Múltiple (MCO) ===\n")

  vars_dep <- c("puntaje_saberpro_generico", MODULOS_GENERICOS)
  vars_dep <- intersect(vars_dep, names(df))
  specs    <- c("base", "ef_ies", "ef_mun")

  todos_modelos <- list()

  # --- Estimar los 6 × 3 modelos ---
  for (vd in vars_dep) {
    for (sp in specs) {
      nombre_mod <- paste0(vd, "_", sp)
      message(sprintf("  Estimando: %s (%s)...", vd, sp))

      f <- tryCatch(
        construir_formula(vd, spec = sp, incluir_dist = TRUE,
                           incluir_dummies = TRUE),
        error = function(e) NULL
      )
      if (is.null(f)) next

      res <- estimar_modelo(df, vd, f, sp)
      todos_modelos[[nombre_mod]] <- res

      if (guardar && !is.null(res)) {
        guardar_modelo(res, nombre_mod, dir_modelos)
      }
    }
  }

  # --- Tabla 4: coeficientes consolidados ---
  message("\nConstruyendo Tabla 4...")
  tabla4 <- construir_tabla4(todos_modelos)
  if (guardar) guardar_tabla(tabla4, "T4_coeficientes_todos_modelos", dir_tablas)

  # --- β_IA resumido por módulo ---
  message("Tabla resumen β_IA...")
  tbl_beta <- tabla_beta_ia(tabla4)
  if (guardar) guardar_tabla(tbl_beta, "T4b_beta_IA_por_modulo", dir_tablas)

  # --- Tres versiones geográficas (solo dummies / solo dist / ambas) ---
  message("\nEstimando versiones geográficas (colinealidad)...")
  versiones_geo <- purrr::map(vars_dep, function(vd) {
    estimar_tres_versiones_geograficas(df, vd)
  }) %>% purrr::set_names(vars_dep)

  # Tabla FIV de cada versión "ambas"
  tbl_vif <- purrr::map_dfr(versiones_geo, function(vg) {
    vif_vals <- vg$ambas$vif
    if (is.null(vif_vals)) return(NULL)
    tibble::enframe(vif_vals, name = "variable", value = "vif") %>%
      dplyr::mutate(vif = round(vif, 2),
                    alerta = vif > 10)
  }, .id = "modulo")

  if (guardar) guardar_tabla(tbl_vif, "T_vif_version_ambas", dir_tablas)

  # --- Imprimir resultados clave ---
  message("\n--- β_IA por módulo y especificación ---")
  print(tbl_beta)

  if (nrow(tbl_vif) > 0) {
    message("\n--- FIV (versión con dummies + distancia) ---")
    print(tbl_vif %>% dplyr::filter(alerta))
  }

  list(
    modelos      = todos_modelos,
    tabla4       = tabla4,
    beta_ia      = tbl_beta,
    versiones_geo = versiones_geo,
    vif_tabla    = tbl_vif
  )
}

# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================
if (!interactive()) {
  df <- readRDS("data/processed/datos_analisis.rds")
  resultados_reg <- regresion_ols(df)
}
