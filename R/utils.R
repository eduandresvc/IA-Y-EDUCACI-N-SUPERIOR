# =============================================================================
# utils.R — Funciones auxiliares compartidas
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# =============================================================================

# -----------------------------------------------------------------------------
# Paquetes requeridos
# -----------------------------------------------------------------------------
paquetes <- c(
  "tidyverse", "haven", "readxl",
  "sandwich", "lmtest", "car", "estimatr",
  "fixest", "modelsummary", "broom",
  "nortest", "tseries",
  "ggplot2", "ggthemes", "patchwork",
  "knitr", "kableExtra", "flextable",
  "scales", "viridis", "corrplot"
)

cargar_paquetes <- function(pkgs = paquetes) {
  faltantes <- pkgs[!pkgs %in% installed.packages()[, "Package"]]
  if (length(faltantes) > 0) {
    message("Instalando paquetes faltantes: ", paste(faltantes, collapse = ", "))
    install.packages(faltantes, dependencies = TRUE)
  }
  invisible(lapply(pkgs, library, character.only = TRUE))
}

# -----------------------------------------------------------------------------
# Constantes del proyecto
# -----------------------------------------------------------------------------

# Nombres exactos de las IES de la muestra (confirmar con DataICFES)
IES_MUESTRA <- c(
  "UNIVERSIDAD NACIONAL DE COLOMBIA",
  "UNIVERSIDAD DISTRITAL FRANCISCO JOSE DE CALDAS",
  "UNIVERSIDAD DE ANTIOQUIA",
  "UNIVERSIDAD DEL VALLE",
  "UNIVERSIDAD SURCOLOMBIANA",
  "UNIVERSIDAD DE NARINO",
  "UNIVERSIDAD DEL TOLIMA"
)

# Programas académicos de interés (confirmar con DataICFES)
PROGRAMAS_MUESTRA <- c(
  "ECONOMIA",
  "ADMINISTRACION DE EMPRESAS",
  "CONTADURIA PUBLICA",
  "ADMINISTRACION",
  "CONTADURIA"
)

# Años de análisis
ANOS_PREVIO <- c(2021, 2022)   # periodo_ia = 0
ANOS_IA     <- c(2023, 2024)   # periodo_ia = 1

# Distancias a Bogotá D.C. por departamento (km por vía terrestre, IGAC/INVIAS)
DISTANCIAS_BOGOTA <- c(
  "BOGOTA"    = 0,
  "ANTIOQUIA" = 415,
  "VALLE"     = 460,
  "TOLIMA"    = 210,
  "HUILA"     = 310,
  "NARINO"    = 785
)

# Módulos genéricos Saber Pro
MODULOS_GENERICOS <- c(
  "punt_lectura_critica",
  "punt_razona_cuant",
  "punt_competen_ciud",
  "punt_comuni_escrita",
  "punt_ingles"
)

MODULOS_ETIQUETAS <- c(
  "punt_lectura_critica" = "Lectura Crítica",
  "punt_razona_cuant"    = "Razonamiento Cuantitativo",
  "punt_competen_ciud"   = "Competencias Ciudadanas",
  "punt_comuni_escrita"  = "Comunicación Escrita",
  "punt_ingles"          = "Inglés"
)

# Nivel de significancia
ALPHA <- 0.05

# -----------------------------------------------------------------------------
# Tema ggplot personalizado
# -----------------------------------------------------------------------------
tema_investigacion <- function() {
  theme_minimal(base_size = 12) +
    theme(
      plot.title    = element_text(face = "bold", size = 13, hjust = 0.5),
      plot.subtitle = element_text(size = 10, hjust = 0.5, color = "gray40"),
      plot.caption  = element_text(size = 8, hjust = 0, color = "gray50"),
      axis.title    = element_text(size = 10),
      legend.position = "bottom",
      panel.grid.minor = element_blank(),
      strip.text = element_text(face = "bold")
    )
}

