---
work_package_id: WP08
title: Continuous publication
dependencies:
- WP03
- WP04
- WP05
- WP06
- WP07
requirement_refs:
- FR-012
tracker_refs: []
planning_base_branch: feat/guide-site-build
merge_target_branch: feat/guide-site-build
branch_strategy: Planning artifacts for this mission were generated on feat/guide-site-build. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into feat/guide-site-build unless the human explicitly redirects the landing branch.
subtasks:
- T036
- T037
- T038
- T039
- T040
phase: Phase 3 - Publication and acceptance
assignee: ''
agent: claude
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: implementer-ivan
authoritative_surface: .github/workflows/publish.yml
create_intent:
- .github/workflows/publish.yml
execution_mode: code_change
model: ''
owned_files:
- .github/workflows/publish.yml
role: implementer
tags: []
task_type: implement
---

# Work Package Prompt: WP08 – Continuous publication

## ⚡ Do This First: Load Agent Profile

Use the `/ad-hoc-profile-load` skill to load the agent profile specified in the frontmatter (or any
user-defined profile), and behave according to its guidance before parsing the rest of this prompt.

- **Profile**: `implementer-ivan`
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

No surface can lag another, and no human step stands between a change and its publication.

Success criteria:

- Every push to `main` rebuilds and redeploys **all** surfaces (FR-012).
- A change is live within **5 minutes** (NFR-005).
- A lint failure blocks **both** publication targets — Pages *and* the `pack` branch.
- Verified by actually pushing, not by reading the YAML.

## Context & Constraints

This WP integrates the five that precede it. Read their prompts' Test Strategy sections — the commands
they define are what you wire together.

**Why "block both" is a requirement, not a nicety.** `data-model.md` § Failure semantics: publishing a
valid site beside a broken branch (or vice versa) is *worse* than publishing neither. It is precisely how
a surface starts disagreeing with the guide's own text — the failure mode that makes the guide lie to
readers who already followed its instructions (R-002). One lint gate, both targets behind it.

**The 5-minute budget is mostly TeX's problem.** WP04 chose pandoc + XeLaTeX for print quality
(decision `01KXP7BCG6XFDHDRGZ57NXG90Q`), and installing a TeX distribution per run will blow NFR-005 on
its own. Use the prebuilt image WP04 specified.

**Prerequisite outside the code**: GitHub Pages must be enabled for the repository and permitted to
publish from Actions (dependency **D-002**). WP01's spike should already have confirmed this; if not,
confirm before writing the workflow.

**Constraints**:

- Publishing the `pack` branch happens **only** from CI on `main` (WP06, T030). Never from a PR, never
  from a fork, never from a laptop.
- Pages is a project site on the `/dungeon-masters-guide/` subpath (C-003).

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T036 – `publish.yml`: build, lint, deploy Pages

- **Purpose**: The pipeline.

- **Steps**:
  1. `.github/workflows/publish.yml`, triggered on push to `main` (and on pull_request for
     **build + lint only**, never publish).
  2. Job `verify`: `poetry install`, then
     - `guide roles lint` (WP02)
     - `guide links check` (WP07)
     - `poetry run pytest`
  3. Job `build`: the site (WP03), the book and PDF (WP04), `llms.txt`/`llms-full.txt` (WP05); assemble
     one Pages artifact including `.nojekyll` and the raw `.md` files.
  4. Job `deploy`: `actions/deploy-pages`, on `main` only.
  5. Remove WP01's spike workflow (`spike-content-type.yml`) if it is still present — it has served its
     purpose and a stray Pages-deploying workflow is a hazard.

- **Files**: `.github/workflows/publish.yml`

- **Parallel?**: No.

- **Notes**: PRs must build and lint but never deploy. A fork PR that could publish to Pages or
  force-push a branch would be a genuine security problem, not just a mistake.

### Subtask T037 – The pack-branch mirror job

