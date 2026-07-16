---
schema_version: 1
artifact_type: spec-kitty.analysis-report
command: /spec-kitty.analyze
mission_slug: guide-site-build-01KXP76R
mission_id: 01KXP76R20B7GDSGW5VFEK9TFG
generated_at: '2026-07-16T21:06:34.496339+00:00'
analyzer_agent: unknown
input_artifacts:
  spec.md:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/kitty-specs/guide-site-build-01KXP76R/spec.md
    sha256: 10c8b0cecc861d8a2764ff0eb0cc1801ebac3ba646beffe7cba77437caf3c6af
  plan.md:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/kitty-specs/guide-site-build-01KXP76R/plan.md
    sha256: 3097385842951484f651d4fd91edce07980aa3436b52fb7c7543c2458b6958a3
  tasks.md:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/kitty-specs/guide-site-build-01KXP76R/tasks.md
    sha256: af66c742d204f894444f28419309e8eff43ea24c68c55729e8e57e30002a70cd
  charter:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/.kittify/charter/charter.md
    sha256: fef944ebc79e9ee2ed69a8dfafe87322aaa74f5c5ed98d84e9528f86c538edde
verdict: ready
issue_counts:
  medium: 0
  critical: 0
  high: 0
  low: 3
  info: 0
findings:
- id: D1
  severity: low
  category: duplication
  summary: SC-007 and NFR-005 both state the same 5-minute publication threshold; benign, but a change to one can silently diverge from the other.
- id: C4
  severity: low
  category: coverage
  summary: WP01 and WP09 carry requirement_refs for requirements they prove or verify rather than implement, which inflates apparent coverage; the real implementers are WP03 and WP06.
- id: CH1
  severity: low
  category: charter-alignment
  summary: The default-generated charter sets 'CLI operations should complete quickly (typically under 2 seconds)', which the guide book pdf build exceeds by design; NFR-005 budgets 5 minutes. A hedged SHOULD scoped to product CLIs, and this project ships none.
---

## Specification Analysis Report (re-run 4 — mid-implementation, WP01+WP02 approved)

**Mission**: `guide-site-build-01KXP76R`
**Trigger**: `stale_analysis_report` (stale input: `plan.md`) after a precision correction to the
`extra_css` hazard, raised at WP02's review.
**Supersedes**: run 1 (`blocked`, 1 high / 6 medium / 2 low), run 2 (`ready`, 4 medium / 2 low),
run 3 (`ready`, 3 low).
**Status**: WP01 **approved**, WP02 **approved** (cycle 1). WP03–WP06 ready to dispatch in parallel.
**Charter**: present. Re-evaluated; no MUST violated.

### Resolved since run 2

| ID | Was | Resolution |
|----|-----|-----------|
| C2 | MEDIUM — FR-013 claims "every published surface"; WP07 checks only `main` and `pack` | **Gap closed rather than requirement narrowed.** WP03 now enables MkDocs link validation so `--strict` fails on broken internal links (the site); WP04 T022 already covers the book. WP07's prompt states its two-branch scope is deliberate, with a table of which WP covers which surface. FR-013 is now literally true. |
| C3 | MEDIUM — base-URL swap asserted only for `llms.txt` (WP05) | WP03 T016 now asserts it for the site's generated addresses (AI pointer, `rel="alternate"`, PDF link). A hard-coded hostname would previously have survived there while the machine files looked clean. |
| I1 | MEDIUM — plan.md's Project Structure was fiction | Grounded in what WP01/WP02 actually built: five previously-omitted modules, the `src/theme/` site↔book split, `spike/`, `doc/acceptance/`, and the `guide` command surface WP03–WP08 call. Also carries the two build-time traps WP02 discovered. |
| I2 | MEDIUM — WP08 deleted a file in WP01's `owned_files` | WP01 removed the spike at teardown and review confirmed its absence across every ref. T036 now verifies rather than deletes, and says to stop and ask if it reappeared. |
| — | plan.md's Charter Check said "no charter exists" | Self-inflicted staleness: true when written, false once a charter was created to satisfy the implement gate. Re-evaluated statement by statement; no MUST violated. |

