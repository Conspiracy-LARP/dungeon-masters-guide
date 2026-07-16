---
work_package_id: WP06
title: The pack branch
dependencies:
- WP02
requirement_refs:
- FR-009
- FR-010
tracker_refs: []
planning_base_branch: feat/guide-site-build
merge_target_branch: feat/guide-site-build
branch_strategy: Planning artifacts for this mission were generated on feat/guide-site-build. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into feat/guide-site-build unless the human explicitly redirects the landing branch.
subtasks:
- T027
- T028
- T029
- T030
- T031
phase: Phase 2 - The surfaces
assignee: ''
agent: "claude:opus:python-pedro:implementer"
shell_pid: "2435"
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: python-pedro
authoritative_surface: src/build/packbranch.py
create_intent:
- src/build/packbranch.py
- tests/test_packbranch.py
execution_mode: code_change
model: ''
owned_files:
- src/build/packbranch.py
- tests/test_packbranch.py
role: implementer
tags: []
task_type: implement
---

# Work Package Prompt: WP06 – The pack branch

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

Publish the guide's markdown alone — flat, under the filename models look for — as the branch creators
attach to their own projects.

Success criteria:

- A `pack` branch tree containing exactly `src/pack/`'s files, flat, with no build machinery and no
  meta-documentation (FR-009).
- `start.md` published as `AGENTS.md`, with every reference to it rewritten (FR-010).
- **The generated tree is byte-identical to the existing hand-built `d024682`** (C-005).
- The publisher force-pushes idempotently and states the read-only contract on the branch.

## Context & Constraints

Read first: `contracts/pack-branch.md` — it is your spec, both halves (consumer and producer). Then
`research.md` § R4 and `quickstart.md`.

**Read this twice: someone is already depending on this branch.**

It was created **by hand on 2026-07-16** as commit `d024682`, to unblock the `5g_arg` project, whose
`doc/core` submodule points at it. The guide *already tells readers* to run
`git submodule add -b pack … doc/core` — in `src/pack/start.md`, `src/pack/README.md` and
`src/pack/technical-suggestions.md`. Those are promises already made. If your automation produces a
different tree, the guide starts lying to people who followed its published instructions (spec risk
**R-002**). Hence the reproduction gate in T029: **match the hand-built tree before you take over.**

**Why an orphan mirror, not a subtree split.** `doc/build.md` suggests `git subtree split`, and
`research.md` § R4 rejects it: the branch must also apply a **rename and a reference rewrite**, which a
subtree split cannot do. Preserved per-file history has no value to consumers, who only ever read the
tip. A force-pushed orphan commit is idempotent and cannot drift.

**Constraints**:

- **Never write to `src/pack/`** (C-002, C-006).
- Reuse `rename.rewrite_references()` and `Document.published_name` from WP02. Do not reimplement the
  rename here — WP03 uses the same logic, and one definition means one fix.
- The branch is **read-only by contract**. It is force-pushed; nobody may commit to it directly.

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T027 – `packbranch.py`: the orphan mirror tree builder

- **Purpose**: Build the tree that becomes the branch, as a pure function of `src/pack/`.

- **Steps**:
  1. `guide pack build --out <dir>` (click command): materialise the branch tree into a directory.
  2. Contents: **exactly** the `.md` files of `src/pack/`, flat. Nothing else — no `src/`, no `doc/`,
     no `.github/`, no `mkdocs.yml`, no build files (contract, Producer table).
  3. Derive the file list from `roles.load_documents()` (WP02), not a glob, so a document missing a role
     fails here too rather than being silently mirrored.
  4. Keep tree-building separate from pushing (T030). A pure builder is testable; a builder that pushes
     is not.

- **Files**: `src/build/packbranch.py`

- **Parallel?**: No.

- **Notes**: The exclusion list is the whole point of the branch — creators asked for the markdown and
  none of the machinery. Anything extra that leaks in is a defect, not a convenience.

### Subtask T028 – Apply rename and reference rewrite to the branch tree

- **Purpose**: FR-010 — the two-part job the contract warns about.

- **Steps**:
  1. Write `start.md`'s content to `AGENTS.md` in the output tree. `start.md` must not exist on the
     branch.
  2. Apply `rename.rewrite_references()` (WP02) to **every** document in the tree, so references to
     `start.md` become `AGENTS.md`. Today only `README.md` contains one — do not special-case it; the
     next document to reference it must be handled automatically.
  3. The invariant: **links resolve on every branch.** They say `start.md` on `main`, where that file
     exists, and `AGENTS.md` on `pack`, where it exists. WP07 enforces this; you produce it.

- **Files**: `src/build/packbranch.py`

- **Parallel?**: No.

- **Notes**: This is exactly where the hand-build nearly went wrong. Renaming the file without rewriting
  references gives a branch whose `README.md` links to a file that does not exist. Both halves, always.

