# =============================================================================
# 00_main.R — Script principal de orquestación
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# Universidad Surcolombiana — Facultad de Economía y Administración, 2026
# =============================================================================
#
# INSTRUCCIONES DE USO:
# 1. Descargue los microdatos Saber Pro (2021, 2022, 2023, 2024) desde:
#    https://www.icfes.gov.co/data-icfes/
#    Guárdelos en data/raw/ con los nombres:
#      saberpro_2021.csv  (o .sav / .xlsx)
#      saberpro_2022.csv
#      saberpro_2023.csv
#      saberpro_2024.csv
#
# 2. Ejecute este script desde la raíz del proyecto:
#    source("R/00_main.R")
#    o desde terminal: Rscript R/00_main.R
#
# NOTA: Si no tiene los datos disponibles, el script detectará la ausencia
# y generará datos SIMULADOS para probar el flujo completo.
# Los resultados con datos simulados NO son válidos para el artículo.
# =============================================================================

cat("================================================================================\n")
cat("  DISPARIDADES SABER PRO Y ADOPCIÓN DE IA GENERATIVA (2021-2024)\n")
cat("  Eduardo Andrés Victoria Cadena — Universidad Surcolombiana\n")
cat("================================================================================\n\n")

# Establecer directorio de trabajo en la raíz del proyecto
# (Ajustar si se ejecuta desde otra ubicación)
if (file.exists("R/utils.R")) {
  # ya estamos en la raíz
} else if (file.exists("../R/utils.R")) {
  setwd("..")
} else {
  stop("Ejecute este script desde la raíz del proyecto.")
}

# =============================================================================
# PASO 0: Verificar e instalar paquetes
# =============================================================================
cat("--- Verificando paquetes requeridos ---\n")
source("R/utils.R")
cargar_paquetes()

# =============================================================================
# PASO 1: Preparación de datos
# =============================================================================
cat("\n--- PASO 1: Preparación de datos ---\n")
source("R/01_preparar_datos.R")

datos_en_raw <- length(list.files("data/raw", pattern = "saberpro_\\d{4}")) > 0

if (datos_en_raw) {
  cat("Datos reales detectados en data/raw/. Procesando...\n")
  df <- preparar_datos()
} else {
  cat("ADVERTENCIA: No se encontraron datos en data/raw/\n")
  cat("Generando datos SIMULADOS para prueba del flujo.\n")
  cat("Estos datos NO deben usarse para resultados finales.\n\n")
  df <- generar_datos_simulados(n = 3000, semilla = 42)
  dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)
  saveRDS(df, "data/processed/datos_analisis.rds")
  readr::write_csv(df, "data/processed/datos_analisis.csv")
}

cat(sprintf("\nMuestra final: %d estudiantes | %d variables\n",
            nrow(df), ncol(df)))
cat(sprintf("Período pre-IA (2021-2022): n = %d\n",
            sum(df$periodo_ia == 0, na.rm = TRUE)))
cat(sprintf("Período IA    (2023-2024): n = %d\n",
            sum(df$periodo_ia == 1, na.rm = TRUE)))

# =============================================================================
# PASO 2: Análisis descriptivo (Parte 1)
# =============================================================================
cat("\n--- PASO 2: Análisis Descriptivo (Parte 1) ---\n")
source("R/02_analisis_descriptivo.R")

resultados_desc <- analisis_descriptivo(df, guardar = TRUE)

cat("\nTablas guardadas en outputs/tablas/:\n")
cat("  T0_resumen_univariado.csv\n")
cat("  T3_descriptivo_periodos.csv\n")
cat("  T3b_prueba_puntajes.csv\n")
cat("  T_descriptivo_departamento.csv\n")

# =============================================================================
# PASO 3: Regresión MCO (Parte 2)
# =============================================================================
cat("\n--- PASO 3: Regresión Lineal Múltiple MCO (Parte 2) ---\n")
source("R/03_regresion_ols.R")

resultados_reg <- regresion_ols(df, guardar = TRUE)

cat("\nTablas guardadas en outputs/tablas/:\n")
cat("  T4_coeficientes_todos_modelos.csv\n")
cat("  T4b_beta_IA_por_modulo.csv\n")
cat("  T_vif_version_ambas.csv\n")

# =============================================================================
# PASO 4: Diagnósticos
# =============================================================================
cat("\n--- PASO 4: Diagnósticos de los modelos MCO ---\n")
source("R/04_diagnosticos.R")

resultados_diag <- ejecutar_diagnosticos(
  lista_modelos = resultados_reg$modelos,
  tabla4        = resultados_reg$tabla4,
  guardar       = TRUE
)

cat("\nTablas guardadas:\n")
cat("  T_diagnosticos_resumen.csv\n")
cat("  T_correccion_multiplas.csv\n")
cat("  (gráficos de diagnóstico en outputs/figuras/)\n")

# =============================================================================
# PASO 5: Visualizaciones
# =============================================================================
cat("\n--- PASO 5: Generando visualizaciones ---\n")
source("R/05_visualizaciones.R")

generar_visualizaciones(
  df     = df,
  tabla4 = resultados_reg$tabla4,
  guardar = TRUE
)

cat("\nFiguras guardadas en outputs/figuras/:\n")
cat("  F1_boxplot_periodo_depto.png\n")
cat("  F2_histograma_periodos.png\n")
cat("  F3_dispersion_distancia.png\n")
cat("  F4_coefplot_beta_ia.png\n")
cat("  F5_brechas_departamentales.png\n")
cat("  F6_correlaciones.png\n")
cat("  F7_serie_anual_depto.png\n")

# =============================================================================
# PASO 6: Reporte final de resultados clave
# =============================================================================
cat("\n================================================================================\n")
cat("  RESUMEN DE RESULTADOS CLAVE\n")
cat("================================================================================\n\n")

# β_IA
cat("1. Coeficiente β_IA (período de IA generativa):\n")
if (!is.null(resultados_reg$beta_ia)) {
  print(resultados_reg$beta_ia %>%
          dplyr::select(modulo, spec, coef_ic, p_valor))
}

# Corrección por pruebas múltiples
if (!is.null(resultados_diag$correccion_multiplas)) {
  cat("\n2. Corrección por pruebas múltiples (β_IA):\n")
  print(resultados_diag$correccion_multiplas)
}

# Diagnósticos
if (!is.null(resultados_diag$tabla_resumen)) {
  cat("\n3. Diagnósticos del modelo base (puntaje genérico):\n")
  print(resultados_diag$tabla_resumen %>%
          dplyr::filter(grepl("generico", modelo, ignore.case = TRUE)))
}

cat("\n================================================================================\n")
cat("  INTERPRETACIÓN (condicional, NO causal):\n")
cat("  * β_IA > 0 y sig.: asociación positiva con el período de IA.\n")
cat("  * β_IA < 0 y sig.: asociación negativa con el período de IA.\n")
cat("  * Coef. departamental < 0: brecha condicional negativa vs Bogotá D.C.\n")
cat("  * distancia_bogota_km < 0 y sig.: centralización educativa.\n")
cat("================================================================================\n\n")

cat("Análisis completado. Revise outputs/ para tablas y figuras.\n")
