# Capítulo 1 — Python básico

> Todo lo que aparece como palabra reservada, operador o construcción
> sintáctica en los archivos del proyecto, con ejemplos.

---

## 1.1 ¿Qué es Python?

**Python** es un lenguaje de programación interpretado, de tipado
dinámico, multiparadigma (soporta programación imperativa, orientada
a objetos y funcional). En el proyecto se usa la versión **3.10+**.

- **Interpretado:** las instrucciones se ejecutan línea por línea, sin
  necesidad de compilar el código a un binario previamente.
- **Tipado dinámico:** una variable puede contener un entero en una
  línea y una cadena en la siguiente; el tipo se determina en tiempo
  de ejecución.
- **Multiparadigma:** se puede escribir con funciones puras
  (`def func():`), con clases (`class Foo:`), o mezclando ambos.

---

## 1.2 Estructura de un script

Un archivo `.py` se ejecuta de arriba a abajo. La estructura típica de
los archivos del proyecto es:

```python
"""Docstring del módulo: descripción global."""

from __future__ import annotations    # bandera de comportamiento futuro

import os                              # 1) imports de la stdlib
import sys

import numpy as np                     # 2) imports de terceros
import pandas as pd


# ===========================
# 3) Constantes globales
# ===========================
RUTA_DEFECTO: str = "/content/drive/MyDrive/IA_EDUCACION_SUPERIOR"


# ===========================
# 4) Definiciones de funciones
# ===========================
def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"


# ===========================
# 5) Bloque de ejecución
# ===========================
if __name__ == "__main__":
    print(saludar("Eduardo"))
```

---

## 1.3 Palabras reservadas (keywords)

Estas son las palabras que Python reserva para sí. **No puedes usarlas
como nombres de variables.** En el proyecto aparecen las siguientes:

| Palabra | Para qué sirve | Ejemplo |
|---|---|---|
| `def` | Definir una función. | `def f(x):` |
| `return` | Devolver un valor desde una función. | `return x + 1` |
| `if`, `elif`, `else` | Bifurcación condicional. | `if x > 0:` |
| `for` | Bucle iterativo. | `for x in lista:` |
| `while` | Bucle condicional. | `while ok:` |
| `in` | Pertenencia / iteración. | `if x in [1, 2, 3]:` |
| `not` | Negación booleana. | `not True` → `False` |
| `and`, `or` | Y / O lógico. | `a and b` |
| `True`, `False`, `None` | Constantes. | `x = None` |
| `import` | Cargar un módulo. | `import os` |
| `from` | Importar un nombre específico de un módulo. | `from os import path` |
| `as` | Renombrar al importar. | `import numpy as np` |
| `class` | Definir una clase. | `class Foo:` (no se usa mucho en el proyecto). |
| `try`, `except`, `finally` | Manejo de excepciones. | `try: x = 1/0 except: ...` |
| `raise` | Lanzar una excepción. | `raise ValueError(...)` |
| `with` | Gestor de contexto. | `with open(f) as fp:` |
| `pass` | Sentencia vacía. | `def f(): pass` |
| `lambda` | Función anónima. | `lambda x: x**2` |
| `global` | Declarar una variable como global. | `global DEPARTAMENTOS` |
| `is` | Comparación de identidad. | `if x is None:` |
| `assert` | Aserción. | `assert x > 0` |
| `continue` | Saltar a la siguiente iteración. | (dentro de un bucle) |
| `break` | Salir del bucle. | (dentro de un bucle) |
| `yield` | Devolver un generador. | (no se usa mucho en el proyecto). |

---

## 1.4 Operadores

### 1.4.1 Aritméticos

| Operador | Significado | Ejemplo |
|---|---|---|
| `+` | Suma | `2 + 3` → `5` |
| `-` | Resta | `5 - 2` → `3` |
| `*` | Multiplicación | `4 * 3` → `12` |
| `/` | División flotante | `7 / 2` → `3.5` |
| `//` | División entera | `7 // 2` → `3` |
| `%` | Módulo (resto) | `7 % 2` → `1` |
| `**` | Potencia | `2 ** 3` → `8` |

