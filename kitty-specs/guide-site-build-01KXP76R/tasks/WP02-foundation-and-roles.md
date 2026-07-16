---
work_package_id: WP02
title: Build foundation and the roles declaration
dependencies: []
requirement_refs:
- FR-010
- FR-011
tracker_refs: []
planning_base_branch: feat/guide-site-build
merge_target_branch: feat/guide-site-build
branch_strategy: Planning artifacts for this mission were generated on feat/guide-site-build. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into feat/guide-site-build unless the human explicitly redirects the landing branch.
subtasks:
- T005
- T006
- T007
- T008
- T009
- T010
- T011
- T045
phase: Phase 1 - Foundation
assignee: ''
agent: "claude:opus:python-pedro:implementer"
shell_pid: "79720"
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: python-pedro
authoritative_surface: src/build/roles.py
create_intent:
- pyproject.toml
- poetry.lock
- mkdocs.yml
- src/build/__init__.py
- src/build/cli.py
- src/build/config.py
- src/build/roles.py
- src/build/rename.py
- src/build/provenance.py
- tests/conftest.py
- tests/test_roles.py
- tests/test_rename.py
- tests/test_provenance.py
execution_mode: code_change
model: ''
owned_files:
- pyproject.toml
- poetry.lock
- mkdocs.yml
- src/build/__init__.py
- src/build/cli.py
- src/build/config.py
- src/build/roles.py
- src/build/rename.py
- src/build/provenance.py
- tests/conftest.py
- tests/test_roles.py
- tests/test_rename.py
- tests/test_provenance.py
role: implementer
tags: []
task_type: implement
---

# Work Package Prompt: WP02 – Build foundation and the roles declaration

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

Stand up the Python build project, and — the part that matters — make the site config the **single
declaration** of chapter order and document roles, which every other work package derives from.

Success criteria:

- `poetry install` and `poetry run pytest` work from a clean checkout.
- `mkdocs.yml` declares the ten chapters in reading order and the two not-a-chapter documents.
- `roles.py` resolves every `.md` in `src/pack/` to exactly one role, and **fails loudly** on one it
  cannot.
- `roles.py` knows that `start.md`'s `published_name` is `AGENTS.md`.
- `rename.py` rewrites references to `start.md` **without touching `getting-started.md`**.
- The prose drift check reports mismatches between the declaration and the guide's prose lists — and
  never edits the prose.

## Context & Constraints

Read first: `kitty-specs/guide-site-build-01KXP76R/quickstart.md` (short, covers the traps), then
`contracts/roles-declaration.md` (the contract you are implementing) and `data-model.md` (the Document
entity and its invariants).

**Why one declaration.** The reading order already appears in four prose places across the guide, and
`mkdocs.yml` would make five. Rather than hand-sync five copies, the config is authoritative and the
prose is *verified* against it. This is spec assumption **A-002** and contract
`roles-declaration.md`. If you find yourself adding a second list of chapter names anywhere, stop —
that is the exact thing this WP exists to prevent.

**Why not front-matter.** The obvious alternative — a `role:` key in each document's YAML front-matter —
is rejected on a concrete ground: **these files are published raw and shipped to creators** (FR-007,
FR-009). Front-matter would appear in the markdown a creator reads at `doc/core/ethics.md` and in what a
model fetches from the site. Build metadata must not leak into the product.

**Constraints**:

- **Never write to `src/pack/`.** It is input. Content is out of scope (C-006), and the build is
  forbidden from editing prose (C-002). The drift check *reports*; it does not fix.
- Follow the repo's Python conventions: type hints on signatures, absolute imports, `click` for CLIs,
  `black`, `mypy`, `pytest`, Poetry.
- Runs in parallel with WP01. Do not wait for the spike — nothing here depends on its finding.

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T005 – Poetry project, dependencies, dev tooling, click entry point, test harness

- **Purpose**: A working Python project the other six subtasks and four downstream WPs build on.

