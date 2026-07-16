---
schema_version: 1
artifact_type: spec-kitty.analysis-report
command: /spec-kitty.analyze
mission_slug: guide-site-build-01KXP76R
mission_id: 01KXP76R20B7GDSGW5VFEK9TFG
generated_at: '2026-07-16T20:18:29.827561+00:00'
analyzer_agent: unknown
input_artifacts:
  spec.md:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/kitty-specs/guide-site-build-01KXP76R/spec.md
    sha256: 10c8b0cecc861d8a2764ff0eb0cc1801ebac3ba646beffe7cba77437caf3c6af
  plan.md:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/kitty-specs/guide-site-build-01KXP76R/plan.md
    sha256: 69310bf0051ac7e90f42851b326a1142154cb85b1a7a802699b0b56d28e56d5e
  tasks.md:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/kitty-specs/guide-site-build-01KXP76R/tasks.md
    sha256: 2cadc5ee839564450ac9b382540e40700937a2d24e965b191b933e7240f0a219
  charter:
    path:
    sha256:
verdict: blocked
issue_counts:
  low: 2
  medium: 6
  critical: 0
  high: 1
  info: 0
findings:
- id: C1
  severity: high
  category: coverage
  summary: NFR-003 (zero hand-authored content; every surface traces to src/pack/) has no verifying task in any work package — it is cited as an aspiration in three WPs but nothing asserts it, and SC-004 depends on it.
- id: C2
  severity: medium
  category: coverage
  summary: FR-013 requires cross-references resolve on every published surface, but WP07 checks only two (main and pack); the site and book renderings are unverified.
- id: C3
  severity: medium
  category: coverage
  summary: NFR-001's base-URL swap test lives only in WP05, so the site's generated URLs (WP03) have no equivalent assertion that a domain change is a one-value edit.
- id: I1
  severity: medium
  category: inconsistency
  summary: plan.md Project Structure omits four modules the tasks create (config.py, rename.py, cli.py, site.py), the src/theme/site vs src/theme/book split, and the spike/ and doc/acceptance/ directories.
- id: I2
  severity: medium
  category: inconsistency
  summary: WP08 T036 instructs deletion of .github/workflows/spike-content-type.yml, which is declared in WP01's owned_files — an undeclared cross-WP ownership edit.
- id: U1
  severity: medium
  category: underspecification
  summary: WP02 T011 defers an unresolved decision to the implementer — whether prose drift fails CI or merely reports — rather than resolving it in planning.
- id: U2
  severity: medium
  category: underspecification
  summary: mkdocs docs_dir points at src/pack, which contains README.md and start.md that are deliberately absent from nav; WP03's own test strategy uses mkdocs build --strict, which typically fails on files not in nav. The interaction with the derived landing page (FR-001) is unspecified.
- id: D1
  severity: low
  category: duplication
  summary: SC-007 and NFR-005 both state the same 5-minute publication threshold; benign, but a change to one can silently diverge from the other.
- id: C4
  severity: low
  category: coverage
  summary: WP01 and WP09 carry requirement_refs (FR-007, FR-008, FR-009) for requirements they prove or verify rather than implement, which inflates apparent coverage; the real implementers are WP03 and WP06.
---

## Specification Analysis Report

