---
work_package_id: WP01
title: Prove the machine surface can exist
dependencies: []
requirement_refs:
- FR-007
- FR-008
tracker_refs: []
planning_base_branch: feat/guide-site-build
merge_target_branch: feat/guide-site-build
branch_strategy: Planning artifacts for this mission were generated on feat/guide-site-build. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into feat/guide-site-build unless the human explicitly redirects the landing branch.
subtasks:
- T001
- T002
- T003
- T004
phase: Phase 1 - Foundation
assignee: ''
agent: "claude:opus:reviewer-renata:reviewer"
shell_pid: "87301"
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: researcher-robbie
authoritative_surface: spike/
create_intent:
- spike/probe.md
- spike/probe.txt
- spike/.nojekyll
- spike/index.html
- .github/workflows/spike-content-type.yml
- spike/FINDINGS.md
execution_mode: code_change
model: ''
owned_files:
- spike/**
- .github/workflows/spike-content-type.yml
role: researcher
tags: []
task_type: research
---

# Work Package Prompt: WP01 – Prove the machine surface can exist

## ⚡ Do This First: Load Agent Profile

Use the `/ad-hoc-profile-load` skill to load the agent profile specified in the frontmatter (or any
user-defined profile), and behave according to its guidance before parsing the rest of this prompt.

- **Profile**: `researcher-robbie`
- **Role**: `researcher`
- **Agent/tool**: `claude`

If no profile is specified, run `spec-kitty agent profile list` and select the best match for this work
package's `task_type` and `authoritative_surface`.

---

## Markdown Formatting

Wrap HTML/XML tags in backticks: `` `<div>` ``, `` `<script>` ``
Use language identifiers in code blocks: ` ```python `, ` ```bash `

---

## Objectives & Success Criteria

**Answer one question with evidence: does GitHub Pages serve a raw `.md` file as text an LLM can read?**

This work package is a spike. It produces a finding, not a feature. It is done when a real HTTP response
from a real deployment is recorded, and `contracts/url-map.md` has been confirmed or amended.

Success criteria:

- A recorded `curl -i` response for a `.md` served from GitHub Pages, showing the actual `Content-Type`
  and any `Content-Disposition`.
- The same for a `.txt` twin and an extensionless twin — because those are the fallbacks, and knowing
  now costs one extra file.
- Confirmation that `.nojekyll` is honoured and the subpath behaves as expected.
- `contracts/url-map.md` condition **C1** marked confirmed, or amended with the fallback.
- The throwaway deployment removed, or clearly marked as a spike, before you finish.

## Context & Constraints

**Why this exists, and why it is first.** Everything machine-facing in this mission — FR-007 (raw
markdown at parallel URLs) and FR-008 (`/AGENTS.md` as the one URL you hand an LLM) — depends on a
behaviour that **the host controls and we do not**. Two failure modes:

1. Without `.nojekyll`, Pages runs the site through Jekyll, which processes markdown and may not serve
   `.md` at all.
2. Even served, the platform chooses the content type. If `.md` arrives as a download or is rendered to
   HTML, the machine surface fails **while the site looks perfect**.

That second one is spec risk **R-001** and it is the most dangerous thing in this mission, because the
failure is *invisible*. You cannot find it by reading the site. You cannot find it locally — a local
`mkdocs serve` proves nothing about what Pages does. And by the time anyone notices, the theme is
polished and the URL map is baked into the guide's published text.

Read before starting:

- `kitty-specs/guide-site-build-01KXP76R/contracts/url-map.md` — the contract you are testing, especially
  condition **C1** and the Amendment rule.
- `kitty-specs/guide-site-build-01KXP76R/research.md` § R3 — the reasoning and the designed fallback.
- `kitty-specs/guide-site-build-01KXP76R/spec.md` — FR-007, FR-008, R-001.

**Constraints**:

- **Do not touch `src/pack/`.** Content is out of scope (C-006).
- **Do not build the site.** That is WP03. You are proving a precondition, not implementing anything.
- The real deployment is a project site on a **subpath** (`/dungeon-masters-guide/`), not a domain root
  (C-003). Your spike must reproduce that shape or it proves nothing about the real thing.

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T001 – Stand up a throwaway Pages deployment with `.nojekyll` and probe files

- **Purpose**: Create the smallest possible thing that can answer the question honestly. Not the site —
  just enough to make the host reveal its behaviour.

- **Steps**:
  1. Create `spike/` containing:
     - `.nojekyll` (empty file)
     - `probe.md` — a few lines of markdown, including a heading and a link, so you can tell whether it
       arrives as source or as rendered HTML
     - `probe.txt` — the same content, different extension (fallback candidate)
     - `probe` — the same content, no extension (fallback candidate)
     - `index.html` — a one-line page, so the deployment is obviously a spike and not a mistake
  2. Add `.github/workflows/spike-content-type.yml` that publishes **only `spike/`** to Pages via
     `actions/upload-pages-artifact` + `actions/deploy-pages`.
  3. Confirm with the repository owner that Pages is enabled and permitted to publish from Actions
     (dependency **D-002**). If it is not, stop and report — this is an account-level setting, not code.

- **Files**: `spike/.nojekyll`, `spike/probe.md`, `spike/probe.txt`, `spike/probe`,
  `spike/index.html`, `.github/workflows/spike-content-type.yml`

- **Parallel?**: No. T002 depends on it being live.

- **Notes**: Keep it obviously disposable. Someone will find this branch later and wonder what it is —
  put a one-line comment at the top of the workflow saying it is a WP01 spike and is expected to be
  deleted.

### Subtask T002 – Record the actual HTTP response for `.md`, and for `.txt`/extensionless twins

- **Purpose**: Get evidence, not an impression. The finding must be a recorded response, so a reader in
  six months can check it rather than trust it.

- **Steps**:
  1. Once deployed, for each of `probe.md`, `probe.txt`, `probe`:
     ```bash
     curl -isS "https://conspiracy-larp.github.io/dungeon-masters-guide/<file>" | head -20
     ```
  2. Record for each: HTTP status, `Content-Type`, presence of `Content-Disposition`, and whether the
     body is the markdown **source** or rendered HTML.
  3. Fetch `probe.md` the way a model would — a plain GET with no browser headers — and confirm the body
     is the source text.
  4. Confirm `.nojekyll` was honoured: the `.md` exists at all, and was not renamed or converted.
  5. Write the raw responses into `spike/FINDINGS.md`. Paste the
     actual headers. Do not paraphrase them.

- **Files**: `spike/FINDINGS.md`

- **Parallel?**: No.

- **Notes**: The interesting distinction is **readable vs. downloadable**, not "does it 200". A file can
  return 200 and still be useless to a model if it arrives as an attachment. Judge the response the way a
  model would experience it.

### Subtask T003 – Decide: confirm the URL map, or specify the fallback

- **Purpose**: Convert the evidence into a decision the rest of the mission can build on.

- **Steps**:
  1. If `.md` serves as readable text: condition **C1** holds. The URL map stands. Say so explicitly.
  2. If it does not, choose and specify the fallback, in this order of preference:
     - **`.txt` twins** — publish `<doc>.md.txt` alongside, and point `llms.txt` at those.
     - **Extensionless twins** — publish `<doc>` with an explicit content type if the host allows it.
     - **Fly** — full control over headers, but reintroduces infrastructure the stakeholder explicitly
       does not want (C-003). Last resort only, and it needs stakeholder sign-off.
  3. Record the decision with its rationale and the evidence that drove it.

- **Files**: `spike/FINDINGS.md`

- **Parallel?**: No.

- **Notes**: Prefer the fallback that changes the guide's published text *least*. Every address the guide
  quotes to readers is a promise it has already made.

### Subtask T004 – Amend `contracts/url-map.md`; escalate if the guide's own text must change

- **Purpose**: Make the finding binding on every downstream WP, and surface the consequence if it is
  expensive.

- **Steps**:
  1. Update `contracts/url-map.md`: mark **C1** confirmed (with the recorded content-type) or amend the
     map to the chosen fallback.
  2. **If the map changed**: stop and escalate. Per the contract's own Amendment rule, a changed map also
     changes `src/pack/start.md`, `src/pack/README.md` and `src/pack/technical-suggestions.md`, which
     quote addresses and commands to readers — and **content is out of scope for this mission (C-006)**.
     That is a stakeholder decision, not an implementer's.
  3. Remove the spike deployment, or leave it clearly marked. Do not leave a mystery workflow behind.
  4. Report the finding in the Activity Log in one plain sentence: does the machine surface work, yes or
     no.

- **Files**: `kitty-specs/guide-site-build-01KXP76R/contracts/url-map.md`

- **Parallel?**: No.

- **Notes**: A "no" here is a **good outcome for this WP** — it is exactly what the spike exists to find,
  and finding it now is worth more than any amount of downstream progress. Do not soften a negative
  finding.

## Test Strategy

No automated tests. The deliverable is evidence: recorded HTTP responses from a real deployment, pasted
verbatim.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Pages is not enabled, or Actions cannot deploy (D-002) | Confirm with the owner in T001, before writing anything |
| The spike proves something about a domain root, not our subpath | Reproduce the project-site subpath shape exactly (C-003) |
| A "works in my browser" conclusion | Judge as a model would: plain GET, inspect headers, not the rendering |
| The spike deployment is left behind and confuses someone | T004 removes or marks it |
| A negative finding gets softened to avoid blocking the mission | A negative finding *is* the mission's most valuable output right now |

## Review Guidance

- Are actual HTTP headers pasted in, or are they paraphrased? Only the former is evidence.
- Was the extensionless/`.txt` fallback probed *while the spike was up*? Re-deploying to learn it later
  is wasted effort.
- Does `contracts/url-map.md` now state a definite outcome for C1?
- If the map changed, was it escalated rather than absorbed by editing `src/pack/`?

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
- 2026-07-16T20:30:29Z – claude:opus:researcher-robbie:researcher – shell_pid=79084 – Assigned agent via action command
- 2026-07-16T20:38:22Z – claude:opus:researcher-robbie:researcher – shell_pid=79084 – Yes — the machine surface works: GitHub Pages serves raw .md from the subpath as text/markdown; charset=utf-8, readable source with no download disposition, so C1 is confirmed and the URL map needs no amendment.
- 2026-07-16T20:41:56Z – claude:opus:reviewer-renata:reviewer – shell_pid=87301 – Started review via action command
- 2026-07-16T20:43:56Z – user – shell_pid=87301 – Review passed: evidence-grade spike. Verbatim curl -i headers from the REAL project-site subpath (conspiracy-larp.github.io/dungeon-masters-guide/, run 29532549096, deployed from the lane branch) — not a domain root, not local. Independently re-probed live: probe.md=text/markdown; charset=utf-8, probe.txt=text/plain, probe=application/octet-stream, no Content-Disposition on any, live body sha256 matches the recorded sha AND the committed probe files (all three byte-identical at 614 bytes, so extension was the only variable). .txt/extensionless fallbacks probed while the spike was up, as required. C1 marked CONFIRMED in contracts/url-map.md (6441d18, correctly on the planning branch per lane guard); map unchanged, no fallback adopted, Amendment rule not triggered, git diff --stat src/pack/ empty (C-006 respected). Cleanup verified: spike workflow file absent from every branch, probe files deleted, github-pages deployment-branch policy back to main-only (temp policy 54841701 gone). Sole residue is the still-live spike index.html, which FINDINGS.md discloses honestly and which self-describes as a throwaway — acceptable per the 'removed OR clearly marked' criterion. Bonus value: evidence corrects research R3's fallback order (extensionless is octet-stream, worse than the problem). No unrelated changes.
