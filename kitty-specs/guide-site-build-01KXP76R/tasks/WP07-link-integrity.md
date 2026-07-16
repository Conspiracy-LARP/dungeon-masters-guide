---
work_package_id: WP07
title: Link integrity across branches
dependencies:
- WP06
requirement_refs:
- FR-013
tracker_refs: []
planning_base_branch: feat/guide-site-build
merge_target_branch: feat/guide-site-build
branch_strategy: Planning artifacts for this mission were generated on feat/guide-site-build. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into feat/guide-site-build unless the human explicitly redirects the landing branch.
subtasks:
- T032
- T033
- T034
- T035
phase: Phase 2 - The surfaces
assignee: ''
agent: "claude:opus:reviewer-renata:reviewer"
shell_pid: "12712"
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: python-pedro
authoritative_surface: src/build/links.py
create_intent:
- src/build/links.py
- tests/test_links.py
execution_mode: code_change
model: ''
owned_files:
- src/build/links.py
- tests/test_links.py
role: implementer
tags: []
task_type: implement
---

# Work Package Prompt: WP07 – Link integrity across branches

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

Machine-enforce the invariant the whole architecture rests on.

Success criteria:

- Every relative link between pack documents resolves **on `main`**, where the bootstrap is `start.md`.
- Every relative link resolves **on the `pack` branch**, where it is `AGENTS.md`.
- No relative link contains a path separator (C-001).
- Inline-code examples are excluded — the guide documents the link convention using inline code, and
  those samples are illustrations, not links.
- Runs in CI and fails the build (FR-013).

## Context & Constraints

Read first: `data-model.md` § Cross-reference — it states the three rules precisely. Then `research.md`
§ R7 and `quickstart.md`.

**Why rule 3 is not redundant with rule 2.** They have already disagreed in this project's history. On
2026-07-16, `src/pack/README.md` was written with a link to `AGENTS.md`: correct on the `pack` branch,
a 404 on `main`, where the file is `start.md`. It was caught only by an ad-hoc check that happened to be
run. That is precisely the class of error a human misses and a machine catches for free — and it is why
this WP exists.

**Why the code-example exclusion matters.** The guide *teaches* the bare-sibling-link convention, and it
does so by showing examples in inline code — in `quickstart.md`, in `CLAUDE.md`, in `doc/build.md`. A
naive extractor will treat `` `[ethics.md](ethics.md)` `` inside backticks as a real link and, worse,
will flag the guide's own explanatory prose as a violation. The checker must distinguish a link from a
picture of a link.

**Constraints**:

- **Never write to `src/pack/`** (C-002, C-006). Report; do not fix.
- Depends on WP06: you need the pack-branch tree builder to check the branch's links.

**Your scope is the two branches, and that is deliberate** (resolves analysis finding C2). FR-013 says
cross-references must resolve on *every* published surface; the other two are covered elsewhere, so do
not duplicate them:

| Surface | Covered by |
|---|---|
| `main` (bootstrap is `start.md`) | **you** — T034 |
| `pack` branch (bootstrap is `AGENTS.md`) | **you** — T034 |
| The rendered site | WP03 — MkDocs link validation under `--strict` |
| The book | WP04 T022 — the cross-reference flattening tests |

The two branches are where the risk actually lives, because they are the only surfaces where the *same
bytes* must resolve against *different filenames*. That asymmetry has already broken once.

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T032 – `links.py`: extract links, excluding inline-code examples

- **Purpose**: Find the real links, and only the real links.

- **Steps**:
  1. `extract_links(text: str) -> list[Link]` returning target and source position.
  2. **Exclude** fenced code blocks (```` ``` ````) and inline code (`` ` ``) before extracting. Per
     `data-model.md`, a Cross-reference has `context: prose | code_example`, and only `prose` counts.
  3. Exclude external links (`http://`, `https://`, `mailto:`) and pure anchors (`#…`) — this checker is
     about relative sibling links.
  4. Test against the guide's real documents: `quickstart.md` and `CLAUDE.md` both contain inline-code
     link samples that must **not** be extracted.

- **Files**: `src/build/links.py`, `tests/test_links.py`

- **Parallel?**: No.

- **Notes**: Get the exclusion right before the assertions, or every subsequent rule fires on false
  positives and someone disables the check.

### Subtask T033 – Assert no path separators in any cross-link (C-001)

- **Purpose**: Protect the property that lets one set of bytes serve four surfaces.

- **Steps**:
  1. Any relative link target containing `/` fails, naming file and line.
  2. The error message should explain *why*, not just what — the next person needs to know this is
     load-bearing, not pedantry. Something like: *"`src/pack/ethics.md` — links must be bare sibling
     names (`ethics.md`), because the same bytes are served from four different roots."*
  3. Test both directions: a bare name passes, a pathed name fails.

- **Files**: `src/build/links.py`

- **Parallel?**: **[P]** — independent of T034.

- **Notes**: This one rule is the reason the pack must stay flat. A helpful IDE "fix" that turns
  `ethics.md` into `src/pack/ethics.md` breaks the site, the book, the branch and GitHub's rendering
  simultaneously.

### Subtask T034 – Assert resolution on both `main` and `pack`

- **Purpose**: The rule that has already been broken once.