- **Purpose**: FR-009/FR-010 in CI — the branch consumers actually attach to.

- **Steps**:
  1. Job `mirror`: `guide pack build` then `guide pack publish` (WP06), force-pushing to `origin pack`.
  2. **Only** on push to `main`. Never on PRs, never on forks.
  3. It needs write permission to the repo; scope the token narrowly.
  4. Must run **after** `verify` (T038).
  5. Idempotent: a re-run with no source change must not churn the branch meaningfully.

- **Files**: `.github/workflows/publish.yml`

- **Parallel?**: No.

- **Notes**: This force-pushes a branch that `5g_arg`'s submodule tracks. It is safe because the branch
  is read-only by contract — but that makes the `verify` gate before it non-negotiable.

### Subtask T038 – A lint failure blocks **both** publication targets

- **Purpose**: The failure semantics from `data-model.md`.

- **Steps**:
  1. Both `deploy` and `mirror` declare `needs: verify`.
  2. Test it for real: break a link on a branch, confirm **neither** target publishes. Reading the YAML
     is not evidence.
  3. Ensure a failure is visible — a red run, not a silently skipped job.

- **Files**: `.github/workflows/publish.yml`

- **Parallel?**: No.

- **Notes**: The temptation is to let the site deploy while the branch fails, since the site "looks
  fine". That is exactly the divergence this rule forbids.

### Subtask T039 – Baked TeX image to protect the 5-minute budget

- **Purpose**: NFR-005.

- **Steps**:
  1. Use the prebuilt pandoc/XeLaTeX image WP04 specified. Do not `apt-get install texlive-*` per run.
  2. Cache Poetry dependencies.
  3. Measure the real end-to-end time from push to live. Record it.
  4. If it exceeds 5 minutes, report with the measurement rather than quietly accepting it — NFR-005 is
     a stated threshold and missing it is a finding.

- **Files**: `.github/workflows/publish.yml`

- **Parallel?**: **[P]** — separable from T036/T037.

- **Notes**: A full TeX install is hundreds of megabytes and minutes. This subtask is the difference
  between meeting NFR-005 and missing it.

### Subtask T040 – Verify rebuild-and-redeploy actually happens on push

- **Purpose**: FR-012, proven rather than assumed.

- **Steps**:
  1. Push a real, trivial change to `main`.
  2. Confirm, on the live site: the change is visible; `llms-full.txt` contains it; the PDF regenerated;
     the `pack` branch tip moved.
  3. Time it against the 5-minute budget.
  4. Record the evidence in the Activity Log.

- **Files**: n/a — verification

- **Parallel?**: No.

- **Notes**: "All surfaces" means all. The most likely miss is the `pack` branch, because it is the one
  nobody looks at — and it is the one a downstream project is already tracking.

## Test Strategy

The workflow is verified by executing it, not by review:

- A PR: builds and lints, publishes nothing.
- A push to `main`: everything rebuilds and redeploys within 5 minutes.
- A deliberate lint failure: **neither** target publishes.
- A re-run with no change: the `pack` branch does not churn.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Pages not enabled / Actions not permitted (D-002) | Confirm before writing; WP01 should have settled it |
| Per-run TeX install blows NFR-005 | Prebuilt image (T039); measure and report |
| Site publishes while the branch fails → surfaces diverge | Both behind `needs: verify` (T038), tested for real |
| A PR or fork force-pushes `pack` or deploys Pages | Publish only on push to `main`; narrow token scope |
| WP01's spike workflow left deploying to Pages | T036 removes it |
| "It's in the YAML so it works" | T040 pushes a real change and looks |

## Review Guidance

- Can a pull request publish anything? It must not.
- Are `deploy` and `mirror` both gated on `verify`? Was that tested by breaking something?
- What is the measured push-to-live time?
- Is WP01's spike workflow gone?
- Did the `pack` branch tip actually move on a real push?

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
