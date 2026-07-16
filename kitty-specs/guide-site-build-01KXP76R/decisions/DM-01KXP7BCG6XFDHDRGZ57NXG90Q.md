# Decision Moment `01KXP7BCG6XFDHDRGZ57NXG90Q`

- **Mission:** `guide-site-build-01KXP76R`
- **Origin flow:** `plan`
- **Slot key:** `plan.book.pdf-toolchain`
- **Input key:** `pdf_toolchain`
- **Status:** `resolved`
- **Created:** `2026-07-16T19:44:40.454593+00:00`
- **Resolved:** `2026-07-16T19:48:13.909975+00:00`
- **Opened by:** `cli`
- **Other answer:** `false`

## Question

How should the printable PDF be produced: a print-typesetting engine (pandoc/LaTeX) or an HTML-to-PDF renderer that reuses the site's own stylesheet?

## Options

- pandoc-latex
- html-to-pdf
- Other

## Final answer

pandoc-latex: produce the printable PDF with pandoc and a XeLaTeX template. Chosen for print typography quality, accepting a TeX dependency in CI and two independent style systems (site CSS and LaTeX template) that must be kept from drifting.

## Rationale

_(none)_

## Change log

- `2026-07-16T19:44:40.454593+00:00` — opened
- `2026-07-16T19:48:13.909975+00:00` — resolved (final_answer="pandoc-latex: produce the printable PDF with pandoc and a XeLaTeX template. Chosen for print typography quality, accepting a TeX dependency in CI and two independent style systems (site CSS and LaTeX template) that must be kept from drifting.")
