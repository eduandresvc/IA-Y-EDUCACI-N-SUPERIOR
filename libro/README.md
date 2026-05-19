# Libro didáctico — *Análisis de microdatos Saber Pro y su asociación con la IA Generativa*

> **Una guía palabra por palabra del código del proyecto.**
> Eduardo Andrés Victoria Cadena — Universidad Surcolombiana, 2026.

Este libro acompaña el código del proyecto (los cuatro `.py` y los tres
`.ipynb` que viven en `python/`). El objetivo es que un lector sin
formación previa en programación pueda entender **cada palabra, cada
instrucción, cada función, cada librería y cada concepto** que aparece
realmente en esos archivos. Los comentarios del código no se analizan
aquí: el foco está en lo que efectivamente ejecuta el intérprete.

---

## ¿Cómo está organizado el libro?

El libro está dividido en **cuatro partes**, en orden de profundidad
creciente. Si nunca has programado en Python, te sugiero empezar por la
**Parte I** y avanzar capítulo por capítulo. Si ya tienes experiencia,
puedes ir directamente a la **Parte II** y consultar la Parte I como
referencia.

### Parte I — Fundamentos

| Capítulo | Contenido |
|---|---|
| [Cap. 1 — Python básico](./01_python_basico.md) | Palabras reservadas, operadores, sintaxis, tipos, errores comunes. Todo lo que aparece en el código del proyecto. |
| [Cap. 2 — Librerías clave](./02_librerias_clave.md) | `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `argparse`, `unicodedata`, `re`, `os`, `sys`, `datetime`, `typing`, `warnings`, `subprocess`, `importlib`. |

### Parte II — Scripts Python (`.py`)

| Capítulo | Archivo |
|---|---|
| [Cap. 3 — `preparar_datos.py`](./03_preparar_datos.md) | Carga de microdatos DataICFES, construcción de variables y limpieza. |
| [Cap. 4 — `analisis_descriptivo.py`](./04_analisis_descriptivo.md) | Comparación bivariada entre cohortes, Tabla 3 y figuras. |
| [Cap. 5 — `regresion_mco.py`](./05_regresion_mco.md) | 18 modelos MCO, diagnósticos, correcciones por pruebas múltiples. |
| [Cap. 6 — `main.py`](./06_main.md) | Orquestador del pipeline completo. |

### Parte III — Notebooks Colab (`.ipynb`)

| Capítulo | Archivo |
|---|---|
| [Cap. 7 — Notebooks Colab](./07_notebooks_colab.md) | Estructura JSON de un `.ipynb`, mecánica de Google Colab y recorrido por las celdas de `colab_01`, `colab_02` y `colab_03`. |

### Parte IV — Referencias

| Capítulo | Contenido |
|---|---|
| [Cap. 8 — Glosario alfabético](./08_glosario.md) | Definición de todos los términos técnicos del proyecto en orden A-Z. |

---

## Convenciones tipográficas

A lo largo del libro se usan estas convenciones:

- `código`  — un identificador, función o palabra reservada de Python.
- *cursiva* — un concepto técnico que se define o introduce.
- **negrita** — un punto importante.
- `>>>` antes de una línea — entrada interactiva en el REPL.
- `→` separa una expresión de su resultado.

**Ejemplo:**

> `pd.isna(x)` *devuelve* `True` si `x` es `NaN`, `None` o `pd.NA`.
> Si `x = np.nan`, entonces `pd.isna(x)` → `True`.

---

## Cómo usar este libro

1. **Aprendizaje desde cero:** lee de la Parte I a la IV de corrido.
2. **Consulta puntual:** ve directamente al capítulo del archivo que
   estés leyendo. Cada capítulo es autosuficiente y referencia los
   conceptos que necesita.
3. **Búsqueda alfabética:** abre el [glosario](./08_glosario.md) y usa
   `Ctrl+F` para encontrar el término exacto.

---

## Fuentes y prerrequisitos

Para entender por qué cada función del código existe (y no sólo cómo
funciona), revisa:

- **Documento de la investigación:** explica la pregunta empírica, el
  marco teórico, las variables y la metodología.
- **Diccionario DataICFES** (`Diccionario_Examen_Saber_Pro.pdf`):
  describe el significado y los valores posibles de cada campo del
  microdato.
- **`docs/DOCUMENTACION_TECNICA.md`:** resumen técnico de la
  arquitectura del proyecto.

---

¡Bienvenido al libro! Sigue con [Cap. 1 — Python básico](./01_python_basico.md).
