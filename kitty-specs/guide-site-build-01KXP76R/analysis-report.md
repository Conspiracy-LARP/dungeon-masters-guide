---
schema_version: 1
artifact_type: spec-kitty.analysis-report
command: /spec-kitty.analyze
mission_slug: guide-site-build-01KXP76R
mission_id: 01KXP76R20B7GDSGW5VFEK9TFG
generated_at: '2026-07-16T20:29:55.703773+00:00'
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
    sha256: af66c742d204f894444f28419309e8eff43ea24c68c55729e8e57e30002a70cd
  charter:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/.kittify/charter/charter.md
    sha256: fef944ebc79e9ee2ed69a8dfafe87322aaa74f5c5ed98d84e9528f86c538edde
verdict: ready
issue_counts:
  medium: 4
  low: 3
  high: 0
  critical: 0
  info: 0
findings:
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
  summary: plan.md Project Structure omits five modules the tasks create (config.py, rename.py, cli.py, site.py, provenance.py), the src/theme/site vs src/theme/book split, and the spike/ and doc/acceptance/ directories.
- id: I2
  severity: medium
  category: inconsistency
  summary: WP08 T036 instructs deletion of .github/workflows/spike-content-type.yml, which is declared in WP01's owned_files — an undeclared cross-WP ownership edit.
- id: D1
  severity: low
  category: duplication
  summary: SC-007 and NFR-005 both state the same 5-minute publication threshold; benign, but a change to one can silently diverge from the other.
- id: C4
  severity: low
  category: coverage
  summary: WP01 and WP09 carry requirement_refs (FR-007, FR-008, FR-009) for requirements they prove or verify rather than implement, which inflates apparent coverage; the real implementers are WP03 and WP06.
- id: CH1
  severity: low
  category: charter-alignment
  summary: The default-generated charter sets a performance target of 'CLI operations should complete quickly (typically under 2 seconds)', which the guide book pdf build exceeds by design; NFR-005 budgets 5 minutes end-to-end. A hedged SHOULD, not a MUST, and it plausibly scopes to product CLIs rather than build pipelines - but it is a default nobody chose.
---

## Specification Analysis Report (re-run after remediation)

**Mission**: `guide-site-build-01KXP76R` · **Analysed**: spec.md, plan.md, tasks.md + 9 WP prompts
**Supersedes**: the first run (verdict `blocked`, 9 findings: 1 high, 6 medium, 2 low)
**Charter**: **now present** — created during this session via `charter interview --defaults --profile
minimal` + `generate` + `sync`, because `agent action implement` refuses to run without one
(`charter_source missing`). This is the first run in which Charter Alignment is assessable.

### Resolved since the previous run

| ID | Was | Resolution | Evidence |
|----|-----|-----------|----------|
| C1 | HIGH — NFR-003 (zero hand-authored content) had no verifying task, leaving SC-004's "true by construction" claim unenforced | WP02 gains subtask **T045**: `guide verify provenance` asserts every published file derives from a `src/pack/` document or an explicit allow-list; a file matching neither fails the build. WP08's `verify` gate runs it after the build. | `tasks/WP02` T045; `tasks/WP08` T036; commit `27e52b1` |
| U1 | MEDIUM — WP02 T011 deferred the CI-strictness decision to the implementer | Decided in planning: drift **warns** on feature branches, **fails** on `main`, with the rationale recorded. The prompt now tells the implementer not to re-litigate it. | `tasks/WP02` T011 |
| U2 | MEDIUM — `docs_dir: src/pack` puts `README.md`/`start.md` in the docs tree while absent from `nav`; `mkdocs build --strict` fails on that, and the interaction with the derived landing page was unspecified | Declared MkDocs' `not_in_nav` key listing exactly the `not_in_book` set — suppresses the intentional-omission warning **without** weakening `--strict` for genuinely undeclared documents (which FR-011 still requires to fail). Landing page explicitly derived; `README.md` explicitly not the index. Role lint now asserts `not_in_nav` and `not_in_book` agree. | `contracts/roles-declaration.md` § "The `--strict` interaction"; `tasks/WP02` T006, T010; `tasks/WP03` |

Additionally, dependency **D-002** (GitHub Pages enabled, publishable from Actions) is now **satisfied**:
Pages is live at `https://conspiracy-larp.github.io/dungeon-masters-guide/` with `build_type: workflow`,
matching the address `contracts/url-map.md` already assumed. WP01 is no longer blocked on a prerequisite
outside the code.

