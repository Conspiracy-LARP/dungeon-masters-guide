---
work_package_id: WP04
title: The book and the printable PDF
dependencies:
- WP02
requirement_refs:
- FR-003
- FR-004
tracker_refs: []
planning_base_branch: feat/guide-site-build
merge_target_branch: feat/guide-site-build
branch_strategy: Planning artifacts for this mission were generated on feat/guide-site-build. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into feat/guide-site-build unless the human explicitly redirects the landing branch.
subtasks:
- T017
- T018
- T019
- T020
- T021
- T022
phase: Phase 2 - The surfaces
assignee: ''
agent: "claude:opus:python-pedro:implementer"
shell_pid: "26621"
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: python-pedro
authoritative_surface: src/theme/book/
create_intent:
- src/theme/book/template.tex
- src/theme/book/fonts/README.md
- src/build/book.py
- tests/test_book.py
execution_mode: code_change
model: ''
owned_files:
- src/theme/book/**
- src/build/book.py
- tests/test_book.py
role: implementer
tags: []
task_type: implement
---

# Work Package Prompt: WP04 – The book and the printable PDF

## ⚡ Do This First: Load Agent Profile

Use the `/ad-hoc-profile-load` skill to load the agent profile specified in the frontmatter (or any
user-defined profile), and behave according to its guidance before parsing the rest of this prompt.

- **Profile**: `python-pedro`
- **Role**: `implementer`
- **Agent/tool**: `claude`

If no profile is specified, run `spec-kitty agent profile list` and select the best match for this work
package's `task_type` and `authoritative_surface`.

---

## Markdown Formatting

Wrap HTML/XML tags in backticks: `` `<div>` ``, `` `<script>` ``
Use language identifiers in code blocks: ` ```python `, ` ```bash `

---

## Objectives & Success Criteria

The cover-to-cover read: one long document, and a PDF that is genuinely pleasant on paper.

Success criteria:

- All ten chapters, in the declared reading order, as one single-file HTML document (FR-003).
- A PDF with a title page, a table of contents **carrying page numbers**, real pagination, and body type
  sized for A4 (FR-004).
- **No construction that assumes clicking.** A reader on paper cannot follow "see `ethics.md`" (FR-004).
- Both generated from `src/pack/` — nothing hand-authored (NFR-003).
- Fonts pinned; the build reproducible in CI.

## Context & Constraints

Read first: `quickstart.md`, `research.md` § R2, and `plan.md` § Complexity Tracking.

**Why LaTeX.** The stakeholder chose pandoc + XeLaTeX over an HTML-to-PDF renderer — decision
`01KXP7BCG6XFDHDRGZ57NXG90Q` — because print typography is the entire point of this output. They read on
paper; that is why this output exists. The rejected alternative (WeasyPrint/Paged.js) would have reused
the site's stylesheet for automatic visual parity and lighter CI.

**The cost you are carrying.** That choice creates a **second, independent style system**. The site has
CSS (WP03); this book has a LaTeX template. They can drift. This is recorded and accepted in
`plan.md` § Complexity Tracking. Your job is not to make them identical — parity is "not embarrassing",
not exact. Keep shared decisions (typefaces, palette) declared in one place and referenced by both.

**Constraints**:

- **Never write to `src/pack/`** (C-002, C-006).
- `src/theme/site/**` belongs to WP03. You own `src/theme/book/**`. Do not cross.
- Chapter order comes from `roles.load_documents()` (WP02). Never hard-code a chapter list.
- CI has a 5-minute budget (NFR-005); a TeX install per run will blow it. Use a prebuilt pandoc/TeX
  image (WP08 wires it; you specify what it needs).

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T017 – `book.py`: assemble chapters in nav order

- **Purpose**: One document from ten, in the one declared order.

- **Steps**:
  1. `guide book assemble` (click command) using `roles.load_documents()` (WP02) for chapters and order.
  2. Concatenate chapter sources with correct heading-level handling: each chapter's `#` becomes a book
     chapter. Check whether pandoc's `--shift-heading-level-by` suits, or whether to normalise during
     assembly.
  3. **Chapters only.** `README.md` and `start.md` are `not_in_book` (contract
     `roles-declaration.md`) — they ship as pages and raw markdown, never in the book's flow.
  4. Emit an intermediate assembled markdown file; both the HTML and PDF derive from it, so they cannot
     disagree.

- **Files**: `src/build/book.py`, `tests/test_book.py`

- **Parallel?**: No — T018 transforms its output.

- **Notes**: The guide's chapters each open with an italic "Companion to `creator-kit.md`" preamble aimed
  at a reader who arrived at a single page. In a cover-to-cover book those read oddly, but **do not edit
  them** — that is a content decision (C-006). If it grates, raise it as a finding.

### Subtask T018 – Flatten print-hostile cross-references

- **Purpose**: FR-004 — a printed page cannot be clicked. This is a requirement, not a nicety.

- **Steps**:
  1. Find every cross-reference in the assembled document: bare sibling links like
     `[ethics.md](ethics.md)`, and prose references like "see `storytelling.md`".
  2. Transform each into something a paper reader can act on — resolve to the chapter it names, e.g.
     *"see Chapter 6, Ethics"*, or a page cross-reference via LaTeX's referencing.
  3. **Do not modify `src/pack/`.** This transform runs on the assembled intermediate only.
  4. Leave inline-code examples alone: the guide *documents* the link convention using inline code
     (e.g. in `quickstart.md`, `CLAUDE.md`), and those samples are illustrations, not links. Same
     exclusion rule WP07 uses.

- **Files**: `src/build/book.py`, `tests/test_book.py`

- **Parallel?**: No.

- **Notes**: This is the subtask most likely to be skipped as "polish" and then quietly fail SC-003.
  A PDF full of "see `ethics.md`" is not a book; it is a website that has been printed.

### Subtask T019 – `src/theme/book/`: LaTeX template — title page, ToC with page numbers, A4

- **Purpose**: The typographic quality that justified the whole toolchain decision.

- **Steps**:
  1. `src/theme/book/template.tex` — a pandoc LaTeX template with:
     - a title page (title, subtitle, and the fact that it is the guide's own manual)
     - `\tableofcontents` with page numbers
     - A4, sensible margins, readable body size (11pt+), running heads, page numbers
     - widow/orphan control and hyphenation — the things LaTeX was chosen for
  2. Handle the guide's real constructs: wide tables (the tells comparison, requirement tables), block
     quotes, code fences, em-dashes, the occasional emoji.
  3. Keep the typographic decisions aligned with WP03's palette/type where practical, and accept
     approximation.

- **Files**: `src/theme/book/template.tex`

- **Parallel?**: **[P]** — independent of T021.

- **Notes**: Emoji in XeLaTeX is a classic failure — the guide uses ✅/❌ in `storytelling.md`'s tells
  table and 🤖 in the AI pointer. Decide deliberately: a font that covers them, or a substitution. Do
  not let it crash the build silently at the end.

### Subtask T020 – Pinned fonts and the pandoc/XeLaTeX container invocation

- **Purpose**: Reproducibility, and protecting NFR-005.

- **Steps**:
  1. Pin the typefaces. Do not rely on system fonts — CI's are not yours.
  2. Specify the pandoc/TeX container image and invocation `book.py` shells out to. Prefer a prebuilt
     image with XeLaTeX included over installing TeX packages at build time.
  3. Document the fonts and licences in `src/theme/book/fonts/README.md`. This is a public repo and the
     guide has a `THIRD_PARTY_NOTICES` habit in sibling projects; bundled fonts need their licences
     stated.
  4. Record the expected build duration so WP08 can hold the 5-minute line.

- **Files**: `src/theme/book/fonts/README.md`, `src/build/book.py`

- **Parallel?**: No.

- **Notes**: Font licensing is a real obligation, not paperwork. Check redistribution terms before
  bundling.

### Subtask T021 – The single-file HTML book

- **Purpose**: FR-003 — the whole guide as one page, for reading online cover to cover.

- **Steps**:
  1. From the same assembled intermediate as the PDF (so they cannot disagree), render one
     self-contained HTML document with an internal ToC.
  2. Here links **can** be clicked, so the flattening from T018 should not be applied — or should be
     applied differently. Decide deliberately and note it.
  3. Link it from the site (WP03 surfaces it).

- **Files**: `src/build/book.py`

- **Parallel?**: **[P]** — independent of T019.

- **Notes**: The two book renderings have opposite needs: paper cannot click, HTML should. One
  intermediate, two transforms.

### Subtask T022 – Tests for assembly and cross-reference flattening

- **Purpose**: Protect the two things that will regress silently.

- **Steps**:
  1. Assembly: chapters present, in nav order, `not_in_book` documents absent, heading levels correct.
  2. Flattening: a bare sibling link becomes a chapter reference; an inline-code sample is untouched.
  3. `src/pack/` unmodified after a build.
  4. Use the temporary pack fixture from WP02's `conftest.py`, not the live pack.

- **Files**: `tests/test_book.py`

- **Parallel?**: No.

- **Notes**: PDF rendering itself is hard to unit-test — that is what SC-003 (print it) is for. Test the
  transforms, which is where the logic lives.

## Test Strategy

```bash
poetry run pytest tests/test_book.py
poetry run guide book assemble && poetry run guide book pdf
```

Mandatory: chapters in nav order; `not_in_book` excluded; cross-references flattened for print;
inline-code samples untouched; `src/pack/` unmodified. The PDF's real acceptance is SC-003 in WP09 —
printed on paper, by a human.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Cross-reference flattening treated as polish, skipped, fails SC-003 | It is T018, a first-class subtask with tests |
| Emoji crash XeLaTeX late in the build | Decide the font/substitution deliberately in T019 |
| System fonts differ in CI | Pin them (T020) |
| TeX install per run blows the 5-minute budget | Prebuilt image, specified in T020 |
| Book and site styles drift | Accepted (plan.md Complexity Tracking); share declarations where practical |
| Bundled fonts with wrong licences in a public repo | Check terms; document in `fonts/README.md` |

## Review Guidance

- Open the PDF: title page, ToC **with page numbers**, real pagination?
- Search the PDF for "`.md`" — any surviving click-dependent reference is an FR-004 failure.
- Are chapters in the declared order, with `README.md`/`start.md` absent?
- `git diff --stat src/pack/` — must be empty.
- Is there a hard-coded chapter list anywhere, instead of `roles.load_documents()`?

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
- 2026-07-16T21:06:57Z – claude:opus:python-pedro:implementer – shell_pid=2435 – Assigned agent via action command
- 2026-07-16T21:28:55Z – claude:opus:python-pedro:implementer – shell_pid=2435 – Ready for review: book assembled in nav order from roles.load_documents(); PDF has title page, page-numbered ToC, 58 pages, cross-references flattened to chapter+page; single-file HTML book from the same intermediate with links retargeted to internal anchors. Emoji substituted to pifont dingbats with two guards against silent glyph loss. Image pinned by digest. src/pack/ untouched.
- 2026-07-16T21:29:46Z – claude:opus:reviewer-renata:reviewer – shell_pid=14582 – Started review via action command
- 2026-07-16T22:44:57Z – claude:opus:reviewer-renata:reviewer – shell_pid=24774 – Started review via action command
- 2026-07-16T22:51:27Z – user – shell_pid=24774 – Moved to planned
- 2026-07-16T22:52:11Z – claude:opus:python-pedro:implementer – shell_pid=26621 – Started implementation via action command
