# =============================================================================
# 01_preparar_datos.R — Carga, depuración y construcción de variables
# Investigación: IA Generativa y Saber Pro — Eduardo A. Victoria Cadena
# =============================================================================
# Fuente: DataICFES (https://www.icfes.gov.co/data-icfes/)
# Los archivos deben descargarse manualmente para cada año (2021, 2022, 2023, 2024)
# y depositarse en data/raw/ con el nombre: saberpro_YYYY.csv (o .sav / .xlsx)
# =============================================================================

source("R/utils.R")
cargar_paquetes()

# =============================================================================
# 1. CARGA DE MICRODATOS
# =============================================================================
# DataICFES publica los archivos en formato .sav (SPSS) o .xlsx por año.
# Esta función unifica los cuatro archivos anuales en un solo data frame.

cargar_datos_brutos <- function(ruta_raw = "data/raw") {

  archivos <- list.files(ruta_raw, pattern = "saberpro_\\d{4}\\.(csv|sav|xlsx)$",
                         full.names = TRUE)

  if (length(archivos) == 0) {
    stop(
      "No se encontraron archivos en '", ruta_raw, "'.\n",
      "Descargue los microdatos Saber Pro 2021-2024 de DataICFES y ubíquelos como:\n",
      "  data/raw/saberpro_2021.csv (o .sav / .xlsx)\n",
      "  data/raw/saberpro_2022.csv\n",
      "  data/raw/saberpro_2023.csv\n",
      "  data/raw/saberpro_2024.csv"
    )
  }

  lista <- purrr::map(archivos, function(f) {
    ext <- tools::file_ext(f)
    df  <- switch(ext,
      csv  = readr::read_csv(f, locale = readr::locale(encoding = "UTF-8"),
                             show_col_types = FALSE),
      sav  = haven::read_sav(f),
      xlsx = readxl::read_excel(f),
      stop("Formato no soportado: ", ext)
    )
    # Extraer año del nombre del archivo
    anio <- as.integer(stringr::str_extract(basename(f), "\\d{4}"))
    df %>% dplyr::mutate(ANIO_APLICACION = anio)
  })

  dplyr::bind_rows(lista)
}

# =============================================================================
# 2. MAPEO DE NOMBRES DE COLUMNAS (DataICFES → nombres internos)
# =============================================================================
# Los nombres de columna pueden variar entre versiones del diccionario ICFES.
# Este bloque estandariza los nombres. Ajustar si el diccionario cambia.

mapear_columnas <- function(df) {

  # Diccionario: nombre_en_DataICFES = nombre_interno
  mapa <- c(
    # Puntajes módulos genéricos
    "MOD_LECTURA_CRITICA_PUNT"  = "punt_lectura_critica",
    "MOD_RAZONA_CUANTITAT_PUNT" = "punt_razona_cuant",
    "MOD_COMPETEN_CIUDADA_PUNT" = "punt_competen_ciud",
    "MOD_COMUNI_ESCRITA_PUNT"   = "punt_comuni_escrita",
    "MOD_INGLES_PUNT"           = "punt_ingles",
    # Identificación estudiante e institución
    "ESTU_CONSECUTIVO"          = "id_estudiante",
    "ESTU_INST_NOMBRE"          = "nombre_ies",
    "INST_ORIGEN"               = "naturaleza_ies_raw",
    "INST_MUNICIPIO_NOMBRE"     = "municipio_ies",
    "INST_DEPARTAMENTO_NOMBRE"  = "departamento_ies",
    "ESTU_PRGM_ACADEMICO"       = "programa_academico",
    # Características socioeconómicas
    "FAMI_ESTRATOVIVIENDA"      = "estrato_raw",
    "ESTU_GENERO"               = "genero_raw",
    "FAMI_EDUCACIONPADRE"       = "nivel_educ_padre_raw",
    "ESTU_HORASSEMANATRABAJA"   = "horas_trabaja_raw",
    "ESTU_PAGOMATRICULAPADRES"  = "pago_matricula_raw",
    "FAMI_TIENEINTERNET"        = "internet_raw",
    "ESTU_AREARESIDE"           = "area_residencia_raw",
    # Puntaje Saber 11
    "ESTU_PUNTAJE_GLOBAL"       = "puntaje_saber11"
  )

  # Nombres presentes en el data frame (insensible a mayúsculas)
  nombres_df   <- toupper(names(df))
  mapa_nombres <- toupper(names(mapa))

  for (i in seq_along(mapa)) {
    idx <- which(nombres_df == mapa_nombres[i])
    if (length(idx) == 1) {
      names(df)[idx] <- mapa[i]
    }
  }
  df
}

