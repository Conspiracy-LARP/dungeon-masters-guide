---
work_package_id: WP05
title: The machine-readable sources
dependencies:
- WP01
- WP02
requirement_refs:
- FR-005
- FR-006
tracker_refs: []
subtasks:
- T023
- T024
- T025
- T026
phase: Phase 2 - The surfaces
assignee: ''
agent: claude
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: python-pedro
authoritative_surface: src/build/llms.py
create_intent:
- src/build/llms.py
- tests/test_llms.py
execution_mode: code_change
model: ''
owned_files:
- src/build/llms.py
- tests/test_llms.py
role: implementer
tags: []
task_type: implement
---

# Work Package Prompt: WP05 – The machine-readable sources

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

Let a model consume the guide — and, more importantly, discover that there is a **procedure to follow**
rather than a pile of documents to read.

Success criteria:

- `llms.txt` follows the llmstxt.org convention, and its **first, most prominent entry is the bootstrap,
  described as a procedure** (FR-005).
- `llms-full.txt` is every chapter concatenated in the declared reading order (FR-006).
- Every address derives from the one configured base — changing it changes them all (NFR-001, SC-006).
- Both generated; neither hand-written (NFR-003).

## Context & Constraints

Read first: `contracts/llms-txt.md` — it is short and it *is* your spec, including the exact shape and
the one deliberate deviation from the convention. Also `research.md` § R8.

**The deviation is the point.** The llmstxt convention is designed for models that want to **read** a
project. This guide wants models to **act**: a creator's whole interaction is "read this URL and do what
it says." An `llms.txt` that dutifully lists ten chapters alphabetically would satisfy the convention
and defeat the mission — a model would read the entire guide and then ask the creator what they want,
having missed that a scripted interview exists. So the bootstrap leads, and it is labelled as a
procedure.

**Do not start before WP01 reports.** Your link targets point at raw `.md` (contract `llms-txt.md`
rule 5), and that depends on url-map condition **C1**, which WP01 is proving. If the map was amended,
your targets change.

**Constraints**:

- **Never write to `src/pack/`** (C-002, C-006).
- Chapter list and order come from `roles.load_documents()` (WP02). Never hard-code them.
- Every URL through `config.absolute_url()` (WP02, T007). Never compose one by hand — the subpath and
  the future domain switch both depend on it (C-003, NFR-001).
- `config.py` is owned by WP02; you consume it.

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T023 – `llms.py`: `llms.txt`, bootstrap first, as a procedure

- **Purpose**: FR-005 — the machine index, shaped so a model acts rather than reads.

- **Steps**:
  1. `guide llms index` (click command) emitting `llms.txt` per `contracts/llms-txt.md`:
     - `# The Dungeon Master's Guide`
     - a blockquote summary that tells a model it may **act**, not just read
     - a leading `## Start here` section whose sole entry is the bootstrap, at
       `{base}AGENTS.md`, described as a complete procedure to follow
     - `## The guide` — the chapters, generated in nav order with their titles
     - `## Everything` — `llms-full.txt`
  2. Use `Document.published_name` (WP02) so the bootstrap is linked as `AGENTS.md`, never `start.md`.
  3. Do not hand-write the chapter list. It is generated from the declaration, or it will drift.

- **Files**: `src/build/llms.py`

- **Parallel?**: No — T024 shares the module.

- **Notes**: Read the sample in `contracts/llms-txt.md` and match its intent. The blockquote is
  load-bearing prose: it is the sentence that tells a model it does not need to read ten chapters first.

### Subtask T024 – `llms-full.txt`: chapters concatenated in nav order

- **Purpose**: FR-006 — the whole guide in one fetch, for a model that wants all of it.

- **Steps**:
  1. `guide llms full` emitting `llms-full.txt`: every **chapter**, in nav order, concatenated.
  2. Separate chapters clearly so a model can tell where one ends — a heading or a delimiter comment.
  3. Chapters only. `README.md` and `start.md` are `not_in_book`
     (`contracts/roles-declaration.md`); the bootstrap has its own address and is not buried here.
  4. Preserve source bytes. This is the guide's text, not a rendering of it.

- **Files**: `src/build/llms.py`

- **Parallel?**: **[P]** — separable from T023.

- **Notes**: Same order as the book (WP04), from the same declaration. If these two ever disagree, the
  declaration is not being used somewhere.

### Subtask T025 – Every address derives from the configured base

- **Purpose**: NFR-001 and SC-006 — a domain switch must be a one-value change.

- **Steps**:
  1. Route every URL in both outputs through `config.absolute_url()` (WP02).
  2. Verify subpath correctness: addresses must be
     `https://conspiracy-larp.github.io/dungeon-masters-guide/AGENTS.md`, not
     `https://conspiracy-larp.github.io/AGENTS.md` (C-003).
  3. Grep your own output for a hard-coded hostname before you call this done.

- **Files**: `src/build/llms.py`

- **Parallel?**: No.

- **Notes**: The failure mode is invisible until the day a domain is bought, and then it is a scavenger
  hunt. One helper, no exceptions.

### Subtask T026 – Tests, including the base-URL swap (SC-006)

- **Purpose**: Prove the shape and the relocatability.

- **Steps**:
  1. `llms.txt`: bootstrap is the **first** link and appears before any chapter; it points at
     `AGENTS.md`, not `start.md`; every chapter present in nav order.
  2. `llms-full.txt`: chapters in nav order; `not_in_book` documents absent; content byte-preserved.
  3. **The SC-006 test**: build with base A, rebuild with base B, assert every address changed and none
     retained A. This is the one that catches a hard-coded hostname.
  4. Use the temporary pack fixture (WP02 `conftest.py`), not the live pack.

- **Files**: `tests/test_llms.py`

- **Parallel?**: No.

- **Notes**: The base-swap test is cheap and it is the only thing standing between you and a
  find-and-replace scramble later.

## Test Strategy

```bash
poetry run pytest tests/test_llms.py
poetry run guide llms index && poetry run guide llms full
```

Mandatory: bootstrap first in `llms.txt` and linked as `AGENTS.md`; chapters generated in nav order, not
hand-listed; `llms-full.txt` excludes `not_in_book`; base-URL swap changes every address; `src/pack/`
unmodified.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Convention followed literally, bootstrap buried, mission defeated | Contract rule 1; T026 asserts bootstrap is first |
| A hard-coded hostname breaks the future domain switch | `absolute_url()` only; base-swap test (T026) |
| Links point at `start.md`, which does not exist on the site | Use `published_name` (WP02) |
| Root-level addresses instead of subpath | T025 verifies against C-003 |
| Link targets wrong because C1 was amended | Wait for WP01 before finalising targets |

## Review Guidance

- Read the generated `llms.txt` **as a model would**. Does it tell you, in the first ten lines, that
  there is a procedure? Or does it look like a table of contents?
- Is the bootstrap linked as `AGENTS.md`?
- Is any chapter list hand-written?
- Does the base-swap test exist and pass?

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