- **Steps**:
  1. **On `main`**: every link resolves against `src/pack/`, where the bootstrap is `start.md`.
  2. **On `pack`**: build the branch tree (WP06's `guide pack build`) and check every link resolves
     there, where the bootstrap is `AGENTS.md`.
  3. Report which branch a failure occurred on. "Link broken" is not actionable; "resolves on `main`,
     404 on `pack`" is.
  4. Wire as `guide links check` for CI.

- **Files**: `src/build/links.py`

- **Parallel?**: No.

- **Notes**: The asymmetry is deliberate, not a bug — `start.md` on one branch, `AGENTS.md` on the other
  (C-004). The checker's job is to prove both are internally consistent, not to make them the same.

### Subtask T035 – Tests, including the historical `README.md` regression

- **Purpose**: Lock in the bug that actually happened.

- **Steps**:
  1. **The regression test**: a `README.md` linking to `AGENTS.md` on `main` must **fail** rule 2. This
     is the real 2026-07-16 bug; it must never come back.
  2. A pathed link fails rule 1.
  3. An inline-code sample is not extracted.
  4. A link to a genuinely missing file fails on the right branch, with the branch named.
  5. The **real current pack passes**, on both branches. If it does not, that is a live finding — report
     it, do not fix `src/pack/`.
  6. Use the temporary pack fixture (WP02 `conftest.py`) for synthetic cases; the live pack for case 5.

- **Files**: `tests/test_links.py`

- **Parallel?**: No.

- **Notes**: Case 5 is the only place in this mission where testing against the live pack is right — it
  is the check's actual job.

## Test Strategy

```bash
poetry run pytest tests/test_links.py
poetry run guide links check     # must pass against the real pack today, on both branches
```

Mandatory: the `README.md`→`AGENTS.md`-on-`main` regression fails; a pathed link fails; inline-code
samples are ignored; the live pack passes on both branches; failures name the branch.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Naive extraction flags the guide's own inline-code examples | T032's exclusion, tested against `quickstart.md` and `CLAUDE.md` |
| Checking only `main`, missing the asymmetry — the original bug | T034 checks both; T035 locks the regression |
| Unactionable errors get ignored, then disabled | Name the file, the line, and the branch; explain why the rule exists |
| The checker "fixes" `src/pack/` | C-002 forbids it; report only |

## Review Guidance

- Does the test suite contain the actual historical bug — `README.md` → `AGENTS.md` failing on `main`?
- Run it against the live pack: green on both branches?
- Add `[x](src/pack/ethics.md)` to a fixture — does it fail with a message explaining *why*?
- Does an inline-code sample trip it? It should not.

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
- 2026-07-16T21:18:04Z – claude:opus:python-pedro:implementer – shell_pid=10042 – Assigned agent via action command
- 2026-07-16T21:24:49Z – claude:opus:python-pedro:implementer – shell_pid=10042 – Ready for review: guide links check enforces all three cross-reference rules on both branches; live pack passes; 2026-07-16 README->AGENTS.md regression locked as a test; guards mutation-demonstrated red
- 2026-07-16T21:25:17Z – claude:opus:reviewer-renata:reviewer – shell_pid=12712 – Started review via action command
- 2026-07-16T21:29:39Z – user – shell_pid=12712 – Review passed: independently reproduced all four claimed mutation guards at the exact counts (strip_code->identity: 8 failed; has_separator->False: 4 failed; drop pack-branch resolution: 1 failed; resolution not distinguishing branch name sets: 2 failed, incl. test_the_2026_07_16_readme_regression). Guard-the-guard verified: extract_links->[] kills test_the_real_pack_has_cross_references_to_check. The inline-code trap holds: all three real files (quickstart.md, CLAUDE.md, doc/build.md) are PRESENT and genuinely PASS (not skipped), and each test asserts the sample is still present before asserting it is not extracted, so it cannot rot silently. 151 passed, black clean, mypy clean (16 files), 'guide links check' green on the live pack both branches. git diff src/pack/ EMPTY vs mission base (C-002/C-006). WP06 consumed not reimplemented: pack_surface() calls build_tree(); SOURCE_NAME/PUBLISHED_NAME imported from rename.py; no duplicated rename logic. Adjudication: I AGREE with rule 1 running on main's bytes only and skipping resolution for pathed links. Verified rather than trusted: rename.py's rewrite is a bare-name start.md->AGENTS.md substitution that cannot introduce a separator, and build_tree writes only pack-derived files, so the pack branch's link set is main's link set -- checking both would report every violation twice. Probed the concealment concern empirically: a pathed link to a nonexistent basename reports rule 1 only, and after the rule-1 fix the resolution defect surfaces on the next run (2 findings). Nothing is hidden from the gate, which still fails; the cost is one extra iteration on a rare compound error, against the certain cost of triple-reporting noise that gets checks disabled. Anti-pattern checklist: 1 dead code PASS (note: LinkError is defined and caught in cli.py but never raised -- vestigial, non-blocking); 2 synthetic-fixture PASS (mutations prove tests drive production paths); 3 silent-empty-return PASS (none in links.py); 4 FR-013 coverage PASS; 5 frozen surface PASS; 6 locked decision PASS; 7 shared-file ownership: cli.py is additive group registration mandated by T034 step 4, coordination noted; 8 fragility PASS (sys.exit(1) is intended fail-loud). ONE NON-BLOCKING FINDING FOR WP08: deleting the final sys.exit(1) from links_check leaves all 151 tests green -- the CLI's fail-the-build path is unguarded. Not blocking because WP08 T036 runs pytest in the same job (test_the_real_pack_passes_on_both_branches fails the build on a real broken link regardless) and WP08 T038 verifies a deliberate lint failure blocks both targets by actually pushing. WP08 should confirm the non-zero exit empirically.