# -----------------------------------------------------------------------------
# Formateo de p-valores
# -----------------------------------------------------------------------------
fmt_pval <- function(p) {
  dplyr::case_when(
    p < 0.001 ~ "< 0.001***",
    p < 0.01  ~ sprintf("%.3f**", p),
    p < 0.05  ~ sprintf("%.3f*", p),
    p < 0.10  ~ sprintf("%.3f.", p),
    TRUE      ~ sprintf("%.3f", p)
  )
}

# Estrellas de significancia
stars <- function(p) {
  dplyr::case_when(
    p < 0.001 ~ "***",
    p < 0.01  ~ "**",
    p < 0.05  ~ "*",
    p < 0.10  ~ ".",
    TRUE      ~ ""
  )
}

# -----------------------------------------------------------------------------
# Guardar tabla como CSV y RDS
# -----------------------------------------------------------------------------
guardar_tabla <- function(df, nombre, directorio = "outputs/tablas") {
  dir.create(directorio, showWarnings = FALSE, recursive = TRUE)
  readr::write_csv(df, file.path(directorio, paste0(nombre, ".csv")))
  saveRDS(df, file.path(directorio, paste0(nombre, ".rds")))
  message("Tabla guardada: ", nombre)
}

# Guardar figura
guardar_figura <- function(p, nombre, ancho = 10, alto = 7,
                            directorio = "outputs/figuras") {
  dir.create(directorio, showWarnings = FALSE, recursive = TRUE)
  ggplot2::ggsave(
    filename = file.path(directorio, paste0(nombre, ".png")),
    plot = p, width = ancho, height = alto, dpi = 300
  )
  message("Figura guardada: ", nombre)
}

# Guardar modelo
guardar_modelo <- function(modelo, nombre, directorio = "outputs/modelos") {
  dir.create(directorio, showWarnings = FALSE, recursive = TRUE)
  saveRDS(modelo, file.path(directorio, paste0(nombre, ".rds")))
  message("Modelo guardado: ", nombre)
}

# -----------------------------------------------------------------------------
# Calcular puntaje genérico agregado (promedio de 5 módulos)
# -----------------------------------------------------------------------------
calcular_puntaje_generico <- function(df) {
  df %>%
    dplyr::mutate(
      puntaje_saberpro_generico = rowMeans(
        dplyr::select(., dplyr::all_of(MODULOS_GENERICOS)),
        na.rm = TRUE
      )
    )
}

# -----------------------------------------------------------------------------
# Etiquetas legibles para variables
# -----------------------------------------------------------------------------
ETIQUETAS_VARS <- c(
  "puntaje_saberpro_generico" = "Puntaje Genérico (promedio 5 módulos)",
  "punt_lectura_critica"      = "Lectura Crítica",
  "punt_razona_cuant"         = "Razonamiento Cuantitativo",
  "punt_competen_ciud"        = "Competencias Ciudadanas",
  "punt_comuni_escrita"       = "Comunicación Escrita",
  "punt_ingles"               = "Inglés",
  "periodo_ia"                = "Período IA (2023-2024 = 1)",
  "estrato"                   = "Estrato socioeconómico",
  "genero"                    = "Género (Masculino = 1)",
  "nivel_educ_padre"          = "Nivel educativo del padre",
  "estu_trabaja"              = "Trabaja (Sí = 1)",
  "estu_cabeza_familia"       = "Cabeza de familia (aprox.)",
  "jornada"                   = "Jornada nocturna (= 1)",
  "internet"                  = "Acceso a internet (Sí = 1)",
  "area_residencia"           = "Área urbana (= 1)",
  "naturaleza_ies"            = "IES privada (= 1)",
  "puntaje_saber11"           = "Puntaje Saber 11",
  "distancia_bogota_km"       = "Distancia a Bogotá (km)",
  "d_antioquia"               = "Dpto. Antioquia (ref. Bogotá)",
  "d_valle"                   = "Dpto. Valle del Cauca (ref. Bogotá)",
  "d_huila"                   = "Dpto. Huila (ref. Bogotá)",
  "d_narino"                  = "Dpto. Nariño (ref. Bogotá)",
  "d_tolima"                  = "Dpto. Tolima (ref. Bogotá)"
)