# =============================================================================
# 3. FILTRO DE MUESTRA
# =============================================================================
filtrar_muestra <- function(df) {

  # Normalizar texto para comparaciones
  df <- df %>%
    dplyr::mutate(
      nombre_ies_upper       = toupper(stringr::str_squish(nombre_ies)),
      programa_upper         = toupper(stringr::str_squish(programa_academico)),
      departamento_ies_upper = toupper(stringr::str_squish(departamento_ies))
    )

  ies_patron     <- paste(toupper(IES_MUESTRA), collapse = "|")
  programas_patron <- paste(toupper(PROGRAMAS_MUESTRA), collapse = "|")
  anos_validos   <- c(ANOS_PREVIO, ANOS_IA)

  df %>%
    dplyr::filter(
      stringr::str_detect(nombre_ies_upper, ies_patron),
      stringr::str_detect(programa_upper, programas_patron),
      ANIO_APLICACION %in% anos_validos
    )
}

# =============================================================================
# 4. CONSTRUCCIÓN DE VARIABLES
# =============================================================================
construir_variables <- function(df) {

  df %>%

    # --- Variable de interés: período IA ---
    dplyr::mutate(
      periodo_ia = dplyr::if_else(ANIO_APLICACION %in% ANOS_IA, 1L, 0L)
    ) %>%

    # --- Estrato (numérico 1-6) ---
    dplyr::mutate(
      estrato = dplyr::case_when(
        stringr::str_detect(estrato_raw, "Sin estrato|0") ~ NA_real_,
        stringr::str_detect(estrato_raw, "1")  ~ 1,
        stringr::str_detect(estrato_raw, "2")  ~ 2,
        stringr::str_detect(estrato_raw, "3")  ~ 3,
        stringr::str_detect(estrato_raw, "4")  ~ 4,
        stringr::str_detect(estrato_raw, "5")  ~ 5,
        stringr::str_detect(estrato_raw, "6")  ~ 6,
        is.numeric(estrato_raw)                ~ as.numeric(estrato_raw),
        TRUE                                   ~ NA_real_
      )
    ) %>%

    # --- Género (0 = Femenino, 1 = Masculino) ---
    dplyr::mutate(
      genero = dplyr::case_when(
        toupper(genero_raw) %in% c("M", "MASCULINO", "HOMBRE") ~ 1L,
        toupper(genero_raw) %in% c("F", "FEMENINO",  "MUJER")  ~ 0L,
        TRUE ~ NA_integer_
      )
    ) %>%

    # --- Nivel educativo del padre (ordinal numérico) ---
    # Categorías aproximadas del ICFES (verificar diccionario)
    dplyr::mutate(
      nivel_educ_padre = dplyr::case_when(
        stringr::str_detect(toupper(nivel_educ_padre_raw),
                            "NINGUNO|PRIMARIA INCOMPLETA")            ~ 1,
        stringr::str_detect(toupper(nivel_educ_padre_raw),
                            "PRIMARIA COMPLETA")                      ~ 2,
        stringr::str_detect(toupper(nivel_educ_padre_raw),
                            "SECUNDARIA INCOMPLETA|BACHILLERATO INC") ~ 3,
        stringr::str_detect(toupper(nivel_educ_padre_raw),
                            "SECUNDARIA COMPLETA|BACHILLERATO COMP")  ~ 4,
        stringr::str_detect(toupper(nivel_educ_padre_raw),
                            "TECNICA|TECNOLOGICA|TECNICO")            ~ 5,
        stringr::str_detect(toupper(nivel_educ_padre_raw),
                            "UNIVERSITARIA|PROFESIONAL")              ~ 6,
        stringr::str_detect(toupper(nivel_educ_padre_raw),
                            "POSTGRADO|ESPECIALIZACION|MAESTRIA|DOCTORADO") ~ 7,
        TRUE ~ NA_real_
      )
    ) %>%

    # --- Trabaja (0 = no trabaja, 1 = trabaja) ---
    dplyr::mutate(
      estu_trabaja = dplyr::case_when(
        horas_trabaja_raw %in% c("0", "No trabaja", "0 horas") ~ 0L,
        is.na(horas_trabaja_raw) ~ NA_integer_,
        TRUE ~ 1L
      )
    ) %>%

    # --- Cabeza de familia (proxy: estudiante paga su matrícula) ---
    dplyr::mutate(
      estu_cabeza_familia = dplyr::case_when(
        stringr::str_detect(toupper(pago_matricula_raw),
                            "EL MISMO|PROPIO|ESTUDIANTE") ~ 1L,
        is.na(pago_matricula_raw) ~ NA_integer_,
        TRUE ~ 0L
      )
    ) %>%

    # --- Jornada (0 = diurna, 1 = nocturna) ---
    # Se aproxima con el campo de programa si está disponible; si no, se omite
    # dplyr::mutate(jornada = ...) — requiere campo específico en DataICFES

    # --- Internet en el hogar (0 = sin acceso, 1 = con acceso) ---
    dplyr::mutate(
      internet = dplyr::case_when(
        toupper(internet_raw) %in% c("SI", "SÍ", "S") ~ 1L,
        toupper(internet_raw) %in% c("NO", "N")        ~ 0L,
        TRUE ~ NA_integer_
      )
    ) %>%

    # --- Área de residencia (0 = rural, 1 = urbana) ---
    dplyr::mutate(
      area_residencia = dplyr::case_when(
        toupper(area_residencia_raw) %in% c("URBANA", "CABECERA") ~ 1L,
        toupper(area_residencia_raw) %in% c("RURAL", "CENTRO POBLADO",
                                            "RURAL DISPERSO")     ~ 0L,
        TRUE ~ NA_integer_
      )
    ) %>%

    # --- Naturaleza IES (0 = pública, 1 = privada) ---
    dplyr::mutate(
      naturaleza_ies = dplyr::case_when(
        toupper(naturaleza_ies_raw) %in% c("OFICIAL", "PUBLICA") ~ 0L,
        toupper(naturaleza_ies_raw) == "PRIVADA"                  ~ 1L,
        TRUE ~ NA_integer_
      )
    ) %>%

    # --- Departamento de la IES ---
    dplyr::mutate(
      depto_ies = dplyr::case_when(
        stringr::str_detect(departamento_ies_upper, "BOGOT")     ~ "BOGOTA",
        stringr::str_detect(departamento_ies_upper, "ANTIOQUIA") ~ "ANTIOQUIA",
        stringr::str_detect(departamento_ies_upper, "VALLE")     ~ "VALLE",
        stringr::str_detect(departamento_ies_upper, "HUILA")     ~ "HUILA",
        stringr::str_detect(departamento_ies_upper, "NARI")      ~ "NARINO",
        stringr::str_detect(departamento_ies_upper, "TOLIMA")    ~ "TOLIMA",
        TRUE ~ "OTRO"
      )
    ) %>%

    # --- Dummies departamentales (base = Bogotá D.C.) ---
    dplyr::mutate(
      d_antioquia = as.integer(depto_ies == "ANTIOQUIA"),
      d_valle     = as.integer(depto_ies == "VALLE"),
      d_huila     = as.integer(depto_ies == "HUILA"),
      d_narino    = as.integer(depto_ies == "NARINO"),
      d_tolima    = as.integer(depto_ies == "TOLIMA")
    ) %>%

    # --- Distancia a Bogotá (km, lookup table) ---
    dplyr::mutate(
      distancia_bogota_km = dplyr::recode(depto_ies, !!!DISTANCIAS_BOGOTA,
                                           .default = NA_real_)
    ) %>%

    # --- Puntaje genérico agregado ---
    calcular_puntaje_generico()
}

