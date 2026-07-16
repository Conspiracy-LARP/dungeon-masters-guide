# Implementation Plan: Guide Site, Book, and LLM Bootstrap

**Branch**: `feat/guide-site-build` | **Date**: 2026-07-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `kitty-specs/guide-site-build-01KXP76R/spec.md`

## Summary

Publish the guide's finished markdown as four surfaces that cannot disagree, because all are generated
from the same bytes: an attractive site, a printable book, machine-readable sources, and the `pack`
branch creators attach to their own projects.

The technical approach: MkDocs + Material for the site, its `nav:` acting as the single declaration of
chapter order and document roles; pandoc + XeLaTeX for a print-quality PDF; small Python/click scripts
deriving `llms.txt`, `llms-full.txt`, the book source, and an orphan-branch mirror; GitHub Actions
publishing everything to GitHub Pages on every push.

The mission's real objective is behavioural, not visual: a creator hands any LLM one URL and it
scaffolds their workspace and opens the interview. That surface depends on the host serving raw markdown
as readable text — a thing we do not control and cannot test locally — so proving it comes first.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: MkDocs + Material (site); pandoc with XeLaTeX (PDF); PyYAML (parsing the nav declaration); click (build CLIs); Poetry (dependency management)
**Storage**: N/A — stateless static output (C-004)
**Testing**: pytest for build scripts; role + link lint enforced in CI; one behavioural acceptance test run against a real LLM (SC-001); one printed-on-paper check (SC-003)
**Target Platform**: GitHub Pages, project site served from the `/dungeon-masters-guide/` subpath (C-003)
**Project Type**: single — a static publishing pipeline, no application and no runtime
**Performance Goals**: a source change is live on every surface within 5 minutes (NFR-005)
**Constraints**: pack stays flat with bare sibling links, no path separators (C-001); the build never edits prose (C-002); every absolute address derives from one configured base so a domain is a one-value change (NFR-001); the bootstrap is never named `AGENTS.md` on `main` (C-004); stock theme plus palette/typography only (NFR-004)
**Scale/Scope**: 12 source documents, 10 chapters, 7 published surfaces, single-digit contributors

## Charter Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Skipped — no charter exists.** `spec-kitty charter context` reports `mode: missing` for both `specify`
and `plan`; `.kittify/charter/charter.md` is absent. No charter gates to evaluate, and this is not
treated as a violation.

Two built-in directives were applied regardless, and both pass:

- **DIRECTIVE_003 (Decision Documentation)** — the PDF toolchain fork is recorded as decision
  `01KXP7BCG6XFDHDRGZ57NXG90Q` with rationale and rejected alternative. R1–R8 in `research.md` each
  carry a rationale and the alternatives considered.
- **DIRECTIVE_010 (Specification Fidelity)** — every concern below cites the FR/NFR/C it serves. Nothing
  is planned that the spec did not ask for.

**Post-design re-check**: passes. Phase 1 introduced no new architectural surface beyond what the spec
requires; the one design choice with a cost the spec did not anticipate (two style systems, from the
pandoc/LaTeX decision) is recorded in Complexity Tracking below.

## Project Structure

### Documentation (this mission)

```
kitty-specs/guide-site-build-01KXP76R/
├── plan.md              # This file
├── spec.md              # Committed 7231c72
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
├── checklists/          # Spec quality checklist
├── decisions/           # DM-01KXP7BCG6XFDHDRGZ57NXG90Q (PDF toolchain)
└── tasks/               # /spec-kitty.tasks output — NOT created by /spec-kitty.plan
```

### Source Code (repository root)

```
src/pack/                # THE GUIDE — canonical, flat, 12 .md files. Read-only to this mission (C-006).

mkdocs.yml               # WP02. Site config AND the single declaration of reading order + roles (R5).
pyproject.toml           # WP02. Poetry. Packages src/build only — src/pack is content, not a package.
poetry.lock

src/build/               # Python/click CLIs, Poetry-managed. Command surface: `guide <group> <cmd>`.
├── cli.py               #   WP02. The `guide` click group.
├── config.py            #   WP02. The ONE base-URL helper. Nothing else composes a URL. (NFR-001)
├── roles.py             #   WP02. Document model, role resolution, published_name (FR-011)
│                        #         → `guide roles lint | list | check-drift`
├── rename.py            #   WP02. Reference rewriting, boundary-aware (FR-010). Shared by WP03 + WP06.
├── provenance.py        #   WP02. Every output traces to the pack (NFR-003)
│                        #         → `guide verify provenance --output <dir>`
├── site.py              #   WP03. Landing-page derivation, AI pointer, raw-md publishing
├── book.py              #   WP04. Chapter assembly + print cross-ref flattening
├── llms.py              #   WP05. llms.txt / llms-full.txt
├── packbranch.py        #   WP06. The orphan mirror
└── links.py             #   WP07. Link/invariant check across both branches

src/theme/
├── site/                # WP03. Palette + typography ONLY (NFR-004). CSS ships via custom_dir —
│   └── overrides/       #       NOT extra_css, which resolves into src/pack/. See below.
└── book/                # WP04. LaTeX template + pinned fonts.

tests/                   # pytest. Temporary-pack fixtures — never the live src/pack/.
spike/                   # WP01. FINDINGS.md only; the spike itself is removed.
doc/acceptance/          # WP09. Behavioural evidence (SC-001/002/003).
.github/workflows/       # WP08. publish.yml — build, lint, deploy Pages, mirror the pack branch.
doc/build.md             # The requirements source. Not modified by this mission.
```

