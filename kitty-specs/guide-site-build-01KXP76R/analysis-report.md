---
schema_version: 1
artifact_type: spec-kitty.analysis-report
command: /spec-kitty.analyze
mission_slug: guide-site-build-01KXP76R
mission_id: 01KXP76R20B7GDSGW5VFEK9TFG
generated_at: '2026-07-16T23:29:15.132454+00:00'
analyzer_agent: unknown
input_artifacts:
  spec.md:
    path: /Users/salimfadhley/workspace/dungeon-masters-guide/kitty-specs/guide-site-build-01KXP76R/spec.md
    sha256: af3583531c034ac47aefc12a258ab7f10e5e943ccc882bd6b7a6664c141f8d32
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
  high: 0
  critical: 0
  low: 3
  medium: 1
  info: 0
findings:
- id: G1
  severity: medium
  category: coverage
  summary: "WP06's reproduction gate compares live src/pack/ against d024682, so it asserts the guide's content never changes rather than that the automation reproduces the hand-built branch. Proven: making the stakeholder's premise.md edit reds test_generated_tree_reproduces_the_hand_built_branch. It will block the first automated run carrying real content."
- id: D1
  severity: low
  category: duplication
  summary: SC-007 and NFR-005 both state the same 5-minute publication threshold.
- id: C4
  severity: low
  category: coverage
  summary: WP01 and WP09 carry requirement_refs for requirements they prove or verify rather than implement.
- id: CH1
  severity: low
  category: charter-alignment
  summary: The charter's stock 'CLI operations under 2 seconds' default versus a build that takes longer by design. A hedged SHOULD scoped to product CLIs; this project ships none.
---

## Specification Analysis Report (re-run 5 — post-descope, all lanes merged)

**Mission**: `guide-site-build-01KXP76R`
**Trigger**: `stale_analysis_report` after the stakeholder descoped FR-003/FR-004/SC-003.
**Status**: WP01–WP07 **approved** (7/9). All lanes merged onto `feat/guide-site-build`. The site is
**live** at `https://conspiracy-larp.github.io/dungeon-masters-guide/` via a hand deploy.

### Scope change

**FR-003, FR-004 and SC-003 descoped** by the stakeholder: the website and the LLM-readable markdown are
the deliverables; nobody reads the book. Beyond preference, this removes the only reason CI needs a
1.1GB pandoc/TeX image — WP04 measured ~58s cold against ~6s to render — taking the main risk out of
NFR-005. WP04's code is complete, reviewed and approved; it stays in the repo and leaves the pipeline.

Functional coverage is now **11/11** of the in-scope FRs.

### The one finding that matters

**G1 — WP06's reproduction gate blocks content changes.** Not predicted; proven. `guide book`-independent:
`test_generated_tree_reproduces_the_hand_built_branch` compares the tree generated from **live**
`src/pack/` against `d024682`. Making the stakeholder's own `premise.md` edit turns it red with
`Difference(published_name='creator-kit.md', kind='content')`.

C-005 asked for a one-time proof *before* the automation takes over, and WP06's own prompt said to
compare against `d024682`'s **inputs** — regenerate from that commit's `src/pack/`. The implementer took
the simpler path: correct today, blocking tomorrow. **WP08 cannot go green while it stands**, because the
first automated run carries `premise.md`, the rewritten bootstrap and nine new abstracts.

This is the mission's signature defect inverted: not a check with no teeth, but a check biting the wrong
thing.

### Coverage

**Functional: 11/11 in scope** (FR-003/FR-004 descoped). **Non-functional: 6/6.** **Constraints: 6/6.**

FR-013 now genuinely covers every remaining surface — and was exercised for real during the lane merge:
`guide links check` passed on both `main` and the pack branch against the new content.

### Charter Alignment

No MUST violated. CH1 is the only tension and is now *less* relevant: with the PDF descoped, the slowest
command is gone.

### Metrics

- Requirements: 23 in scope (11 FR, 6 NFR, 6 C) · WPs: 9 · Subtasks: 45
- Coverage: 17/17 FR+NFR in scope (100%)
- Critical 0 · High 0 · Medium 1 · Low 3

### Assessment

Seven of nine approved, every lane merged onto one branch, and all three gates green together for the
first time — including WP07's link checker, which the hand deploy could not run.

The hand deploy proved the pipeline's shape works but left two gaps only automation closes: it runs
without the link gate, and it never mirrors the `pack` branch, so `5g_arg`'s submodule still tracks the
hand-built `d024682` and has received none of the new content.

**G1 is the gate on the gate.** Fix it inside WP08, or WP08 ships a pipeline that reds on the content it
is meant to publish.

### Next Actions

1. **WP08** — merge-to-main deploy, link gate restored, pack-branch mirror, no TeX. **Fix G1 first.**
2. **WP09** — behavioural acceptance. SC-003 (print it) is descoped; SC-001 (cold bootstrap against a
   real model) is now the whole test, and it is the one that matters.
3. D1, C4, CH1 — accept.