### 1.4.2 Comparación

| Operador | Significado |
|---|---|
| `==` | Igual |
| `!=` | Distinto |
| `<`, `<=` | Menor / menor o igual |
| `>`, `>=` | Mayor / mayor o igual |
| `is`, `is not` | Identidad de objeto (no de valor) |

> **Importante:** `==` compara *valores*. `is` compara *identidad de
> objeto* (la misma posición en memoria). Para detectar `None` siempre
> se usa `is None`, no `== None`.

### 1.4.3 Booleanos escalares y vectoriales

| Escalar | Vectorial (numpy/pandas) |
|---|---|
| `and` | `&` |
| `or` | `\|` |
| `not` | `~` |

> Los operadores `&`, `\|`, `~` se aplican **elemento a elemento** sobre
> arrays o Series. Cuando aparecen entre paréntesis, los paréntesis son
> obligatorios por precedencia, p. ej. `(df["x"] > 0) & (df["y"] < 1)`.

### 1.4.4 Asignación

| Operador | Equivale a |
|---|---|
| `x = 5` | Asignación simple. |
| `x += 1` | `x = x + 1` |
| `x -= 1` | `x = x - 1` |
| `x *= 2` | `x = x * 2` |
| `a, b = b, a` | Intercambio de valores. |
| `a, b = func()` | Desempaquetado de tupla. |
| `*resto, ultimo = lista` | Desempaquetado con splat. |

### 1.4.5 Pertenencia y membresía

| Construcción | Significado |
|---|---|
| `x in lista` | `True` si `x` aparece en `lista`. |
| `x not in lista` | Negación de lo anterior. |
| `"sub" in "supercadena"` | Subcadena. |
| `"clave" in diccionario` | Clave existe. |

---

## 1.5 Tipos básicos

### 1.5.1 Enteros, flotantes y booleanos

```python
n   = 42          # int
pi  = 3.14159     # float
ok  = True        # bool (en realidad un int 1 o 0)
```

### 1.5.2 Cadenas (`str`)

```python
nombre = "Eduardo"
saludo = 'Hola'         # comillas simples o dobles, equivalentes
varias = """línea 1
línea 2"""              # cadena multilínea (triple comilla)
ruta = r"C:\nuevo"      # raw string: no interpreta \n
plant = f"Hola, {nombre}"   # f-string: interpolación
```

**Métodos de cadena usados en el proyecto:**

| Método | Qué hace |
|---|---|
| `.strip()` | Quita espacios al inicio y al final. |
| `.upper()` / `.lower()` | Mayúsculas / minúsculas. |
| `.replace(a, b)` | Sustituye `a` por `b`. |
| `.startswith(s)` | `True` si empieza con `s`. |
| `.endswith(s)` | `True` si termina con `s`. |
| `.format(...)` | Sustituye `{...}` por argumentos. |
| `.split(sep)` | Divide en lista por `sep`. |
| `.join(iter)` | Concatena un iterable con `sep` entre medio. |

### 1.5.3 Listas (`list`)

```python
xs = [1, 2, 3]
xs.append(4)        # [1, 2, 3, 4]
xs[0]               # 1 (primer elemento)
xs[-1]              # 4 (último elemento)
xs[1:3]             # [2, 3] (slicing)
len(xs)             # 4
xs + [5, 6]         # [1, 2, 3, 4, 5, 6] (concatena)
```

### 1.5.4 Tuplas (`tuple`)

Como listas pero **inmutables** (no se pueden modificar):

```python
t = (1, 2, 3)
t = 1, 2, 3         # paréntesis opcionales
t[0]                # 1
# t.append(4)       # ERROR: tuplas no tienen append
```

### 1.5.5 Diccionarios (`dict`)