- **Steps**:
  1. `pyproject.toml` via Poetry. Runtime deps: `mkdocs`, `mkdocs-material`, `pyyaml`, `click`.
     Dev deps: `pytest`, `black`, `mypy`.
  2. `src/build/__init__.py` and `src/build/cli.py` — a `click.Group` named `guide` with subcommands
     registered as later WPs add them. For now: a `roles` command group.
  3. `tests/conftest.py` — a fixture giving tests a temporary pack directory, so tests never depend on
     the real `src/pack/` contents (which change independently of this mission).
  4. Confirm `poetry run pytest`, `poetry run black --check .`, `poetry run mypy .` all run clean.

- **Files**: `pyproject.toml`, `poetry.lock`, `src/build/__init__.py`, `src/build/cli.py`,
  `tests/conftest.py`

- **Parallel?**: No — everything else here depends on it.

- **Notes**: `src/` in this repo is **not** a Python source root in the usual sense — `src/pack/` is
  markdown content. Configure packages explicitly (`packages = [{include = "build", from = "src"}]`) so
  Poetry does not try to package the guide.

### Subtask T006 – `mkdocs.yml`: the nav (ten chapters) and the `not_in_book` declaration

- **Purpose**: The single source of reading order and roles.

- **Steps**:
  1. Create `mkdocs.yml` with `docs_dir: src/pack`, `site_name`, and `theme: material`.
  2. `nav:` — the ten chapters, **in this order** (from `doc/build.md`, the requirements source):
     ```yaml
     nav:
       - Creator Kit: creator-kit.md
       - Getting Started: getting-started.md
       - How We Tell It: storytelling.md
       - Philosophy: philosophy.md
       - Improvisation: improvisation.md
       - Ethics: ethics.md
       - Communications: communications.md
       - Worked Example: worked-example.md
       - Technical Suggestions: technical-suggestions.md
       - Continuity Checker: story-continuity-checker-prompt.md
     ```
  3. Declare the not-a-chapter set:
     ```yaml
     extra:
       pack:
         not_in_book:
           - README.md
           - start.md
     ```
  4. Declare MkDocs' `not_in_nav` key listing the same two documents. `docs_dir` is `src/pack`, so they
     sit in the docs tree while being absent from `nav`, and `mkdocs build --strict` fails on that unless
     the omission is declared. `not_in_nav` suppresses it **without** weakening `--strict` — a new
     undeclared document still fails, which is what FR-011 wants. See
     `contracts/roles-declaration.md` § "The `--strict` interaction". Resolves analysis finding U2.
  5. Include the theme/`extra_css` hooks WP03 will populate, pointing at `src/theme/site/`, so WP03 only
     has to create files rather than edit this one.

- **Files**: `mkdocs.yml`

- **Parallel?**: No — T008 reads it.

- **Notes**: The nav order is not yours to invent; it is specified. If `src/pack/` contains a document
  not in either list, that is T010's job to catch, not yours to quietly add.

### Subtask T007 – `config.py`: the single base-URL configuration

- **Purpose**: NFR-001 — moving the guide to a custom domain must be a one-value change.

- **Steps**:
  1. `src/build/config.py` exposes the base URL, read from `mkdocs.yml`'s `site_url`.
  2. Default: `https://conspiracy-larp.github.io/dungeon-masters-guide/` — note the **trailing slash**
     and the **subpath** (C-003).
  3. Provide a single helper — e.g. `absolute_url(path: str) -> str` — that every other module uses.
     Nothing anywhere else may compose a URL by hand.

- **Files**: `src/build/config.py`

- **Parallel?**: **[P]** — independent of T008–T011 once T005 lands.

- **Notes**: This is a small file with a large job. The moment one module hard-codes a hostname, SC-006
  ("change one value") is false, and nobody notices until the domain switch. Make it awkward to bypass.

### Subtask T008 – `roles.py`: Document model, role resolution, `published_name`

