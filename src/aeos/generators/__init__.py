from collections.abc import Callable
from pathlib import Path

from aeos.generators.basic import generate as generate_basic
from aeos.generators.python import generate as generate_python

GeneratorFn = Callable[[Path, str], list[str]]

GENERATORS: dict[str, GeneratorFn] = {
    "basic": generate_basic,
    "python": generate_python,
}