```python
d = {"a": 1, "b": 2, "c": 3}
d["a"]              # 1
d["d"] = 4          # agrega clave nueva
"a" in d            # True
d.keys()            # vista de claves
d.values()          # vista de valores
d.items()           # vista de pares (clave, valor)
d.get("z", 0)       # 0 (valor por defecto si no existe)
```

### 1.5.6 Conjuntos (`set`)

```python
s = {1, 2, 3}
s.add(4)
2 in s              # True
```

### 1.5.7 `None`

`None` es un valor especial que indica "ausencia de valor". Se usa como
valor por defecto y se compara con `is`:

```python
x = None
if x is None:
    print("no hay valor")
```

---

## 1.6 Definición y uso de funciones

```python
def saludar(nombre: str = "mundo") -> str:
    """Devuelve un saludo personalizado."""
    return f"Hola, {nombre}"
```

| Elemento | Significado |
|---|---|
| `def` | Palabra reservada para definir. |
| `saludar` | Nombre de la función. |
| `nombre: str = "mundo"` | Parámetro con anotación de tipo y valor por defecto. |
| `-> str` | Anotación del tipo de retorno. |
| `"""..."""` | Docstring (cadena de documentación). |
| `return` | Devuelve el valor al *caller*. |

**Tipos de parámetros:**

- **Posicionales:** se pasan en orden. `saludar("Eduardo")`.
- **Por palabra clave:** se pasan por nombre. `saludar(nombre="Eduardo")`.
- **`*args`:** acepta un número variable de posicionales. Aparece como
  tupla.
- **`**kwargs`:** acepta un número variable de palabras clave. Aparece
  como dict.

### Funciones anónimas (`lambda`)

```python
cuadrado = lambda x: x ** 2
cuadrado(4)         # 16
```

Útiles cuando se necesita una función pequeña como argumento, p. ej.
`serie.apply(lambda v: v.upper())`.

---

## 1.7 Control de flujo

### 1.7.1 Condicional

```python
if x > 0:
    print("positivo")
elif x == 0:
    print("cero")
else:
    print("negativo")
```

### 1.7.2 Expresión ternaria

```python
etiqueta = "ok" if x > 0 else "no_ok"
```

### 1.7.3 Bucle `for`

```python
for elemento in iterable:
    procesar(elemento)
```

Iterar un diccionario produce sus **claves**:

```python
for clave in diccionario:
    print(clave, diccionario[clave])
# Mejor con .items():
for clave, valor in diccionario.items():
    print(clave, valor)
```

### 1.7.4 `enumerate` y `zip`

```python
for i, x in enumerate(["a", "b", "c"]):
    print(i, x)
# 0 a / 1 b / 2 c

for a, b in zip([1, 2, 3], ["x", "y", "z"]):
    print(a, b)
# 1 x / 2 y / 3 z
```

### 1.7.5 `break` y `continue`

```python
for x in xs:
    if x is None:
        continue          # salta esta iteración
    if x == "fin":
        break             # sale del bucle
    procesar(x)
```

---

## 1.8 Comprensiones

Forma idiomática de construir listas, tuplas, diccionarios y conjuntos:

```python
# Lista de cuadrados
cuadrados = [x ** 2 for x in range(10)]

# Lista filtrada
pares = [x for x in xs if x % 2 == 0]

# Diccionario
mapa = {k.upper(): v for k, v in d.items()}

# Conjunto
unicos = {x for x in lista}

# Expresión generadora (no se materializa)
suma = sum(x ** 2 for x in xs)
```

---

## 1.9 Manejo de excepciones

```python
try:
    riesgo()
except (ValueError, TypeError) as exc:
    print(f"Error capturado: {exc}")
    fallback()
except Exception:
    raise                  # re-lanza
finally:
    cierre()               # se ejecuta SIEMPRE
```

