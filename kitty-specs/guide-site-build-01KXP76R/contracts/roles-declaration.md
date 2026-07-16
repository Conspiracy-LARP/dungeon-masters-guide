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

validation:                           # REQUIRED — without this, --strict does NOT enforce FR-011
  nav:
    omitted_files: warn

not_in_nav: |                         # REQUIRED — see "The --strict interaction" below
  README.md
  start.md
```

## The `--strict` interaction (resolves analysis finding U2)

> **CORRECTED 2026-07-16 by WP02, against a real build.** This section previously claimed that an
> undeclared document "is an INFO that `--strict` escalates to a build failure." **That is false.**
> `validation.nav.omitted_files` defaults to `info`, and `--strict` escalates only `WARNING` — so on
> MkDocs 1.6.1 the real pack **plus** an undeclared `sneaky-new-doc.md` builds green, exit 0. FR-011 was
> therefore enforced by our own lint alone, and anyone running `mkdocs serve` locally would have seen
> nothing. The resolution below now includes the `validation` key that makes the claim true.

`docs_dir` is `src/pack`, so the two `not_in_book` documents sit **inside** the docs tree while being
deliberately absent from `nav`. Left unspecified, WP03's first build behaviour is a guess.

The resolution is declared, not discovered:

1. **Set `validation.nav.omitted_files: warn`.** Without it, `--strict` ignores omitted files entirely
   and FR-011 has no teeth in the build. With it, an undeclared document aborts the build
   (`Aborted with 1 warnings in strict mode!`) — verified.
2. **Use MkDocs' `not_in_nav` key** (MkDocs ≥ 1.6) listing exactly the `not_in_book` set. This tells
   MkDocs the two omissions are intentional, so they pass while a *new* undeclared document still fails
   — which is what FR-011 wants.
3. **Do not** disable `--strict`, and **do not** add the two documents to `nav`. The first hides real
   errors; the second puts the pack's index and the machine bootstrap into the human reading order,
   which is what `not_in_book` exists to prevent.
4. `not_in_nav` and `extra.pack.not_in_book` must list the same files. The role lint (FR-011) asserts it;
   two lists that can disagree is precisely the drift this contract exists to end.

## Theme hooks must not be pre-declared (WP02 finding)

The tasks originally told WP02 to pre-declare the theme hooks so WP03 need only create files. **That is
not possible, and attempting it breaks four lanes.** Recorded here so it is not re-attempted:

- **`theme.custom_dir` is validated eagerly.** A config naming a directory that does not exist yet aborts
  *every* build (`Aborted with a configuration error!`, exit 1) — including WP04, WP05 and WP06, which
  all depend on WP02's lane. It cannot precede the directory it names. **This is the only one of the two
  that aborts.**
- **`extra_css` resolves relative to `docs_dir`, which is `src/pack/` — the product.**
  `extra_css: [stylesheets/extra.css]` would demand `src/pack/stylesheets/extra.css`: build assets
  written into the guide, violating C-002 and C-006. **Ship CSS through `custom_dir` instead** — files
  under `src/theme/site/overrides/` are copied to the output; put the stylesheet there and reference it
  from a `main.html` override.

  *Precision, corrected at WP02's review — the first draft of this section overstated both points, and
  the accurate version is the stronger argument:* `extra_css` naming a missing file does **not** abort;
  it exits 0 and ships a **silent 404**. Nor would it fail the role lint, which globs `*.md` only. So the
  real hazard is not a loud failure you would notice — it is that putting the stylesheet in the only
  place `extra_css` can see it means writing into the product, and putting it anywhere else fails
  quietly at runtime. Verified against MkDocs 1.6.1: a stylesheet under `src/theme/` was not copied to
  output; the same file under `src/pack/stylesheets/` was.

WP03 therefore adds both hooks together with the files they name. This is a small, justified edit to
WP02's `mkdocs.yml` rather than an ownership violation; the config documents exactly what to add.

## The landing page

FR-001 requires the landing page be the kit's "What is this?" pitch, derived at build time (WP03 T013).
`src/pack/README.md` is **not** the site index — it is the pack branch's front door, and it is
`not_in_book`. WP03's hook generates the index; `README.md` is published as a page and as raw markdown
like any other non-chapter document.

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