**Two traps this tree encodes, both found by building rather than reasoning** (WP02):

- **`extra_css` resolves relative to `docs_dir`, which is `src/pack/`.** Declaring it would write build
  assets into the product (C-002, C-006) and then fail the role lint as an undeclared document. CSS ships
  through `theme.custom_dir` instead.
- **`theme.custom_dir` is validated eagerly**, so it cannot be declared before the directory exists — a
  config naming a missing path aborts every build in the four lanes that depend on WP02. WP03 adds both
  hooks together with their files.

**Structure Decision**: Single project. `src/pack/` is input and is never written to by the build
(C-002, C-006); `src/build/` holds the derivation scripts; `src/theme/` holds the bounded styling for
both output systems, split `site/` ↔ `book/` so WP03 and WP04 own disjoint surfaces. This preserves the
repo's existing `src/` ↔ `doc/` split, in which `doc/` is documentation *about* the guide and never
ships.

*Updated 2026-07-16 to match what WP01 and WP02 actually built (analysis finding I1). The earlier tree
omitted five modules, the theme split, and two directories — the map an implementer reads first should
not be fiction.*

## Complexity Tracking

*Fill ONLY if Charter Check has violations that must be justified*

No charter, so no charter violations. One accepted complexity is recorded here because it was chosen
deliberately against a simpler option and future contributors will otherwise wonder why:

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Two independent style systems (Material CSS for the site, a LaTeX template for the book) | The PDF is a first-class output for readers who print; LaTeX gives hyphenation, justification and widow/orphan control a CSS-paged renderer only approximates. Stakeholder decision `01KXP7BCG6XFDHDRGZ57NXG90Q`. | An HTML-to-PDF renderer (WeasyPrint/Paged.js) would reuse the site stylesheet, giving automatic parity and lighter CI — but print typography is the entire point of this output, and it is the one the stakeholder asked for by name. Accepted costs: a TeX image in CI, and two style systems that can drift. |

## Implementation Concern Map

> **Note**: Implementation concerns are NOT work packages and are NOT executable units.
> `/spec-kitty.tasks` translates these into executable WPs — one concern may become
> multiple WPs; multiple small concerns may merge into one WP.

### IC-01 — Prove the machine surface can exist

- **Purpose**: Establish empirically that the host serves raw markdown as text a model can read, because every machine-facing requirement rests on a behaviour the platform controls and we cannot test locally.
- **Relevant requirements**: FR-007, FR-008; risk R-001; research R3
- **Affected surfaces**: a throwaway Pages deployment; `.nojekyll`; the URL map in `doc/build.md` if the finding forces an amendment
- **Sequencing/depends-on**: none — nothing else is worth building until this is known
- **Risks**: Failure here is silent and total: the site can look finished while `/AGENTS.md` serves as a download and the mission's entire purpose fails. If markdown cannot be served readably, the fallback (extensionless or `.txt` twins with `llms.txt` repointed; Fly only as a last resort) changes the published URL map, which changes the guide's own text — so the cost of learning this late is high.

### IC-02 — Declare roles and reading order once

- **Purpose**: Make the site config the single declaration of chapter order and document roles, so the book, the machine index and the lint all derive from one source instead of a fifth hand-maintained copy.
- **Relevant requirements**: FR-011; assumption A-002; research R5; constraint C-002
- **Affected surfaces**: `mkdocs.yml` (`nav:` plus an explicit not-a-chapter list), `src/build/roles.py`, `tests/`
- **Sequencing/depends-on**: none, though every derivation concern consumes it
- **Risks**: The roles list is the mitigation for R-003 (a document silently missing from the book), so the lint must fail the build rather than warn. Front-matter was rejected as the alternative home because the prose files are themselves published raw and shipped to creators — YAML would leak into the reader's markdown.

### IC-03 — The browsable site

