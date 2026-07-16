# Phase 0 — Research

**Mission**: `guide-site-build-01KXP76R`
**Purpose**: resolve every unknown in Technical Context before design.

---

## R1 — Static site generator

**Decision**: MkDocs + Material.

**Rationale**: The brief nominates it; it is Python, matching the repo's existing tooling and the
stakeholder's stated preference for Poetry-managed Python projects. It gives search, nav, responsive
layout, and light/dark theming out of the box — which is most of NFR-002 and NFR-006 for free, and
exactly matches the agreed "stock theme, lightly dressed" bar (NFR-004). Its `nav:` key is a natural
home for the reading order (see R5).

**Alternatives considered**: *Astro Starlight* — more polished defaults, but introduces a Node toolchain
alongside the Python one for no benefit the bounded design budget can use. *Hugo* — fast, but its
templating is a poor fit for the small amount of customisation wanted. *Hand-rolled* — violates NFR-003.

## R2 — Printable PDF toolchain

**Decision**: pandoc + XeLaTeX. **Recorded as decision `01KXP7BCG6XFDHDRGZ57NXG90Q`** (stakeholder,
Phase 1 planning).

**Rationale**: Print typography is the point of this output — the stakeholder specifically wants a PDF
for people who print and read on paper. LaTeX gives real hyphenation, justification, and widow/orphan
control that a CSS-paged renderer approximates at best. FR-004's page-numbered ToC and pagination are
native.

**Alternatives considered**: *WeasyPrint / Paged.js* — would reuse the site stylesheet so the book and
site match automatically, and keep CI light. Rejected in favour of print quality.

**Consequences the design must absorb** (this choice is not free):

- CI needs a TeX distribution. Use a pandoc container image with XeLaTeX preinstalled rather than
  installing TeX packages per run, or NFR-005's 5-minute budget is at risk.
- **Two independent style systems now exist** — the site's CSS and the LaTeX template. They can drift.
  Mitigation: keep the shared decisions (typeface choices, palette) in one declared place and reference
  it from both; accept that exact visual parity is not a requirement, only non-embarrassing consistency.
- Fonts must be available to XeLaTeX in CI. Pin them; do not rely on system defaults.

## R3 — Serving raw markdown as readable text (the highest risk)

**Decision**: publish `.nojekyll`, serve the `.md` files as static assets, and **verify the served
content-type empirically in the first work package, before any other work**.

**Rationale**: FR-007 and FR-008 are the mission's reason to exist, and they depend on a behaviour the
host controls, not us. Two distinct failure modes:

1. **Without `.nojekyll`**, GitHub Pages runs the source through Jekyll, which processes/renames
   markdown and may not serve `.md` at all. This is well documented and the fix is a single empty file.
2. **Content-type.** Even served, the platform decides the type. If `.md` arrives as a download
   disposition or is rendered to HTML, `/AGENTS.md` fails as a machine surface **while the site looks
   perfect** — R-001 in the spec.

**Why this is a spike, not an assumption**: the failure is invisible from the site. No amount of local
testing proves it, because the behaviour belongs to the deployed host. The plan therefore front-loads a
throwaway deployment that publishes one `.md` behind `.nojekyll` and asserts on the actual response
headers. If the content-type is unusable, the fallback is to *also* publish each document at an
extensionless or `.txt` path and point `llms.txt` there — but we must know before styling anything.

**Alternatives considered**: *Assume it works* — rejected; it is the one requirement whose failure is
silent. *Serve from Fly instead* — full control over headers, but reintroduces infrastructure the
stakeholder explicitly does not want (C-003). Keep as the escape hatch only if Pages cannot serve
readable markdown at all.

## R4 — Publishing the `pack` branch

**Decision**: an **orphan-branch mirror, force-pushed** on every push to `main`.

**Rationale**: The branch is a *generated artifact*, not a history. Force-pushing an orphan commit whose
tree is exactly `src/pack/` (with the rename applied) is idempotent, trivially reproducible, and cannot
drift. It reproduces exactly what was created by hand on 2026-07-16 (`d024682`), satisfying C-005.

