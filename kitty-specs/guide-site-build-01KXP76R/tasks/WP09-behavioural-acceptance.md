---
work_package_id: WP09
title: Behavioural acceptance
dependencies:
- WP08
requirement_refs:
- FR-008
- FR-009
tracker_refs: []
subtasks:
- T041
- T042
- T043
- T044
phase: Phase 3 - Publication and acceptance
assignee: ''
agent: claude
history:
- at: '2026-07-16T19:58:13Z'
  actor: system
  action: Prompt generated via /spec-kitty.tasks
agent_profile: human-in-charge
authoritative_surface: kitty-specs/guide-site-build-01KXP76R/acceptance/
create_intent:
- kitty-specs/guide-site-build-01KXP76R/acceptance/sc-001-cold-bootstrap.md
- kitty-specs/guide-site-build-01KXP76R/acceptance/sc-002-submodule.md
- kitty-specs/guide-site-build-01KXP76R/acceptance/sc-003-printed-book.md
- kitty-specs/guide-site-build-01KXP76R/acceptance/summary.md
execution_mode: planning_artifact
model: ''
owned_files:
- kitty-specs/guide-site-build-01KXP76R/acceptance/**
role: reviewer
tags: []
task_type: review
---

# Work Package Prompt: WP09 – Behavioural acceptance

## ⚡ Do This First: Load Agent Profile

Use the `/ad-hoc-profile-load` skill to load the agent profile specified in the frontmatter (or any
user-defined profile), and behave according to its guidance before parsing the rest of this prompt.

- **Profile**: `human-in-charge`
- **Role**: `reviewer`
- **Agent/tool**: `claude`

If no profile is specified, run `spec-kitty agent profile list` and select the best match for this work
package's `task_type` and `authoritative_surface`.

**This profile is deliberate.** T043 requires a printer and a person. An agent cannot close this work
package alone, and should not pretend to.

---

## Markdown Formatting

Wrap HTML/XML tags in backticks: `` `<div>` ``, `` `<script>` ``
Use language identifiers in code blocks: ` ```python `, ` ```bash `

---

## Objectives & Success Criteria

Answer the only questions that decide whether this mission succeeded — none of which a green CI run can
answer.

- **SC-001**: a fresh LLM, given nothing but the one URL, produces a correct workspace with the kit at
  `doc/core/`, and asks about the creator's real-identity boundaries **before writing anything**.
- **SC-002**: the published submodule command runs clean from a bare checkout.
- **SC-003**: the PDF is readable printed on paper.

This work package *is* the test. It produces evidence and a verdict, not code.

## Context & Constraints

Read `spec.md` § Success Criteria and § Why this exists before starting.

**Why these are the tests that matter.** Every other WP can pass while the mission fails. The site can
render, the lints can be green, the branch can publish — and a creator can still hand their LLM the URL
and get nothing useful. The whole point of the guide is that a person with an idea and a model can start
building. That is not a structural property; it is a behavioural one, and the only way to know is to try
it.

**The ordering in SC-001 is the point, not a detail.** The guide's central ethical commitment is that a
creator's real identity is firewalled *out* of the fiction, and that this is established **first**, before
a single artifact exists (`getting-started.md`, Move 1; `ethics.md`). A model that scaffolds a perfect
workspace and *then* asks about identity boundaries **has failed this test** — because by then it has
already written things. Test the order, not just the presence.

**Constraints**:

- Do not fix what you find. Report it. Fixes belong to the WP that owns the surface.
- Do not coach the model in T041. The test is a cold start; hints invalidate it.

## Branch Strategy

- **Strategy**: feature-branch, PR-bound
- **Planning base branch**: `feat/guide-site-build`
- **Merge target branch**: `feat/guide-site-build`
- Execution worktrees are allocated per computed lane from `lanes.json`.

> These fields are populated automatically by `spec-kitty agent mission tasks`.
> Do NOT change them manually unless you are certain the branch topology has changed.

## Subtasks & Detailed Guidance

### Subtask T041 – SC-001: cold bootstrap against a real LLM, verifying *order*

- **Purpose**: The mission's reason for existing.

- **Steps**:
  1. Open a **fresh** session with a real model. No project context, no repo checked out, nothing in
     the context window about this guide.
  2. Give it exactly one instruction, and nothing else:
     > read `https://conspiracy-larp.github.io/dungeon-masters-guide/AGENTS.md` and do what it says
  3. Do not help. Do not clarify. Answer its questions as a naive creator would.
  4. Record the whole transcript.
  5. Assess against the primary scenario in `spec.md`:
     - [ ] Did it fetch and act on the bootstrap without needing more context?
     - [ ] Did it create a correct workspace — `doc/lore/`, `sites/`, `build/`?
     - [ ] Did it attach the kit at `doc/core/`, tracking the `pack` branch?
     - [ ] **Did it ask about real-identity boundaries BEFORE writing any artifact?** ← the one that
           matters
     - [ ] Did it then map the creator's corner and start generating build prompts?
  6. Repeat with a **second, different model** if available. One model's success may be that model's
     good judgement rather than the bootstrap's clarity.

- **Files**: `kitty-specs/guide-site-build-01KXP76R/acceptance/sc-001-cold-bootstrap.md`

- **Parallel?**: No.

- **Notes**: If it fails, the finding is about the *bootstrap's text* — and that text is `src/pack/`
  content, which is **out of scope for this mission** (C-006). Report it as a content finding for a
  follow-up mission. Do not edit the pack to make your test pass.

### Subtask T042 – SC-002: the published submodule command, from a bare checkout

- **Purpose**: The guide has been telling readers to run this since 2026-07-16. Prove it is still true.

- **Steps**:
  1. In a clean temporary directory:
     ```bash
     mkdir -p my-node/doc/lore my-node/sites my-node/build && cd my-node && git init
     git submodule add -b pack git@github.com:Conspiracy-LARP/dungeon-masters-guide.git doc/core
     ```
  2. Assert, exactly as `start.md` promises:
     ```bash
     ls doc/core/AGENTS.md doc/core/creator-kit.md doc/core/getting-started.md
     test ! -e doc/core/src && test ! -e doc/core/doc
     ```
  3. Then the currency check: `git submodule update --remote doc/core` — it must pull cleanly, not break
     the checkout.
  4. Compare against the commands as actually published in `src/pack/start.md`,
     `src/pack/README.md`, and `src/pack/technical-suggestions.md`. **Run what the guide says**, not what
     you think it means.

- **Files**: `kitty-specs/guide-site-build-01KXP76R/acceptance/sc-002-submodule.md`

- **Parallel?**: **[P]**

- **Notes**: `5g_arg`'s `doc/core` already tracks this branch. If this test fails, a real project is
  already broken — escalate immediately rather than filing it.

### Subtask T043 – SC-003: print the PDF and read it on paper

- **Purpose**: This output exists for people who print. A preview proves nothing about paper.

- **Steps**:
  1. **Print it.** On paper. A4 or Letter.
  2. Check:
     - [ ] Title page present and not embarrassing
     - [ ] Table of contents with page numbers that are *correct*
     - [ ] Pagination real — no orphaned headings, no absurd page breaks mid-table
     - [ ] Body text comfortable at arm's length
     - [ ] **No instruction assuming a click** — search the printed text for "see `ethics.md`" and its
           kin (FR-004)
     - [ ] Wide tables (the tells comparison in `storytelling.md`) fit the page
     - [ ] Emoji rendered or sensibly substituted, not tofu boxes
  3. Read a chapter. Not skim — read it. Is it a book, or a printed website?

- **Files**: `kitty-specs/guide-site-build-01KXP76R/acceptance/sc-003-printed-book.md`

- **Parallel?**: **[P]**

- **Notes**: Requires a human with a printer. This is why the profile is `human-in-charge`. An agent
  must not mark this passed from a PDF preview.

### Subtask T044 – Record results; close the mission or escalate

- **Purpose**: A verdict, honestly stated.

- **Steps**:
  1. Write `acceptance/summary.md`: each SC, pass or fail, with a link to its evidence.
  2. For each failure, name the WP that owns the surface, or flag it as a **content** finding (out of
     scope, needs a follow-up mission).
  3. Do not soften a failure to close the mission. A mission that ships a beautiful site whose bootstrap
     does not work has failed, and saying so is the whole value of this WP.
  4. If all three pass, say so plainly and recommend closure.

- **Files**: `kitty-specs/guide-site-build-01KXP76R/acceptance/summary.md`

- **Parallel?**: No.

- **Notes**: SC-001 is not negotiable. The other two are recoverable; a broken bootstrap means the
  project's front door does not open.

## Test Strategy

This work package is the test strategy. Evidence is transcripts, terminal output, and a printed
document — recorded, not summarised.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| The tester coaches the model, invalidating the cold start | T041: one instruction, no help, transcript recorded |
| One model's success mistaken for the bootstrap being clear | Repeat with a second model |
| SC-001 marked pass because the workspace looked right, ignoring order | The checklist makes ordering an explicit gate |
| SC-003 "passed" from a preview | `human-in-charge` profile; print it |
| A failure gets fixed by editing `src/pack/` to suit the test | Content is out of scope (C-006); report as a finding |
| A real consumer is already broken (SC-002) | Escalate immediately, do not queue |

## Review Guidance

- Is there an actual transcript for SC-001, from a genuinely cold session?
- Does it show the identity question arriving **before** any file was written?
- Was SC-002 run as the guide publishes it, or as the tester remembers it?
- Was the PDF printed, or previewed?
- Are failures reported plainly, with the owning WP named?

## Activity Log

- 2026-07-16T19:58:13Z – system – Prompt created.
