"""
==============================================================================
main.py
==============================================================================
Orquestador único de la investigación:

    "Disparidades en el desempeño Saber Pro y su asociación con el período
     de adopción de IA Generativa (2021-2024)"
    Eduardo Andrés Victoria Cadena — Universidad Surcolombiana, 2026.

Ejecuta, en orden, los tres módulos del proyecto:

    1. preparar_datos.ejecutar_pipeline       — limpia DataICFES (2021-2024).
    2. analisis_descriptivo.ejecutar_…        — Parte 1: bivariado (§9).
    3. regresion_mco.ejecutar_regresion       — Parte 2: 18 modelos MCO (§8, §10).

Uso desde la línea de comandos:

    python main.py --ruta /carpeta/con/los_txt
    python main.py --ruta /carpeta --solo descriptivo
    python main.py --ruta /carpeta --solo regresion --saltar-preparar
==============================================================================
"""

from __future__ import annotations

import argparse
from typing import Iterable

from preparar_datos import ejecutar_pipeline, ANIOS, _registrar
from analisis_descriptivo import ejecutar_analisis_descriptivo
from regresion_mco import ejecutar_regresion


def ejecutar_todo(
    ruta_proyecto: str,
    anios: Iterable[int] = ANIOS,
    correr_preparar: bool = True,
    correr_descriptivo: bool = True,
    correr_regresion: bool = True,
) -> None:
    """Ejecuta los tres módulos del proyecto según las banderas."""
    _registrar("===== PIPELINE COMPLETO DE LA INVESTIGACIÓN =====")
    if correr_preparar:
        ejecutar_pipeline(ruta_proyecto=ruta_proyecto, anios=anios)
    if correr_descriptivo:
        ejecutar_analisis_descriptivo(ruta_proyecto=ruta_proyecto)
    if correr_regresion:
        ejecutar_regresion(ruta_proyecto=ruta_proyecto)
    _registrar("===== FIN DEL PIPELINE COMPLETO =====")


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Orquestador completo (preparación + descriptivo + regresión).",
    )
    p.add_argument("--ruta", "-r", required=True,
                   help="Carpeta del proyecto con los `.txt` de DataICFES.")
    p.add_argument("--anios", "-a", nargs="+", type=int, default=ANIOS,
                   help="Años a procesar.")
    p.add_argument("--solo", choices=["preparar", "descriptivo", "regresion"],
                   default=None,
                   help="Si se indica, ejecuta solo ese módulo.")
    p.add_argument("--saltar-preparar", action="store_true",
                   help="No vuelve a generar `procesados/`; usa el existente.")
    return p


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
