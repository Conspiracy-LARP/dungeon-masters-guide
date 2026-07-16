# Quickstart — working on the guide's build

**Mission**: `guide-site-build-01KXP76R`

For whoever picks up an implementation work package. Read `plan.md` first; this is the orientation that
saves you an hour.

## The one-paragraph model

`src/pack/` holds twelve markdown files. That is the product. Everything else in this mission generates
something from it: a site, a book, a PDF, machine-readable indexes, and a branch creators attach to their
own projects. **You never edit `src/pack/`** — content is out of scope (C-006), and the build is
forbidden from touching prose (C-002). If the build seems to need a prose change, that is a finding to
escalate, not a fix to make.

## Setup

```bash
poetry install                       # MkDocs + Material, PyYAML, click, dev tools
poetry run mkdocs serve              # the site, live-reloading
poetry run pytest                    # build-script tests
poetry run black . && poetry run mypy .
```

The PDF needs pandoc + XeLaTeX. Use the container image rather than installing TeX locally; that is also
what CI does, and matching it avoids "works on my machine" typography.

## The three things that will bite you

**1. Do not put a path in a cross-link.** Every link between pack documents is a bare sibling —
`[ethics.md](ethics.md)`, never `[ethics.md](src/pack/ethics.md)`. That single property is why one set
of bytes can serve the site, the book, the pack branch, and GitHub's own rendering with no rewrite step
(C-001). It has already been broken once by a human. `src/build/links.py` exists to catch it.

**2. The bootstrap has two names, on purpose.** It is `start.md` on `main` and `AGENTS.md` on the pack
branch. This is not an inconsistency to tidy up. Agent tools auto-load nested `AGENTS.md` files for the
subtree being edited, and this document's first instruction is `mkdir -p my-node/...` — named
`AGENTS.md` in `src/pack/`, it would fire at *you*, while you were editing the guide, and start
scaffolding someone's node. Rename on the branch, never in place (C-004). And when you rename, rewrite
the references too — both, or links break on one branch.

**3. The reading order lives in exactly one place.** `mkdocs.yml`'s `nav:`. The book, `llms.txt`,
`llms-full.txt`, and the lint all derive from it. Do not add a fifth hand-maintained copy; that is the
problem this design exists to end (`contracts/roles-declaration.md`).

## Where to start

**IC-01, before anything else.** The entire machine-facing surface — the reason this mission exists —
depends on GitHub Pages serving `.md` as readable text, which is a behaviour we do not control and
cannot test locally. Prove it against a real deployment and record the actual response headers. If it
fails, the URL map changes, and so does the guide's published text — which is a much bigger
conversation. Everything else is wasted effort until this is known.

Resist starting with the theme. It is the fun part, it is bounded to palette and typography by NFR-004,
and it cannot tell you whether the thing works.

## How you know you are done

Not by a green CI tick. By these:

- A fresh LLM, given nothing but the URL, sets up a correct workspace **and asks about the creator's real
  identity before writing anything**. The ordering is the point — that firewall is the guide's central
  ethical commitment, and a model that scaffolds beautifully but interviews second has failed.
- `git submodule add -b pack <repo> doc/core` runs clean from a bare checkout, because the guide already
  tells readers to run it.
- The PDF is printed and read on paper.

## Context worth having

- `doc/build.md` — the original brief, and the requirements source.
- `CLAUDE.md` (root, symlinked to `AGENTS.md`) — house rules for editing this repo, including why
  `src/pack/` must stay flat.
- The `pack` branch already exists — hand-built as `d024682` on 2026-07-16 to unblock the `5g_arg`
  project, whose `doc/core` submodule points at it. Your automation must reproduce it byte-for-byte
  before taking it over (C-005). Someone is already depending on it.
