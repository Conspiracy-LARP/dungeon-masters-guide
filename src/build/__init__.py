"""Build machinery for the Dungeon Master's Guide.

`src/pack/` is the product: twelve markdown files. Everything this package does is
*derive* something from them — a site, a book, a PDF, machine-readable indexes, and a
branch creators attach as a submodule.

Two rules hold everywhere in here:

1. **Never write to `src/pack/`.** It is input. The build is forbidden from editing
   prose (C-002) and content is out of scope (C-006). Checks report; they never fix.
2. **The reading order is declared once**, in `mkdocs.yml`'s `nav:`. Every surface reads
   it. A second copy is the exact failure this package exists to prevent.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