**Alternatives considered**: *`git subtree split --prefix=src/pack`* — the brief suggests it, and it
preserves per-file history. Rejected because the branch must also apply a **rename and reference
rewrite** (FR-010), which a subtree split cannot do; we would have to post-process anyway. Preserved
history on a generated branch is of no value to consumers, who only ever read the tip.

**Consequence**: consumers pin a submodule to a force-pushed branch. This is safe for a read-only
reference — `git submodule update --remote` fetches the new tip — but the branch must never be committed
to directly. State that on the branch itself.

## R5 — Where the reading order lives

**Decision**: MkDocs `nav:` in the build configuration is the **single source of truth** for chapter
order and document roles. Every other consumer (book, `llms.txt`, `llms-full.txt`, the lint) derives
from it by parsing that configuration. The prose lists in `src/pack/README.md` and the kit's quick-read
box are **checked against it** by the lint, never hand-synced.

**Rationale**: The build needs the order in configuration regardless (C-002 forbids encoding it in
prose). The order already exists in four places; adding a fifth hand-maintained copy is the failure the
mission should prevent, not commit. One declaration, many derivations.

**Roles fall out of the same source**: a document listed in `nav` is a chapter; a document declared in an
explicit `not_in_book` list is not-a-chapter; a document in `src/pack/` appearing in neither fails the
build (FR-011).

**Alternatives considered**: *A separate `pack.yml` manifest* — cleaner conceptually, but then MkDocs
needs a plugin/macro to consume it, and the config becomes a second source anyway. *Front-matter in each
document* — rejected: it edits the prose files, which are also published raw and shipped to creators, so
YAML front-matter would leak into the reader's markdown. That is a real objection, not a stylistic one.

## R6 — Build tooling and language

**Decision**: Python 3.12, dependencies managed with **Poetry**; build scripts under `src/build/` as
small **click** CLIs with type hints; tests in **pytest**; formatted with **black**; checked with
**mypy**.

**Rationale**: Matches the stakeholder's standing conventions for Python projects and the toolchain
MkDocs already requires. The scripts are few and small: derive `llms.txt`/`llms-full.txt`, assemble the
book source, lint roles and links, build the pack branch.

## R7 — Link integrity across surfaces

**Decision**: a link-check that runs against **both** branches, asserting the C-001 invariant.

**Rationale**: The bare-sibling-link property is what lets one set of bytes serve four surfaces, and it
has already been broken once during authoring (a `README.md` link to `AGENTS.md` resolved on `pack` but
404'd on `main`; caught only by an ad-hoc check). Two assertions: (a) every relative link resolves on
`main`, where the file is `start.md`; (b) every relative link resolves on `pack`, where it is
`AGENTS.md`; and (c) no relative link contains a path separator.

## R8 — `llms.txt` convention

**Decision**: follow llmstxt.org — an H1, a blockquote summary, then link sections. Deviate in one
respect: the **first entry is the bootstrap**, presented as a procedure to follow rather than a document
to read.

**Rationale**: The convention is designed for models that want to *read* a project. Ours wants models to
*act*. FR-005 makes the bootstrap primary for exactly that reason; an index that buries it under
alphabetised chapters would satisfy the convention and defeat the mission.

---

## Resolved unknowns

| Unknown | Status |
|---|---|
| Site generator | Resolved — R1 |
| PDF toolchain | Resolved — R2 (stakeholder decision `01KXP7BCG6XFDHDRGZ57NXG90Q`) |
| Raw markdown served readably | **Deliberately unresolved — R3.** Cannot be settled by research; requires a deployed spike. First work package. |
| Pack branch mechanism | Resolved — R4 |
| Reading-order home | Resolved — R5 (adopts spec assumption A-002) |
| Build language/tooling | Resolved — R6 |
| Link integrity method | Resolved — R7 |
| Machine index shape | Resolved — R8 |

No `[NEEDS CLARIFICATION]` markers remain. R3 is not a clarification — it is a known unknown with a
designed experiment and a fallback.