**Mission**: `guide-site-build-01KXP76R` · **Analysed**: spec.md, plan.md, tasks.md + 9 WP prompts
**Charter**: absent (`.kittify/charter/charter.md` not found) — no charter principles to validate
against. This is reported as fact, not as a violation.

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Coverage | HIGH | spec.md NFR-003; tasks.md (all WPs) | NFR-003 ("100% of every published surface traces to a source document in the pack; zero hand-written pages") has **no verifying task**. It is cited as an aspiration in WP03/WP04/WP05 prose, but no work package owns a check. SC-004 ("no two surfaces can disagree") is claimed true *by construction* on the strength of NFR-003 — so an unverified NFR-003 leaves SC-004 unevidenced. | Add a provenance check to WP02 (it already owns the lint surface) or WP08's `verify` job: assert every published output file derives from a `src/pack/` document, and fail on any output with no source. One subtask. |
| C2 | Coverage | MEDIUM | spec.md FR-013; tasks/WP07 | FR-013 says "verify, as part of the build, that cross-references resolve on **every published surface**". WP07 checks `main` and `pack` only. The site (WP03) and the book (WP04, which *transforms* references in T018) are not covered. | Either narrow FR-013's wording to the two branches (where the real risk lives), or extend WP07 to assert the book's flattened references and the site's rendered links. Prefer narrowing — the transforms are already tested in WP04 T022. |
| C3 | Coverage | MEDIUM | spec.md NFR-001, SC-006; tasks/WP03, WP05 | The base-URL swap test (rebuild with a different base, assert every address changed) exists only in WP05 T026, covering `llms.txt`/`llms-full.txt`. WP03 generates URLs too — the AI pointer, `rel="alternate"`, the PDF link — with no equivalent assertion. A hard-coded hostname in the site would survive. | Add the swap assertion to WP03's test strategy, or lift it to a shared test that walks all generated output. |
| I1 | Inconsistency | MEDIUM | plan.md § Project Structure vs tasks/WP01–WP09 | plan.md's source tree omits `src/build/config.py`, `rename.py`, `cli.py`, `site.py`; shows `src/theme/` undivided where tasks split it into `site/` and `book/` for ownership; and does not mention `spike/` (WP01) or `doc/acceptance/` (WP09). The last two arrived after plan.md was written — `doc/acceptance/` specifically because finalize-tasks rejected `kitty-specs/` ownership. | Update plan.md's Project Structure to match. Low effort, but it is the map a new implementer reads first. |
| I2 | Inconsistency | MEDIUM | tasks/WP08 T036; tasks/WP01 frontmatter | WP08 T036 instructs "Remove WP01's spike workflow (`spike-content-type.yml`)". That path is in **WP01's** `owned_files`. No glob overlap triggered the finalizer, but it is a cross-WP write. | Either move spike teardown into WP01 T004 (which already handles cleanup) or declare it in WP08 as an intentional out-of-map edit with a rationale. Prefer the former: the WP that created it should remove it. |
| U1 | Underspecification | MEDIUM | tasks/WP02 T011 | The subtask says "Decide with the reviewer whether drift fails CI or merely reports", then recommends an answer. Planning is where that decision belongs; leaving it open means two implementers could resolve it differently, and CI strictness is not an implementation detail. | Resolve it now as a decision moment. The prompt's own recommendation (report on the branch, fail on `main`) is sound — record it rather than delegating it. |
| U2 | Underspecification | MEDIUM | contracts/roles-declaration.md; tasks/WP03 | `docs_dir: src/pack` places `README.md` and `start.md` inside the docs tree while deliberately excluding them from `nav` (they are `not_in_book`). WP03's test strategy runs `mkdocs build --strict`, which conventionally errors on files present but not in nav. Meanwhile FR-001's landing page is *derived* from `creator-kit.md` via a hook, while MkDocs may treat `README.md` as the index. The interaction is unspecified and will surface in WP03's first build. | Specify it: either exclude the two documents from `docs_dir` and publish them via the raw-copy path only, or configure the not-in-nav exclusion explicitly. Decide before WP03 starts, or the implementer will invent an answer. |
| D1 | Duplication | LOW | spec.md NFR-005, SC-007 | Both state the 5-minute publication threshold independently. | Harmless. If one changes, change both — or have SC-007 reference NFR-005 rather than restate it. |
| C4 | Coverage | LOW | tasks/WP01, WP09 frontmatter | WP01 (a spike) claims FR-007/FR-008; WP09 (acceptance) claims FR-008/FR-009. Neither implements those requirements — they prove and verify them. Coverage reads 13/13 partly on the strength of WPs that ship no implementation. | Cosmetic. The real implementers (WP03, WP06) also carry the refs, so coverage is genuine. Worth knowing when reading the matrix. |

### Coverage Summary

**Functional requirements — 13/13 mapped (100%)**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| browsable-site-with-nav (FR-001) | Yes | WP03 T012–T016 | |
| per-page-markdown-pointer (FR-002) | Yes | WP03 T014 | |
| single-file-book (FR-003) | Yes | WP04 T017, T021 | |
| printable-pdf (FR-004) | Yes | WP04 T017–T020; verified WP09 T043 | Print acceptance is human |
| llms-txt-index (FR-005) | Yes | WP05 T023 | |
| llms-full-txt (FR-006) | Yes | WP05 T024 | |
| raw-markdown-as-text (FR-007) | Yes | WP01 T001–T004 (proves); WP03 T015 (implements) | Conditional on url-map C1 |
| bootstrap-at-stable-address (FR-008) | Yes | WP03 T015; verified WP09 T041 | |
| pack-branch-published (FR-009) | Yes | WP06 T027–T030 | |
| bootstrap-renamed-and-refs-rewritten (FR-010) | Yes | WP02 T009; WP06 T028 | Shared logic in WP02 |
| declared-document-roles (FR-011) | Yes | WP02 T006, T010 | |
| continuous-republication (FR-012) | Yes | WP08 T036–T040 | |
| cross-references-resolve (FR-013) | Partial | WP07 T032–T035 | **C2** — 2 of 4 surfaces |