- **Purpose**: The entity the whole build reasons about.

- **Steps**:
  1. Implement a `Document` per `data-model.md`: `filename`, `role` (`chapter` | `not_in_book`),
     `position`, `title`, `published_name`.
  2. `load_documents(pack_dir, config) -> list[Document]`: read `mkdocs.yml`, scan `src/pack/*.md`,
     resolve each file's role.
  3. `published_name`: identical to `filename`, **except** `start.md` → `AGENTS.md`.
  4. Expose the chapters in nav order — this is what the book, `llms.txt` and `llms-full.txt` consume.
  5. Validate: chapter positions contiguous from 1; no filename contains `/` (C-001 — a non-flat pack is
     a build failure).

- **Files**: `src/build/roles.py`, `tests/test_roles.py`

- **Parallel?**: No.

- **Notes**: `published_name` lives here rather than in the pack-branch builder deliberately — the site
  (WP03) *also* publishes the bootstrap as `AGENTS.md`, so both consumers need it. One definition, two
  users.

### Subtask T009 – `rename.py`: reference rewriting, with the `getting-started.md` trap covered

- **Purpose**: FR-010. Renaming the file is half the job; rewriting references to it is the other half,
  and skipping it ships broken links.

- **Steps**:
  1. `rewrite_references(text: str) -> str` — replace references to `start.md` with `AGENTS.md`, in both
     link targets and inline text.
  2. **The trap**: `getting-started.md` contains the substring `started.md`, and naive replacement of
     `start.md` must not corrupt it. Use a boundary-aware pattern — e.g. `(?<![\w-])start\.md` — and
     **write the test for `getting-started.md` first**.
  3. Keep this module pure: text in, text out. No filesystem, no git. WP06 handles the tree.

- **Files**: `src/build/rename.py`, `tests/test_rename.py`

- **Parallel?**: **[P]** — independent of T008.

- **Notes**: This trap is not hypothetical. The `pack` branch was built by hand on 2026-07-16 and this
  exact case had to be handled; a naive `sed s/start.md/AGENTS.md/g` corrupts `getting-started.md`.
  Both WP03 and WP06 depend on this being right, so it is worth the test.

### Subtask T010 – Role lint — an undeclared document fails the build

- **Purpose**: Convert a silent failure into a loud one. Spec risk **R-003**.

- **Steps**:
  1. `guide roles lint` (click command): every `.md` in `src/pack/` appears in exactly one of `nav` or
     `not_in_book`.
  2. Fail — non-zero exit, named file, actionable message — on: a document in neither; a document in
     both; a declaration naming a file that does not exist.
  3. Test each of the three failure modes, and the happy path against the real pack.

- **Files**: `src/build/roles.py`, `tests/test_roles.py`

- **Parallel?**: No.

- **Notes**: A warning is not good enough. The failure this prevents is a new document silently missing
  from the book, which nobody notices — a warning in a CI log is indistinguishable from silence.

### Subtask T011 – Prose drift check — report against the declaration, never fix

- **Purpose**: The guide's prose repeats the reading order in `src/pack/README.md` and `creator-kit.md`'s
  quick-read box. Keep them honest without ever editing them.

- **Steps**:
  1. `guide roles check-drift`: extract the document lists from those two files and compare against the
     declaration.
  2. Report any mismatch clearly — which file, which document, missing or extra.
  3. **Never write to `src/pack/`** (C-002, C-006). Report only.
  4. **Strictness is decided, not yours to choose**: drift **warns** (exit 0) on feature branches and
     **fails** (non-zero) on `main`. Rationale: prose and config drift naturally while someone is
     mid-edit, and a hard failure would punish the writer; but drift must never reach `main`, where the
     prose is what creators read. Implement exactly this; do not re-litigate it.

- **Files**: `src/build/roles.py`, `tests/test_roles.py`

- **Parallel?**: No.