# =============================================================================
# 5. DEPURACIÓN FINAL
# =============================================================================
depurar_datos <- function(df) {

  vars_analisis <- c(
    "id_estudiante", "ANIO_APLICACION", "nombre_ies", "programa_academico",
    "depto_ies", "departamento_ies",
    "puntaje_saberpro_generico",
    MODULOS_GENERICOS,
    "periodo_ia", "estrato", "genero", "nivel_educ_padre",
    "estu_trabaja", "estu_cabeza_familia",
    "internet", "area_residencia", "naturaleza_ies",
    "puntaje_saber11",
    "d_antioquia", "d_valle", "d_huila", "d_narino", "d_tolima",
    "distancia_bogota_km"
  )

  # Seleccionar sólo las vars disponibles
  vars_presentes <- intersect(vars_analisis, names(df))
  df <- df %>% dplyr::select(dplyr::all_of(vars_presentes))

  # Eliminar observaciones sin puntaje genérico
  antes <- nrow(df)
  df <- df %>% dplyr::filter(!is.na(puntaje_saberpro_generico))
  message(sprintf("Observaciones eliminadas por NA en puntaje genérico: %d", antes - nrow(df)))

  # Verificar rango de puntajes (ICFES escala 0-300)
  df <- df %>%
    dplyr::filter(
      dplyr::if_all(
        dplyr::all_of(intersect(MODULOS_GENERICOS, names(df))),
        ~ dplyr::between(., 0, 300) | is.na(.)
      )
    )

  message(sprintf("Observaciones finales en muestra: %d", nrow(df)))
  message(sprintf("Distribución por año:\n%s",
    paste(capture.output(print(table(df$ANIO_APLICACION))), collapse = "\n")))
  message(sprintf("Distribución por departamento:\n%s",
    paste(capture.output(print(table(df$depto_ies))), collapse = "\n")))

  df
}