- **Purpose**: Give a human evaluating the project something attractive and navigable to read, on any device.
- **Relevant requirements**: FR-001, FR-002, FR-012 (partly), NFR-002, NFR-004, NFR-006; research R1
- **Affected surfaces**: `mkdocs.yml`, `src/theme/`, the landing page derived from the kit's pitch, per-page AI pointer and `rel="alternate"` metadata, raw `.md` copied to parallel paths, `.nojekyll`
- **Sequencing/depends-on**: IC-01 (URL map must be settled), IC-02 (nav is the order)
- **Risks**: Design investment is explicitly bounded (NFR-004) — palette and typography only. The temptation to build the Gygax homage here is the scope risk; it is Out of Scope by A-004.

### IC-04 — The book and the printable PDF

- **Purpose**: Produce the cover-to-cover read for people who print, with the typographic quality that justified choosing LaTeX.
- **Relevant requirements**: FR-003, FR-004; decision `01KXP7BCG6XFDHDRGZ57NXG90Q`; research R2
- **Affected surfaces**: `src/build/book.py`, `src/theme/` (LaTeX template), pandoc/XeLaTeX container image, pinned fonts
- **Sequencing/depends-on**: IC-02
- **Risks**: Flattening cross-references for paper is part of this concern, not a polish step — a printed page cannot follow "see `ethics.md`" (FR-004). The TeX image threatens the 5-minute budget (NFR-005) if TeX is installed per run rather than baked. This concern creates the style-drift cost recorded in Complexity Tracking.

### IC-05 — The machine-readable sources

- **Purpose**: Let a model consume the guide directly, and — more importantly — discover that there is a procedure it can follow rather than just documents it can read.
- **Relevant requirements**: FR-005, FR-006, FR-008, NFR-001; research R8
- **Affected surfaces**: `src/build/llms.py`, `llms.txt`, `llms-full.txt`, the configured base URL
- **Sequencing/depends-on**: IC-01, IC-02
- **Risks**: `llms.txt` must lead with the bootstrap as an instruction, not bury it in an alphabetised list — an index that satisfies the convention while burying the bootstrap defeats the mission. Every address must derive from the one configured base (NFR-001) or the future domain switch stops being a one-value change.

### IC-06 — The pack branch

- **Purpose**: Publish the markdown alone, under the filename models look for, so creators can attach the kit to their own project.
- **Relevant requirements**: FR-009, FR-010; constraints C-004, C-005; research R4
- **Affected surfaces**: `src/build/packbranch.py`, the `pack` branch on origin
- **Sequencing/depends-on**: IC-02
- **Risks**: The branch already exists — hand-built on 2026-07-16 as `d024682` to unblock a downstream project — so automation must reproduce it byte-for-byte before taking over (C-005), or the guide starts lying to readers who already followed its instructions (R-002). The rename is two jobs, not one: move the file **and** rewrite references, or links break on one branch or the other. Force-pushing a branch that consumers pin means it must be read-only by contract.

### IC-07 — Link integrity across branches

- **Purpose**: Machine-enforce the invariant that makes the whole architecture possible — bare sibling links with no paths, resolving on every surface.
- **Relevant requirements**: FR-013; constraint C-001; research R7
- **Affected surfaces**: `src/build/links.py`, CI
- **Sequencing/depends-on**: IC-06 (needs both branches to check)
- **Risks**: This invariant has already been broken once during authoring — a `README.md` link resolved on `pack` but 404'd on `main` — and was caught only by an ad-hoc check. It is exactly the class of error humans miss and machines catch for free.

### IC-08 — Continuous publication

- **Purpose**: Ensure no surface can lag another, with no human step.
- **Relevant requirements**: FR-012, NFR-005; dependency D-002
- **Affected surfaces**: `.github/workflows/`, Pages settings
- **Sequencing/depends-on**: IC-03, IC-04, IC-05, IC-06, IC-07
- **Risks**: Needs Pages enabled and permitted to publish from automation (D-002) — an account-level prerequisite outside the code. The 5-minute budget (NFR-005) is mostly the TeX image's problem.

### IC-09 — Behavioural acceptance

- **Purpose**: Answer the only questions that decide whether this mission succeeded, none of which a green CI tick can answer.
- **Relevant requirements**: SC-001, SC-002, SC-003; risk R-002; dependency D-003
- **Affected surfaces**: a real LLM session; a clean checkout; a printer
- **Sequencing/depends-on**: IC-08
- **Risks**: SC-001 must be run against a real model and must verify the *order* of events — the identity firewall asked **before** anything is written. That ordering is the guide's central ethical commitment, and a model that scaffolds perfectly but interviews second has failed the test. SC-003 requires paper, not a preview.
