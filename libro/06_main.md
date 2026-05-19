# Capítulo 6 — `main.py`

> El módulo más corto del proyecto: un **orquestador** que encadena los
> otros tres en el orden correcto.

---

## 6.1 Propósito del archivo

`main.py` no contiene lógica analítica nueva. Su responsabilidad es:

1. Importar los puntos de entrada de los otros tres módulos.
2. Permitir ejecutar todo el pipeline en una sola llamada.
3. Ofrecer banderas de CLI (`--solo`, `--saltar-preparar`) para
   ejecuciones parciales (útil cuando ya tienes `procesados/` y sólo
   quieres re-correr el análisis).

---

## 6.2 Cabecera

```python
"""
==============================================================================
main.py
==============================================================================
Orquestador único de la investigación:

    "Disparidades en el desempeño Saber Pro y su asociación con el período
     de adopción de IA Generativa (2021-2024)"

Ejecuta, en orden, los tres módulos del proyecto:

    1. preparar_datos.ejecutar_pipeline       — limpia DataICFES (2021-2024).
    2. analisis_descriptivo.ejecutar_…        — Parte 1: bivariado (§9).
    3. regresion_mco.ejecutar_regresion       — Parte 2: 18 modelos MCO.
==============================================================================
"""
```

Docstring de módulo (cadena de documentación).

---

## 6.3 Imports

```python
from __future__ import annotations

import argparse
from typing import Iterable, Optional

from preparar_datos import (
    ejecutar_pipeline, ANIOS, _registrar,
    RUTA_DEFECTO, setup_colab,
)
from analisis_descriptivo import ejecutar_analisis_descriptivo
from regresion_mco import ejecutar_regresion
```

| Línea | Significado |
|---|---|
| `from __future__ import annotations` | Anotaciones diferidas (cap. 1). |
| `import argparse` | Para la CLI. |
| `from typing import Iterable, Optional` | Anotaciones de tipo. |
| `from preparar_datos import (...)` | Importa **cinco** nombres: la función orquestadora, la lista de años, el logger, la ruta por defecto y `setup_colab`. |
| `from analisis_descriptivo import ejecutar_analisis_descriptivo` | Punto de entrada de la Parte 1. |
| `from regresion_mco import ejecutar_regresion` | Punto de entrada de la Parte 2. |

**Por qué importar de los otros módulos**: Python lee los archivos
sólo una vez. Al importar `ejecutar_pipeline`, también se ejecuta el
código top-level de `preparar_datos.py` (incluidas sus constantes y
funciones, que ahora son accesibles aquí).

---

## 6.4 Función `ejecutar_todo`

```python
def ejecutar_todo(
    ruta_proyecto: Optional[str] = None,
    anios: Iterable[int] = ANIOS,
    correr_preparar: bool = True,
    correr_descriptivo: bool = True,
    correr_regresion: bool = True,
) -> None:
    """Ejecuta los tres módulos según las banderas. En Colab, `ruta=None`
    monta Drive y usa `Mi unidad/IA_EDUCACION_SUPERIOR` automáticamente."""
    _registrar("===== PIPELINE COMPLETO DE LA INVESTIGACIÓN =====")
    if ruta_proyecto is None:
        setup_colab()
        ruta_proyecto = RUTA_DEFECTO
    if correr_preparar:
        ejecutar_pipeline(ruta_proyecto=ruta_proyecto, anios=anios)
    if correr_descriptivo:
        ejecutar_analisis_descriptivo(ruta_proyecto=ruta_proyecto)
    if correr_regresion:
        ejecutar_regresion(ruta_proyecto=ruta_proyecto)
    _registrar("===== FIN DEL PIPELINE COMPLETO =====")
```