| Construcción | Cuándo se ejecuta |
|---|---|
| `try:` | Bloque protegido. |
| `except X:` | Si ocurre una excepción de tipo `X`. |
| `except (X, Y) as e:` | Si ocurre `X` **o** `Y`; captura la excepción en `e`. |
| `else:` | Si NO hubo excepción. |
| `finally:` | Siempre, ocurra o no. |
| `raise` | Lanza una excepción (relanza la actual si está dentro de `except`). |

---

## 1.10 Anotaciones de tipo (`typing`)

Sintaxis declarativa que ayuda a editores y linters. Python las **ignora
en tiempo de ejecución** (a menos que uses `mypy` u otra herramienta).

```python
def f(x: int, y: str = "abc") -> bool:
    ...
```

Tipos comunes (todos importados de `typing`):

| Tipo | Significado |
|---|---|
| `int`, `float`, `bool`, `str` | Tipos primitivos. |
| `List[T]` | Lista de elementos de tipo `T`. |
| `Tuple[A, B]` | Tupla de longitud fija con tipos posicionales. |
| `Dict[K, V]` | Diccionario con claves K y valores V. |
| `Set[T]` | Conjunto de T. |
| `Optional[T]` | `T` o `None`. |
| `Union[A, B]` | `A` o `B`. |
| `Iterable[T]` | Cualquier objeto recorrible (lista, tupla, generador, etc.). |
| `Callable[[A, B], C]` | Función que toma A y B y retorna C. |
| `Any` | Cualquier cosa (escape válido). |

### Forma diferida

`from __future__ import annotations` hace que **todas** las anotaciones
se evalúen como cadenas. Permite referirse a clases definidas más abajo
en el archivo sin causar `NameError`.

---

## 1.11 La variable especial `__name__`

Cuando un archivo `.py` se ejecuta directamente:

```python
print(__name__)     # "__main__"
```

Cuando se importa como módulo:

```python
import miarchivo
print(miarchivo.__name__)   # "miarchivo"
```

Por eso se usa el patrón:

```python
if __name__ == "__main__":
    # esto sólo se ejecuta cuando el archivo se corre directamente
    main()
```

---

## 1.12 Convenciones del proyecto

| Convención | Significado |
|---|---|
| `MAYUSCULAS` | Constante. |
| `_inicial` | Identificador "privado del módulo" (sólo para uso interno). |
| `_` solo | Variable irrelevante (placeholder). |
| `snake_case` | Funciones y variables. |
| `CamelCase` | Clases (raras en el proyecto). |
| `# noqa: …` | Suprime un aviso del linter. |
| `# type: ignore` | Suprime un aviso del verificador de tipos. |

---

## 1.13 Errores comunes y cómo se ven

| Excepción | Causa |
|---|---|
| `SyntaxError` | Error de sintaxis (paréntesis sin cerrar, etc.). |
| `NameError` | Se usa un nombre no definido. |
| `TypeError` | Tipo incorrecto (sumar `str` y `int`). |
| `ValueError` | Valor incorrecto (convertir `"abc"` a int). |
| `KeyError` | Clave no presente en un dict. |
| `IndexError` | Índice fuera de rango en una lista. |
| `AttributeError` | Acceder a un atributo inexistente (`x.foo` cuando `x` no tiene `foo`). |
| `ImportError` / `ModuleNotFoundError` | No se puede importar. |
| `FileNotFoundError` | Ruta inexistente. |
| `ZeroDivisionError` | `x / 0`. |
| `IndentationError` | Indentación incorrecta. |

---

## 1.14 Indentación

Python usa **indentación** (espacios en blanco al inicio de la línea)
para definir bloques. La convención es **4 espacios por nivel**:

```python
def f(x):
    if x > 0:
        return "positivo"
    else:
        return "no_positivo"
```

> No se mezclan tabs y espacios. El proyecto usa **4 espacios siempre**.

---

¡Pasa al [Capítulo 2 — Librerías clave](./02_librerias_clave.md)
para conocer cada librería que el proyecto importa.