# =============================================================================
# 6. FUNCIÓN PRINCIPAL
# =============================================================================
preparar_datos <- function(ruta_raw = "data/raw",
                            ruta_processed = "data/processed") {

  message("=== PASO 1: Cargando datos brutos ===")
  datos_brutos <- cargar_datos_brutos(ruta_raw)
  message(sprintf("Filas cargadas (todos los años): %d", nrow(datos_brutos)))

  message("\n=== PASO 2: Mapeando columnas ===")
  datos_mapeados <- mapear_columnas(datos_brutos)

  message("\n=== PASO 3: Filtrando muestra (IES + programas + años) ===")
  datos_filtrados <- filtrar_muestra(datos_mapeados)
  message(sprintf("Filas tras filtro: %d", nrow(datos_filtrados)))

  message("\n=== PASO 4: Construyendo variables ===")
  datos_construidos <- construir_variables(datos_filtrados)

  message("\n=== PASO 5: Depuración final ===")
  datos_finales <- depurar_datos(datos_construidos)

  message("\n=== PASO 6: Guardando datos procesados ===")
  dir.create(ruta_processed, showWarnings = FALSE, recursive = TRUE)
  saveRDS(datos_finales, file.path(ruta_processed, "datos_analisis.rds"))
  readr::write_csv(datos_finales, file.path(ruta_processed, "datos_analisis.csv"))
  message("Datos guardados en: ", ruta_processed)

  datos_finales
}