| Elemento | Significado |
|---|---|
| `ruta_proyecto: Optional[str] = None` | Si `None`, comportamiento Colab. |
| `anios: Iterable[int] = ANIOS` | Acepta cualquier iterable (lista, tupla, range, generador). |
| `correr_preparar: bool = True` | Bandera para saltar/incluir cada parte. |
| `-> None` | No retorna nada explícito; los efectos quedan en disco. |
| `if ruta_proyecto is None:` | Comparación de identidad. |
| `setup_colab()` | Importado de `preparar_datos`: instala deps + monta Drive si aplica. |
| `if correr_preparar:` | Sólo ejecuta esa fase si la bandera está `True`. |

---

## 6.5 CLI con `argparse`

### `_parser()`

```python
def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Orquestador completo (preparación + descriptivo + regresión).",
    )
    p.add_argument("--ruta", "-r", default=None,
                   help="Carpeta del proyecto con los `.txt` de DataICFES. "
                        "Omitir en Colab para usar `Mi unidad/IA_EDUCACION_SUPERIOR`.")
    p.add_argument("--anios", "-a", nargs="+", type=int, default=ANIOS,
                   help="Años a procesar.")
    p.add_argument("--solo", choices=["preparar", "descriptivo", "regresion"],
                   default=None,
                   help="Si se indica, ejecuta solo ese módulo.")
    p.add_argument("--saltar-preparar", action="store_true",
                   help="No vuelve a generar `procesados/`; usa el existente.")
    return p
```

| Argumento | Tipo | Propósito |
|---|---|---|
| `--ruta` / `-r` | str (opcional) | Carpeta del proyecto. |
| `--anios` / `-a` | lista de int | Años a procesar (default 2021-2024). |
| `--solo` | choice | Limita a un solo módulo. |
| `--saltar-preparar` | flag | Reutiliza el `procesados/` existente. |

### Bloque `__main__`

```python
if __name__ == "__main__":
    args = _parser().parse_args()
    correr_prep = correr_desc = correr_reg = True
    if args.solo == "preparar":
        correr_desc = correr_reg = False
    elif args.solo == "descriptivo":
        correr_prep = correr_reg = False
    elif args.solo == "regresion":
        correr_prep = correr_desc = False
    if args.saltar_preparar:
        correr_prep = False
    ejecutar_todo(
        ruta_proyecto=args.ruta, anios=args.anios,
        correr_preparar=correr_prep,
        correr_descriptivo=correr_desc,
        correr_regresion=correr_reg,
    )
```

| Elemento | Significado |
|---|---|
| `correr_prep = correr_desc = correr_reg = True` | **Asignación múltiple**: las tres variables apuntan al mismo valor (`True`). |
| Cascada `if / elif` | Sólo una rama se ejecuta. Si `args.solo == "preparar"`, sólo `correr_prep` queda `True`. |
| `if args.saltar_preparar:` | Sobrescribe `correr_prep` a `False` (compatible con `--solo`). |
| `ejecutar_todo(...)` | Llama al orquestador con las banderas resueltas. |

---

## 6.6 Ejemplos de uso

| Comando | Qué hace |
|---|---|
| `python main.py` | (En Colab) ejecuta todo usando la ruta por defecto. |
| `python main.py --ruta /carpeta` | Ejecuta todo con la ruta dada. |
| `python main.py --solo descriptivo` | Sólo Parte 1, reusando `procesados/`. |
| `python main.py --solo regresion` | Sólo Parte 2. |
| `python main.py --saltar-preparar` | Descriptivo + regresión, sin re-generar `procesados/`. |
| `python main.py --anios 2021 2022 2023` | Procesa solo tres años. |

---

## 6.7 Recapitulación

Al terminar este capítulo deberías poder:

1. Saber que `main.py` es **sólo orquestación**, sin lógica nueva.
2. Entender las banderas `--solo` y `--saltar-preparar`.
3. Reconocer el patrón de **asignación múltiple**.
4. Identificar el **import de varios nombres** con
   `from módulo import (a, b, c, ...)`.

Pasa al [Capítulo 7 — Notebooks Colab](./07_notebooks_colab.md) para
entender los `.ipynb`.