### Remaining findings — all low, all accepted

| ID | Category | Severity | Summary | Recommendation |
|----|----------|----------|---------|----------------|
| D1 | Duplication | LOW | SC-007 restates NFR-005's 5-minute threshold | Have SC-007 reference NFR-005 |
| C4 | Coverage | LOW | WP01/WP09 refs cover requirements they prove, not implement | Cosmetic; real implementers also carry the refs |
| CH1 | Charter alignment | LOW | Charter's stock 2-second CLI target vs a PDF build that takes minutes | Amend the charter if it keeps surfacing across missions |

### Coverage Summary

**Functional: 13/13 (100%). Non-functional: 6/6 (100%). Constraints: 6/6.**

FR-013 now genuinely covers all four published surfaces (was: two of four).
NFR-001 now asserted on both the site and the machine files (was: machine files only).
NFR-003 has an owner, a command, and a CI gate (was: uncovered — run 1's blocking finding).

### Charter Alignment Issues

No MUST violated. `Must run on macOS and Linux developer environments` — passes (Python plus a
containerised pandoc/TeX). The single SHOULD tension is CH1. DIR-001 ("keep spec, plan, tasks,
implementation and review artifacts consistent", severity `warn`) is the reason this re-run exists: the
artifacts were corrected against evidence rather than left describing a world the build had disproved.

### Unmapped Tasks

None. 45 subtasks across 9 work packages.

### Metrics

- **Total requirements**: 25 (13 FR, 6 NFR, 6 C)
- **Work packages**: 9 · **Subtasks**: 45
- **Overall FR+NFR coverage**: 19/19 (100%)
- **Ambiguity count**: 0 · **Duplication count**: 1
- **Charter conflicts**: 0 MUST, 1 SHOULD tension
- **Critical**: 0 · **High**: 0 · **Medium**: 0 · **Low**: 3

### Assessment

Implementation is under way and is doing what it was designed to do: **test the plan rather than trust
it.** Three planning assumptions have been disproved by execution so far, each cheaply:

1. **The research's fallback ordering was wrong** — WP01 measured extensionless twins as
   `application/octet-stream`, worse than the problem they would solve. The plan had ranked them second.
2. **The `--strict` rationale was wrong** — `validation.nav.omitted_files` defaults to `info` and
   `--strict` escalates only `WARNING`, so FR-011 had no teeth in the build at all. One config key fixed it.
3. **The `extra_css` instruction would have violated C-002/C-006** — it resolves relative to `docs_dir`,
   which is `src/pack/`, so the build would have written assets into the product. **Corrected twice**:
   the first correction overstated it as a loud failure. It is not — a missing `extra_css` file exits 0
   and ships a *silent 404*, and the role lint globs `*.md` only, so a stray `.css` is invisible to it.
   The accurate version is the stronger argument: the hazard is not a failure you would notice.

A fourth was caught at review: `black --check .` was vacuous, because black's `DEFAULT_EXCLUDES` contains
`build` and silently skipped `src/build/` — 5 files checked of 11, while the skipped ones violated black.
That gate would have passed forever while checking nothing, in CI, for four inheriting lanes.

All four are the same shape: **a check that looks like a check but has no teeth.** That this mission keeps
surfacing them is the strongest evidence that its verification-first structure is earning its cost.

The artifacts and the implementation now agree. Nothing blocks.

### Next Actions

1. **Proceed.** WP01 and WP02 are approved. Dispatch the four-lane round — WP03, WP04, WP05, WP06 —
   which is the widest point of the sprint. WP07 follows WP06; WP08 gathers; WP09 closes.
2. **D1, C4, CH1** — accept.