### Subtask T029 – Reproduction gate against the hand-built `d024682`

- **Purpose**: C-005 — prove the automation matches what consumers already have before it takes over.

- **Steps**:
  1. Fetch `d024682` (the current `pack` tip) and compare it, file by file and byte for byte, against
     your generated tree.
  2. It must match exactly. If it does not, **stop and investigate** — one of the two is wrong, and you
     must know which before force-pushing over a branch someone's submodule tracks.
  3. Record the comparison result in the Activity Log.
  4. Note: if `src/pack/` has legitimately changed since 2026-07-16, the trees will differ for good
     reasons. Compare against `d024682`'s *inputs*, or regenerate from that commit's `src/pack/`, rather
     than assuming a mismatch means a bug.

- **Files**: `src/build/packbranch.py`, `tests/test_packbranch.py`

- **Parallel?**: No.

- **Notes**: This gate exists because the hand-build was a real deployment to a real consumer, not a
  rehearsal. Treat a mismatch as a serious finding.

### Subtask T030 – Force-push publisher; read-only contract stated in the commit message

- **Purpose**: Ship it, idempotently, and tell the next person the rules.

- **Steps**:
  1. `guide pack publish` — create an orphan commit from the built tree and force-push to `origin pack`.
  2. Idempotent: same input, same tree. Re-running with no source change must not produce a meaningfully
     different branch.
  3. The commit message must state that the branch is **generated and force-pushed**, that nobody should
     commit to it directly, and that the source is `src/pack/` on `main`. Match the existing message on
     `d024682`.
  4. Guard it: publishing must only happen from CI on `main` (WP08 wires that), never accidentally from
     a developer's machine.

- **Files**: `src/build/packbranch.py`

- **Parallel?**: No.

- **Notes**: Force-pushing a branch that consumers pin is safe **only** because it is a read-only
  reference. Say so on the branch itself; the person who tries to commit to it will read that message.

### Subtask T031 – Tests, including the `getting-started.md` substring trap

- **Purpose**: Protect the rename, the exclusions, and the consumer's paths.

- **Steps**:
  1. `AGENTS.md` exists in the tree; `start.md` does not.
  2. **`getting-started.md` is present and uncorrupted** — the substring trap. It is tested in WP02 for
     the pure function; test it here for the assembled tree.
  3. No excluded path leaks: assert absence of `src/`, `doc/`, `mkdocs.yml`, `.github/`.
  4. No document in the tree contains an unrewritten `start.md` reference.
  5. Every consumer path from the contract exists: `creator-kit.md`, `AGENTS.md`, `README.md`, etc.
  6. Use the temporary pack fixture (WP02 `conftest.py`).

- **Files**: `tests/test_packbranch.py`

- **Parallel?**: No.

- **Notes**: Test the *tree*, not the push. Pushing is a thin wrapper; the tree is the contract.

## Test Strategy

```bash
poetry run pytest tests/test_packbranch.py
poetry run guide pack build --out /tmp/packtree && ls /tmp/packtree
```

Mandatory: `AGENTS.md` present / `start.md` absent; `getting-started.md` intact; no machinery leaked; no
unrewritten references; reproduction gate against `d024682` green.

**Consumer smoke test** (also SC-002 in WP09, but cheap to run here):

```bash
git submodule add -b pack git@github.com:Conspiracy-LARP/dungeon-masters-guide.git doc/core
ls doc/core/AGENTS.md doc/core/creator-kit.md
```

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| **A live consumer already tracks this branch** (`5g_arg`) | Reproduction gate (T029) before any force-push |
| Naive rename corrupts `getting-started.md` | Reuse WP02's boundary-aware `rename.py`; assert in T031 |
| File renamed but references not rewritten → broken links on the branch | T028 does both; WP07 enforces |
| Build machinery leaks onto the branch | Explicit exclusions; T031 asserts absence |
| Accidental force-push from a laptop | T030 guards to CI-on-`main` only |
| Someone commits directly to the branch and loses it | Read-only contract stated in the commit message |

## Review Guidance

- Clone the generated branch and `ls`. Is it *only* markdown?
- Does `getting-started.md` survive intact?
- Does any file on the branch still reference `start.md`?
- Was the reproduction gate against `d024682` actually run, with its result recorded?
- Is the rename reusing WP02's `rename.py`, or was it reimplemented here?

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
- 2026-07-16T21:07:07Z – claude:opus:python-pedro:implementer – shell_pid=2435 – Assigned agent via action command
- 2026-07-16T21:14:23Z – claude:opus:python-pedro:implementer – shell_pid=2435 – Ready for review: reproduction gate GREEN — generated tree byte-identical to d024682 (same git tree object 8d90209, all 12 files). getting-started.md intact. Builder pure and separate from publisher; publish guarded to CI-on-main; no force-push performed.
