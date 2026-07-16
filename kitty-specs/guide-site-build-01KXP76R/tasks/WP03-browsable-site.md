---
work_package_id: WP03
title: The browsable site
dependencies:
- WP01
- WP02
requirement_refs:
- FR-001
- FR-002
- FR-007
- FR-008
tracker_refs: []
planning_base_branch: feat/guide-site-build
merge_target_branch: feat/guide-site-build
branch_strategy: Planning artifacts for this mission were generated on feat/guide-site-build. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into feat/guide-site-build unless the human explicitly redirects the landing branch.
subtasks:
- T012
- T013
- T014
- T015
- T016
phase: Phase 2 - The surfaces
assignee: ''
agent: "claude:opus:frontend-freddy:implementer"
shell_pid: "2435"
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: frontend-freddy
authoritative_surface: src/theme/site/
create_intent:
- src/theme/site/palette.css
- src/theme/site/typography.css
- src/theme/site/overrides/main.html
- src/build/site.py
- tests/test_site.py
execution_mode: code_change
model: ''
owned_files:
- src/theme/site/**
- src/build/site.py
- tests/test_site.py
role: implementer
tags: []
task_type: implement
---

# Work Package Prompt: WP03 – The browsable site

## ⚡ Do This First: Load Agent Profile

Use the `/ad-hoc-profile-load` skill to load the agent profile specified in the frontmatter (or any
user-defined profile), and behave according to its guidance before parsing the rest of this prompt.

- **Profile**: `frontend-freddy`
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

The site a human lands on and reads — and the raw markdown surface published alongside it.

Success criteria:

- `mkdocs build` produces a site with search and nav in the declared reading order (FR-001).
- The landing page is the kit's own "What is this?" pitch (FR-001).
- Every page carries a visible AI pointer and `<link rel="alternate" type="text/markdown">` (FR-002).
- Raw `.md` is published at parallel paths, **with the bootstrap published as `AGENTS.md`** (FR-007,
  FR-008).
- `.nojekyll` is in the output; every generated link is subpath-correct (C-003).
- Readable at 320px with no horizontal scroll (NFR-002); body text meets WCAG AA in light and dark
  (NFR-006).

## Context & Constraints

Read first: `quickstart.md`, then `contracts/url-map.md` — **including WP01's finding**, which may have
amended it. Do not start until WP01 has reported: if raw `.md` cannot be served readably, the addresses
you are about to generate change.

**The design budget is bounded, deliberately.** NFR-004: stock Material plus **palette and typography
only**. The stakeholder chose this over a bespoke design, and a distinctive "referee's manual" identity
is explicitly **Out of Scope** (spec A-004). `doc/build.md` mentions a Gygax homage; that is aspiration,
not this mission's licence. This is the WP where scope will try to creep — the fun is in the theme and
the requirement is readability. If you think the site needs custom components to be good, raise it;
don't build it.

**Constraints**:

- **Never write to `src/pack/`** (C-002, C-006). The landing page is *derived*, not authored — do not
  add an `index.md` to the pack.
- **The `--strict` question is already answered** — do not re-derive it. `src/pack` is the `docs_dir`,
  so `README.md` and `start.md` sit in the docs tree but are intentionally absent from `nav`, which
  `--strict` would fail on. WP02's `mkdocs.yml` declares them under MkDocs' `not_in_nav` key, which
  suppresses that specific warning while still failing on a genuinely undeclared document. Do not
  disable `--strict` and do not add them to `nav`. See `contracts/roles-declaration.md` § "The `--strict`
  interaction".
- `mkdocs.yml` is owned by **WP02**. It already contains the theme and `extra_css` hooks pointing at
  `src/theme/site/`. You create those files; you should not need to edit the config. If you genuinely
  must, record a one-line rationale.
- Every URL derives from `config.absolute_url()` (WP02, T007). Do not hard-code a hostname (NFR-001).

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T012 – `src/theme/site/`: palette and typography, bounded

- **Purpose**: Make it attractive within the agreed budget.

- **Steps**:
  1. `src/theme/site/palette.css` — a considered light and dark palette via Material's CSS custom
     properties. Verify contrast (NFR-006) rather than trusting the eye.
  2. `src/theme/site/typography.css` — readable body type, sensible measure (~65–75 characters), a
     type scale for headings. The guide is long-form prose; measure matters more than personality.
  3. Enable Material's light/dark toggle and its built-in search.
  4. Stop there. No custom components, no bespoke layout.

- **Files**: `src/theme/site/palette.css`, `src/theme/site/typography.css`

- **Parallel?**: **[P]** — independent of T013–T015.

- **Notes**: If a reviewer cannot tell whether you have exceeded NFR-004, you probably have. The test:
  could this be described as "Material with a good palette and good type"? If not, it is out of scope.

### Subtask T013 – Landing page derived from the kit's pitch

- **Purpose**: FR-001 — the first thing a human reads is the guide's own pitch, not a directory.

- **Steps**:
  1. Extract the "What is this?" section from `src/pack/creator-kit.md` at build time.
  2. Render it as the site index — via an MkDocs hook in `src/build/site.py`, not by adding a file to
     the pack. Note `src/pack/README.md` is **not** the index: it is the pack branch's front door and is
     `not_in_book`. It publishes as an ordinary page and as raw markdown.
  3. Link the PDF prominently from the landing page (FR-004 requires it be linked prominently; WP04
     produces it, you surface it).
  4. Fail the build if the expected section cannot be found, rather than shipping an empty landing page.

- **Files**: `src/build/site.py`

- **Parallel?**: **[P]**

- **Notes**: Derivation over authoring is the point — an authored landing page is hand-written content
  that will drift from the kit (NFR-003). If the extraction is fragile, make the failure loud.

### Subtask T014 – Per-page AI pointer and `rel="alternate"` metadata

- **Purpose**: FR-002 — a model that lands on any rendered page should find the clean source in one hop,
  and a human should be able to see the link too.

- **Steps**:
  1. A Material template override in `src/theme/site/overrides/` adding, to every page:
     - a visible link: *"🤖 Reading this as an AI? The clean markdown source is here →"* pointing at
       that page's raw `.md`
     - `<link rel="alternate" type="text/markdown" href="…">` in the head
  2. Both URLs come from `config.absolute_url()` and must be subpath-correct.
  3. The bootstrap's page must point at `AGENTS.md`, not `start.md` — use `Document.published_name` from
     WP02, do not special-case it here.

- **Files**: `src/theme/site/overrides/main.html`, `src/build/site.py`

- **Parallel?**: No — shares the URL logic with T015.

- **Notes**: The visible link is for humans who want the source; the `rel="alternate"` is for machines
  that never render the page. Both are required.

### Subtask T015 – Raw markdown at parallel paths, with the bootstrap published as `AGENTS.md`

- **Purpose**: FR-007 and FR-008 — the machine surface itself.

- **Steps**:
  1. Copy every document from `src/pack/` into the site output at its parallel path, **byte-identical**
     to source.
  2. Publish using `Document.published_name` (WP02): `start.md` is published as `AGENTS.md`.
  3. Apply `rename.rewrite_references()` (WP02) to any published document referencing `start.md`, so the
     published raw markdown is internally consistent — a model fetching `AGENTS.md` and following a link
     to `start.md` would 404.
  4. Verify `/AGENTS.md` exists in the output and is the bootstrap.
  5. Honour WP01's finding: if the URL map was amended, publish the fallback twins instead.

- **Files**: `src/build/site.py`, `tests/test_site.py`

- **Parallel?**: No.

- **Notes**: This is the mission's whole reason for existing. `/AGENTS.md` is the one URL a creator hands
  to an LLM. If this subtask is subtly wrong, everything else still looks fine — which is exactly why
  WP01 went first, and why WP09 tests it against a real model.

### Subtask T016 – `.nojekyll`, subpath correctness, responsive and contrast verification

**Three additions since this prompt was written** — read them before starting; they resolve analysis
findings C2 and C3, and one carries a trap WP02 proved:

- **Add the theme hooks yourself, together with the files they name.** WP02 deliberately did NOT
  pre-declare them, and `mkdocs.yml` documents why: `theme.custom_dir` is validated eagerly, so naming a
  directory before it exists aborts every build in the four lanes depending on WP02; and **`extra_css`
  resolves relative to `docs_dir`, which is `src/pack/`** — declaring it would write build assets into
  the product (C-002, C-006) and fail the role lint. **Ship CSS through `custom_dir`**, i.e.
  `src/theme/site/overrides/stylesheets/extra.css` referenced from a `main.html` override. This is a
  small, sanctioned edit to WP02's `mkdocs.yml`, not an ownership violation.
- **Enable MkDocs link validation** (`validation.links.unrecognized_links: warn`, plus `anchors`) so
  `--strict` fails on a broken internal link in the rendered site. FR-013 requires cross-references
  resolve on *every* published surface; WP07 covers the two branches and WP04 T022 covers the book's
  flattened references, so this closes the site — the last uncovered surface (finding **C2**). Note
  WP02 already set `validation.nav.omitted_files: warn`; follow that pattern.
- **Assert the base-URL swap for the site's URLs** (finding **C3**). WP05 T026 tests it for
  `llms.txt`/`llms-full.txt`, but WP03 also generates addresses — the AI pointer, `rel="alternate"`,
  the PDF link. Build with base A, rebuild with base B, assert every generated address changed and none
  retained A. This is the test that catches a hard-coded hostname, and without it NFR-001/SC-006 hold for
  the machine files but not the site.

- **Purpose**: The conditions the whole surface rests on, verified rather than assumed.

- **Steps**:
  1. Emit `.nojekyll` into the site output. Without it, Pages runs Jekyll over the output and can hide
     or mangle the `.md` files T015 just published.
  2. Grep the built output for root-relative links (`href="/…"`). On a project site served from
     `/dungeon-masters-guide/`, those 404. Every link must be subpath-correct.
  3. Check at 320px: no horizontal scroll on any chapter, including the widest tables (NFR-002).
  4. Check contrast in light and dark against WCAG AA (NFR-006).

- **Files**: `src/build/site.py`, `tests/test_site.py`

- **Parallel?**: No.

- **Notes**: The guide contains wide tables (the tells comparison in `storytelling.md`, several
  requirement tables). Those are the ones that will overflow at 320px. Test with the real content, not a
  sample page.

## Test Strategy

```bash
poetry run pytest tests/test_site.py
poetry run mkdocs build --strict
```

Mandatory cases:

- Nav order in the built site matches the declaration.
- `/AGENTS.md` exists in the output and is the bootstrap's content.
- No published raw document contains an unrewritten `start.md` reference.
- `.nojekyll` is present in the output.
- No root-relative links in the built HTML.
- **Base-URL swap**: rebuild with a different base; every generated address follows, none retains the old
  one (C3, NFR-001, SC-006).
- **A broken internal link fails `mkdocs build --strict`** once link validation is enabled (C2, FR-013).
- Landing-page extraction fails loudly when the expected section is absent.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Scope creep into a bespoke theme | NFR-004 and A-004; reviewer checks the "Material with good palette/type" test |
| `/AGENTS.md` subtly wrong while the site looks perfect | T015's assertions; WP09's real-model test |
| Root-relative links 404 on the subpath | T016 greps the built output |
| Jekyll eats the raw markdown | `.nojekyll` emitted and asserted |
| Wide tables overflow on mobile | Test at 320px with the real chapters |
| A hard-coded hostname survives in the site while `llms.txt` is clean | Base-swap assertion in T016 (C3) |
| `extra_css` writes into `src/pack/` — a C-002/C-006 violation the role lint would then flag | Ship CSS via `custom_dir`; WP02 proved this and documented it in `mkdocs.yml` |
| An authored landing page drifts from the kit | Derive it; fail loudly if extraction breaks |

## Review Guidance

- Fetch `/AGENTS.md` from the built output: is it the bootstrap, and is it raw markdown?
- Does any published raw document still say `start.md`?
- `git diff --stat src/pack/` — must be empty.
- Is the styling defensible as "Material, lightly dressed", or has it become a project?
- Grep the output for hard-coded hostnames.

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
- 2026-07-16T21:06:52Z – claude:opus:frontend-freddy:implementer – shell_pid=2435 – Assigned agent via action command
- 2026-07-16T21:33:24Z – claude:opus:frontend-freddy:implementer – shell_pid=2435 – Ready for review: site + raw markdown surface. /AGENTS.md verified in output; base-swap and provenance pass. Four silent bugs found via real build/browser (README/index collision, font var shadowing, palette outranked by Material's indigo, .gitignore swallowing src/theme/site/) — see commit ab8791e.