### Remaining findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C2 | Coverage | MEDIUM | spec.md FR-013; tasks/WP07 | FR-013 says "every published surface"; WP07 checks `main` and `pack` only. Site and book renderings unverified. | Narrow FR-013's wording to the two branches (where the risk lives), or extend WP07. The book's transforms are already tested in WP04 T022. |
| C3 | Coverage | MEDIUM | spec.md NFR-001, SC-006; tasks/WP03, WP05 | The base-URL swap assertion exists only in WP05 T026. WP03 also generates URLs with no equivalent test. | Add the swap assertion to WP03, or lift it to a shared test walking all generated output. |
| I1 | Inconsistency | MEDIUM | plan.md § Project Structure | Omits `config.py`, `rename.py`, `cli.py`, `site.py`, `provenance.py`, the `src/theme/` split, `spike/`, `doc/acceptance/`. | Update plan.md's tree. It is the map a new implementer reads first. |
| I2 | Inconsistency | MEDIUM | tasks/WP08 T036; tasks/WP01 | WP08 deletes a file in WP01's `owned_files`. | Move spike teardown into WP01 T004, which already handles cleanup. |
| D1 | Duplication | LOW | spec.md NFR-005, SC-007 | Same 5-minute threshold stated twice. | Harmless; have SC-007 reference NFR-005. |
| C4 | Coverage | LOW | tasks/WP01, WP09 | Spike and acceptance WPs carry refs for requirements they prove rather than implement. | Cosmetic; real implementers also carry the refs. |

### Coverage Summary

**Functional: 13/13 (100%)** — unchanged.

**Non-functional: 6/6 (100%)** — was 5/6.

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| relocatable-address (NFR-001) | Partial | WP05 T025–T026 | C3 — site URLs unasserted |
| readable-at-320px (NFR-002) | Yes | WP03 T016 | |
| nothing-hand-authored (NFR-003) | **Yes** | **WP02 T045; WP08 T036** | **Resolved (was C1)** |
| bounded-visual-investment (NFR-004) | Yes | WP03 T012 | Review-judged |
| publication-latency-5min (NFR-005) | Yes | WP08 T039–T040 | |
| wcag-aa-contrast (NFR-006) | Yes | WP03 T016 | |

**Constraints: 6/6 addressed.**

### Charter Alignment Issues

The charter is deliberately non-committal — it defers to "the project's declared" test approach, quality
gates, and tooling rather than imposing its own. Checked statement by statement:

| Charter statement | Force | Assessment |
|---|---|---|
| "Use the project's declared test approach; if none declared, mark NEEDS CLARIFICATION" | SHOULD | **Pass** — plan.md declares pytest + lints + two behavioural tests |
| "Only require the quality gates explicitly declared by this project before merge" | SHOULD | **Pass** — gates are the declared lints and tests |
| "Use only the languages, frameworks, and tools explicitly declared by this project" | SHOULD | **Pass** — Python 3.12, MkDocs+Material, pandoc/XeLaTeX, all declared in Technical Context |
| "At least one focused reviewer approves before merge" | SHOULD | **Pass** — the implement-review loop enforces it |
| "Must run on macOS and Linux developer environments" | **MUST** | **Pass** — Python + containerised pandoc/TeX; no platform-specific code |
| "CLI operations should complete quickly (typically under 2 seconds)" | SHOULD | **CH1 (low)** — `guide book pdf` exceeds this by design; NFR-005 budgets 5 minutes |
| DIR-001 "Keep spec, plan, tasks, implementation, review artifacts consistent" (severity: warn) | warn | **Pass** — this analysis is that check; I1/I2 are the open drift |

**No MUST principle is violated**, so there is no CRITICAL charter finding.

**CH1 in context**: the 2-second target is a stock default from the `software-dev-default` template set,
not a considered decision about this project. It reads as scoped to product CLI operations; this project
ships no CLI to users — `guide` is build machinery, and its slowest command renders a book with LaTeX.
Recorded as LOW rather than silently ignored, because the charter now binds future missions too. If it
grates, amend the charter (its own Amendment Process: proposed by PR, reviewed before adoption) rather
than let a default nobody chose sit as governance.

DIRECTIVE_003 (decision documentation) is now better served than in the first run: U1's resolution is
recorded with its rationale rather than delegated to implementation.

### Unmapped Tasks

None. 45 subtasks across 9 work packages; all mapped.

### Metrics

- **Total requirements**: 25 (13 FR, 6 NFR, 6 C)
- **Total work packages**: 9 · **Total subtasks**: 45 (was 44; T045 added)
- **Functional coverage**: 13/13 (100%)
- **Non-functional coverage**: 6/6 (100%)
- **Overall FR+NFR coverage**: 19/19 (100%)
- **Ambiguity count**: 0 (was 2)
- **Duplication count**: 1
- **Charter conflicts**: 0 MUST, 1 SHOULD tension (CH1)
- **Critical issues**: 0 · **High issues**: 0 (was 1)

### Assessment

The blocking finding is resolved, and resolved where it belongs: NFR-003 now has an owner, a command, and
a CI gate, so SC-004's "no two surfaces can disagree" rests on enforcement rather than convention. The two
mediums that would have cost real time — an implementer inventing the CI-strictness rule, and WP03's first
build failing on a `--strict`/`nav` conflict nobody had specified — are decided in planning.

The four remaining mediums are documentation and scoping tidiness. None blocks a start, none affects
execution order, and none can silently corrupt an output.

### Next Actions

1. **Proceed to implementation.** WP01 and WP02 are both dependency-free and now unblocked (D-002
   satisfied). Dispatch them in parallel — the round the lanes were computed for.
2. **I1 and I2** — fix opportunistically; neither blocks work.
3. **C2 and C3** — decide during WP07/WP03 review; both are one-line scoping calls.
4. **D1, C4, CH1** — accept, or amend the charter's stock 2-second performance default if it will keep
   surfacing across future missions.