**Non-functional requirements — 5/6 verified (83%)**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| relocatable-address (NFR-001) | Partial | WP05 T025–T026 | **C3** — site URLs unasserted |
| readable-at-320px (NFR-002) | Yes | WP03 T016 | |
| nothing-hand-authored (NFR-003) | **No** | — | **C1 — zero coverage** |
| bounded-visual-investment (NFR-004) | Yes | WP03 T012 | Review-judged, not automated |
| publication-latency-5min (NFR-005) | Yes | WP08 T039–T040 | |
| wcag-aa-contrast (NFR-006) | Yes | WP03 T016 | |

**Constraints — 6/6 addressed**: C-001 (WP07 T033), C-002 (WP02 T011 + every prompt's "never write to
`src/pack/`"), C-003 (WP03 T016, WP05 T025), C-004 (WP02 T009, WP06 T028), C-005 (WP06 T029), C-006
(prompt-level prohibition throughout).

### Charter Alignment Issues

None assessable — no charter exists. The two built-in directives applied during planning
(DIRECTIVE_003 decision documentation, DIRECTIVE_010 spec fidelity) both hold: the PDF toolchain fork is
recorded as decision `01KXP7BCG6XFDHDRGZ57NXG90Q`, and every WP cites the requirements it serves.

**Note**: U1 is a mild DIRECTIVE_003 tension — an undecided decision was pushed into implementation
rather than documented in planning. Not a violation (no charter), but the same instinct applies.

### Unmapped Tasks

None. All 44 subtasks roll up to a work package, and all 9 work packages carry `requirement_refs`.
See C4 for a caveat about *what kind* of coverage two of those refs represent.

### Metrics

- **Total requirements**: 25 (13 functional, 6 non-functional, 6 constraints)
- **Total work packages**: 9 · **Total subtasks**: 44
- **Functional coverage**: 13/13 (100%)
- **Non-functional coverage**: 5/6 (83%) — NFR-003 uncovered
- **Overall FR+NFR coverage**: 18/19 (94.7%)
- **Ambiguity count**: 2 (U1, U2)
- **Duplication count**: 1 (D1)
- **Critical issues**: 0
- **High issues**: 1 (C1)

### Assessment

The artifacts are internally coherent and the traceability is real: every functional requirement reaches
a task, no task is orphaned, ownership does not overlap, and dependencies form a clean DAG with no
cycles. The prompts carry project-specific history (the `getting-started.md` rename trap, the
`README.md`/`AGENTS.md` branch asymmetry, the live `5g_arg` consumer) rather than generic guidance.

The one finding that should be fixed before implementation is **C1**. It matters more than its size
suggests: NFR-003 is the mechanism by which SC-004 ("no two surfaces can disagree") is claimed to be true
*by construction*. If nothing verifies NFR-003, then the mission's central architectural claim — one
source, four surfaces, no drift — rests on convention rather than enforcement. That is precisely the
failure this project already knows it is prone to: the reading order drifted across four prose copies,
and a hand-written link broke across two branches. Both were caught by chance. C1 is the same class of
problem, and it is a one-subtask fix.

The remaining findings are cheap to resolve and none blocks a start on WP01, which owns no affected
surface.

### Next Actions

1. **Resolve C1 before `/spec-kitty.implement`.** Add a provenance check to WP02 (owns the lint surface)
   or WP08's `verify` job. One subtask; no re-planning needed.
2. **Resolve U2 before WP03 starts.** The `docs_dir`/`nav`/`--strict` interaction will block WP03's first
   build otherwise, and the implementer will invent an answer that may not match the contract.
3. **Resolve U1 now.** Record the CI-strictness decision rather than delegating it to a reviewer.
4. **Fix I1 and I2 opportunistically** — plan.md's structure and the spike-teardown ownership. Neither
   blocks work.
5. **C2, C3, D1, C4** — accept or address at leisure; none affects execution order.
6. **WP01 can start immediately.** It touches none of the affected surfaces, and its finding may itself
   amend the URL map that C2/C3 concern.

Suggested commands: manually edit `tasks.md` and the relevant WP prompt to add the NFR-003 provenance
subtask (C1); manually amend `contracts/roles-declaration.md` or WP03's prompt for U2; edit
`kitty-specs/guide-site-build-01KXP76R/plan.md` § Project Structure for I1.