- **Notes**: This is the one check that reaches into prose, and the temptation to auto-fix it will be
  strong. Don't. The guide's wording is the product; a script rewording it is exactly the failure C-002
  exists to prevent.

### Subtask T045 – Provenance check: every published file traces back to the pack

- **Purpose**: **NFR-003** — "100% of every published surface traces to a source document in the pack;
  zero hand-written pages." Nothing currently verifies this, and it is the mechanism by which **SC-004**
  ("no two surfaces can disagree") is claimed true *by construction*. Unverified, the mission's central
  architectural claim rests on convention rather than enforcement.

- **Steps**:
  1. `src/build/provenance.py` exposing `guide verify provenance --output <dir>`: walk a built output
     directory and assert every file is accounted for — either derived from a `src/pack/` document
     (by `published_name`) or on an explicit allow-list of known generated artifacts (`llms.txt`,
     `llms-full.txt`, `.nojekyll`, the PDF, the book, search indexes, theme assets).
  2. Any output file matching neither is a **failure**, naming the file: it is hand-authored content,
     which NFR-003 forbids.
  3. Keep the allow-list explicit and small. A wildcard defeats the check.
  4. WP08 wires this into CI's `verify` job; you provide the command.

- **Files**: `src/build/provenance.py`, `tests/test_provenance.py`

- **Parallel?**: **[P]** — independent of T006–T011 once T005 lands.

- **Notes**: This project has already been bitten twice by exactly this class of drift — the reading
  order diverged across four prose copies, and a hand-written link broke across two branches. Both were
  caught by luck. This is the check that replaces luck. Added in response to analysis finding **C1**.

## Test Strategy

`pytest`, against a temporary pack fixture — never the live `src/pack/`, whose contents change
independently of this mission.

Mandatory cases:

- Role resolution: chapter, not-a-chapter, undeclared (fails), double-declared (fails), missing file
  (fails).
- `published_name`: `start.md` → `AGENTS.md`; every other file unchanged.
- **`rewrite_references` leaves `getting-started.md` intact.** This is the regression test that matters.
- Non-flat pack (a file with `/`) fails.
- Drift check reports a mismatch and writes nothing; warns on a feature branch, fails on `main`.
- **Provenance**: an output file with no pack source and no allow-list entry **fails** (T045).

```bash
poetry run pytest
poetry run black --check . && poetry run mypy .
poetry run guide roles lint    # against the real pack: must pass today
```

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Naive `start.md` replacement corrupts `getting-started.md` | Boundary-aware pattern; test written first (T009) |
| A second copy of the reading order creeps in | Everything reads `mkdocs.yml`; review rejects any hard-coded chapter list |
| A module composes a URL by hand, breaking SC-006 | One `absolute_url()` helper (T007); review for hostname literals |
| The drift check "helpfully" edits prose | C-002 forbids it; T011 reports only |
| Tests coupled to real pack contents, breaking when the guide is edited | Temporary-pack fixture in `conftest.py` |

## Review Guidance

- Is there exactly **one** list of chapters in the repo? Grep for chapter filenames outside `mkdocs.yml`.
- Does a test prove `getting-started.md` survives the rename rewrite?
- Does the role lint **fail** (not warn) on an undeclared document?
- Does anything hard-code a hostname instead of using `config.absolute_url()`?
- Did anything write to `src/pack/`? `git diff --stat src/pack/` must be empty.

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
- 2026-07-16T20:30:55Z – claude:opus:python-pedro:implementer – shell_pid=79720 – Assigned agent via action command
- 2026-07-16T20:44:40Z – claude:opus:python-pedro:implementer – shell_pid=79720 – Ready for review: build foundation + roles declaration. 85 tests pass; black/mypy clean; roles lint and check-drift pass against the real pack; src/pack untouched. Two findings in commit msg: mkdocs --strict does NOT fail on undeclared docs by default (fixed via validation.nav.omitted_files: warn); extra_css/custom_dir hooks left for WP03 with rationale documented.