# =============================================================================
# 7. DATOS SIMULADOS PARA PRUEBA (si no hay DataICFES disponible aún)
# =============================================================================
# Esta función genera datos sintéticos con la misma estructura para
# probar los scripts sin esperar a la descarga oficial de DataICFES.
# NO usar para resultados finales.
generar_datos_simulados <- function(n = 3000, semilla = 42) {

  set.seed(semilla)

  deptos <- c("BOGOTA", "ANTIOQUIA", "VALLE", "HUILA", "NARINO", "TOLIMA")
  dist_depto <- DISTANCIAS_BOGOTA[deptos]

  ies_por_depto <- list(
    BOGOTA    = c("UNIVERSIDAD NACIONAL DE COLOMBIA",
                  "UNIVERSIDAD DISTRITAL FRANCISCO JOSE DE CALDAS"),
    ANTIOQUIA = "UNIVERSIDAD DE ANTIOQUIA",
    VALLE     = "UNIVERSIDAD DEL VALLE",
    HUILA     = "UNIVERSIDAD SURCOLOMBIANA",
    NARINO    = "UNIVERSIDAD DE NARINO",
    TOLIMA    = "UNIVERSIDAD DEL TOLIMA"
  )

  # Distribución de observaciones por departamento (aprox. proporcional al tamaño)
  prob_depto <- c(0.30, 0.20, 0.20, 0.12, 0.10, 0.08)

  tibble::tibble(
    id_estudiante   = seq_len(n),
    ANIO_APLICACION = sample(c(2021:2024), n, replace = TRUE,
                             prob = c(0.25, 0.25, 0.25, 0.25)),
    depto_ies       = sample(deptos, n, replace = TRUE, prob = prob_depto)
  ) %>%
    dplyr::mutate(
      nombre_ies = purrr::map_chr(depto_ies, function(d) {
        ies <- ies_por_depto[[d]]
        sample(ies, 1)
      }),
      programa_academico = sample(
        c("ECONOMIA", "ADMINISTRACION DE EMPRESAS", "CONTADURIA PUBLICA"),
        n, replace = TRUE, prob = c(0.25, 0.45, 0.30)
      ),
      periodo_ia       = as.integer(ANIO_APLICACION %in% ANOS_IA),
      estrato          = sample(1:6, n, replace = TRUE,
                                prob = c(0.10, 0.25, 0.30, 0.20, 0.10, 0.05)),
      genero           = rbinom(n, 1, 0.48),
      nivel_educ_padre = sample(1:7, n, replace = TRUE,
                                prob = c(0.05,0.10,0.15,0.30,0.18,0.15,0.07)),
      estu_trabaja     = rbinom(n, 1, 0.40),
      estu_cabeza_familia = rbinom(n, 1, 0.15),
      internet         = rbinom(n, 1, 0.82),
      area_residencia  = rbinom(n, 1, 0.78),
      naturaleza_ies   = as.integer(depto_ies == "BOGOTA" &
                                      nombre_ies == "PRIVADA"),
      puntaje_saber11  = rnorm(n, 280, 45),
      distancia_bogota_km = DISTANCIAS_BOGOTA[depto_ies],
      d_antioquia      = as.integer(depto_ies == "ANTIOQUIA"),
      d_valle          = as.integer(depto_ies == "VALLE"),
      d_huila          = as.integer(depto_ies == "HUILA"),
      d_narino         = as.integer(depto_ies == "NARINO"),
      d_tolima         = as.integer(depto_ies == "TOLIMA")
    ) %>%
    dplyr::mutate(
      # Puntajes simulados con efectos plausibles
      efecto_ia    = -2.5 * periodo_ia,
      efecto_estrato = 3.0 * estrato,
      efecto_depto = dplyr::recode(depto_ies,
        BOGOTA    = 0, ANTIOQUIA = -4, VALLE = -5,
        HUILA     = -9, NARINO = -14, TOLIMA = -7),
      efecto_dist  = -0.008 * distancia_bogota_km,
      base_score   = 145 + efecto_ia + efecto_estrato + efecto_depto +
                     0.05 * (puntaje_saber11 - 280),
      punt_lectura_critica  = pmax(0, pmin(300, base_score + rnorm(n, 0, 12))),
      punt_razona_cuant     = pmax(0, pmin(300, base_score - 5 + rnorm(n, 0, 15))),
      punt_competen_ciud    = pmax(0, pmin(300, base_score + 2 + rnorm(n, 0, 11))),
      punt_comuni_escrita   = pmax(0, pmin(300, base_score + 1 + rnorm(n, 0, 13))),
      punt_ingles           = pmax(0, pmin(300, base_score - 8 + rnorm(n, 0, 20))),
      puntaje_saberpro_generico = (punt_lectura_critica + punt_razona_cuant +
                                     punt_competen_ciud + punt_comuni_escrita +
                                     punt_ingles) / 5
    ) %>%
    dplyr::select(-efecto_ia, -efecto_estrato, -efecto_depto,
                  -efecto_dist, -base_score)
}

# =============================================================================
# EJECUCIÓN DIRECTA (si se llama como script)
# =============================================================================
if (!interactive()) {
  # Si hay datos reales, usar preparar_datos(); si no, usar simulados
  if (length(list.files("data/raw", pattern = "saberpro_\\d{4}")) > 0) {
    df <- preparar_datos()
  } else {
    message("ADVERTENCIA: No se encontraron datos en data/raw/")
    message("Usando datos SIMULADOS para prueba. NO utilizar para resultados finales.")
    df <- generar_datos_simulados(n = 3000)
    saveRDS(df, "data/processed/datos_analisis.rds")
    readr::write_csv(df, "data/processed/datos_analisis.csv")
  }
}
