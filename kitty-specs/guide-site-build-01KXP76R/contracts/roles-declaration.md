# Contract — the roles and reading-order declaration

**Mission**: `guide-site-build-01KXP76R` · Serves FR-011, C-002 · Research R5 · Spec assumption A-002

**One declaration, many derivations.** The site config is the single source of chapter order and
document roles. The book, `llms.txt`, `llms-full.txt`, and the lint all read it. Nothing else declares
order.

## Shape

```yaml
# mkdocs.yml
nav:                                  # ORDER IS AUTHORITATIVE — this is the reading order
  - Creator Kit: creator-kit.md       # position 1
  - Getting Started: getting-started.md
  - How We Tell It: storytelling.md
  - Philosophy: philosophy.md
  - Improvisation: improvisation.md
  - Ethics: ethics.md
  - Communications: communications.md
  - Worked Example: worked-example.md
  - Technical Suggestions: technical-suggestions.md
  - Continuity Checker: story-continuity-checker-prompt.md   # position 10

extra:
  pack:
    not_in_book:                      # published, but outside the book's flow
      - README.md                     # the pack's index; front door of the pack branch
      - start.md                      # the bootstrap; published as AGENTS.md
```

## Rules

| # | Rule | On violation |
|---|---|---|
| 1 | Every `.md` in `src/pack/` appears in exactly one of `nav` or `not_in_book` | **Build fails** (FR-011) |
| 2 | No file appears in both | Build fails |
| 3 | No entry names a file that does not exist | Build fails |
| 4 | `nav` order is the reading order everywhere — book, `llms-full.txt`, `llms.txt` | n/a — derived |
| 5 | The prose lists that repeat the order in `src/pack/README.md` and `creator-kit.md`'s quick-read box are **checked against** this declaration | Build fails, reported as drift |

Rule 1 exists because the failure it prevents is silent: a new document that is neither declared nor
noticed simply never appears in the book, and nobody finds out (R-003). Loud failure is the feature.

Rule 5 is the reason this contract exists at all. The reading order already appears in four prose
places; the config makes five. Rather than hand-sync five copies, the config is authoritative and the
prose is verified against it. The lint may **report** drift but must never **fix** it — editing the
guide's prose is forbidden to the build (C-002) and out of scope for this mission (C-006).

## Why not front-matter

The obvious alternative — declare the role in each document's YAML front-matter — is rejected on a
concrete ground, not a stylistic one: **these files are published raw and shipped to creators**
(FR-007, FR-009). Front-matter would appear in the markdown a creator reads at `doc/core/ethics.md` and
in what a model fetches at `{base}ethics.md`. Build metadata must not leak into the product.
