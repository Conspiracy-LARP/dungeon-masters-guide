# Tasks: Guide Site, Book, and LLM Bootstrap

**Mission**: `guide-site-build-01KXP76R`
**Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md)
**Branch**: planning base `feat/guide-site-build` · work packages merge into `feat/guide-site-build`
**Generated**: 2026-07-16T19:58:13Z

---

## Orientation for implementers

`src/pack/` holds twelve markdown files. That is the product. Every work package below generates
something *from* it. **No work package edits it** — content is out of scope (C-006) and the build is
forbidden from touching prose (C-002). If a WP appears to need a prose change, that is a finding to
escalate, not a fix to make.

Read [quickstart.md](quickstart.md) before your first WP. It is short and it covers the three traps.

**The mission's real objective is behavioural**: a creator hands any LLM one URL and it scaffolds their
workspace and opens the interview, asking about identity boundaries *first*. WP09 is the only thing that
proves it. A green CI run does not.

## Subtask Index

*Reference table only. Progress is tracked by the checkboxes under each work package.*

| ID | Description | WP | Parallel |
|---|---|---|---|
| T001 | Stand up a throwaway Pages deployment with `.nojekyll` and probe files | WP01 | |
| T002 | Record the actual HTTP response for `.md`, and for `.txt`/extensionless twins | WP01 | |
| T003 | Decide: confirm the URL map, or specify the fallback | WP01 | |
| T004 | Amend `contracts/url-map.md`; escalate if the guide's own text must change | WP01 | |
| T005 | Poetry project, dependencies, dev tooling, click entry point, test harness | WP02 | |
| T006 | `mkdocs.yml`: the nav (ten chapters) and the `not_in_book` declaration | WP02 | |
| T007 | `config.py`: the single base-URL configuration | WP02 | [P] |
| T008 | `roles.py`: Document model, role resolution, `published_name` | WP02 | |
| T009 | `rename.py`: reference rewriting, with the `getting-started.md` trap covered | WP02 | [P] |
| T010 | Role lint — an undeclared document fails the build | WP02 | |
| T011 | Prose drift check — warn on branches, fail on `main`, never fix | WP02 | |
| T045 | Provenance check — every published file traces back to the pack (NFR-003) | WP02 | [P] |
| T012 | `src/theme/site/`: palette and typography, bounded | WP03 | [P] |
| T013 | Landing page derived from the kit's pitch | WP03 | [P] |
| T014 | Per-page AI pointer and `rel="alternate"` metadata | WP03 | |
| T015 | Raw markdown at parallel paths, with the bootstrap published as `AGENTS.md` | WP03 | |
| T016 | `.nojekyll`, subpath correctness, responsive and contrast verification | WP03 | |
| T017 | `book.py`: assemble chapters in nav order | WP04 | |
| T018 | Flatten print-hostile cross-references | WP04 | |
| T019 | `src/theme/book/`: LaTeX template — title page, ToC with page numbers, A4 | WP04 | [P] |
| T020 | Pinned fonts and the pandoc/XeLaTeX container invocation | WP04 | |
| T021 | The single-file HTML book | WP04 | [P] |
| T022 | Tests for assembly and cross-reference flattening | WP04 | |
| T023 | `llms.py`: `llms.txt`, bootstrap first, as a procedure | WP05 | |
| T024 | `llms-full.txt`: chapters concatenated in nav order | WP05 | [P] |
| T025 | Every address derives from the configured base | WP05 | |
| T026 | Tests, including the base-URL swap (SC-006) | WP05 | |
| T027 | `packbranch.py`: the orphan mirror tree builder | WP06 | |
| T028 | Apply rename and reference rewrite to the branch tree | WP06 | |
| T029 | Reproduction gate against the hand-built `d024682` | WP06 | |
| T030 | Force-push publisher; read-only contract stated in the commit message | WP06 | |
| T031 | Tests, including the `getting-started.md` substring trap | WP06 | |
| T032 | `links.py`: extract links, excluding inline-code examples | WP07 | |
| T033 | Assert no path separators in any cross-link (C-001) | WP07 | [P] |
| T034 | Assert resolution on both `main` and `pack` | WP07 | |
| T035 | Tests, including the historical `README.md` regression | WP07 | |
| T036 | `publish.yml`: build, lint, deploy Pages | WP08 | |
| T037 | The pack-branch mirror job | WP08 | |
| T038 | A lint failure blocks **both** publication targets | WP08 | |
| T039 | Baked TeX image to protect the 5-minute budget | WP08 | [P] |
| T040 | Verify rebuild-and-redeploy actually happens on push | WP08 | |
| T041 | SC-001 — cold bootstrap against a real LLM, verifying *order* | WP09 | |
| T042 | SC-002 — the published submodule command, from a bare checkout | WP09 | [P] |
| T043 | SC-003 — print the PDF and read it on paper | WP09 | [P] |
| T044 | Record results; close the mission or escalate | WP09 | |

*T045 is appended rather than inserted: renumbering 30+ existing IDs to slot one subtask in
sequence would churn every prompt for no benefit.*

---

# Phase 1 — Foundation

## WP01 — Prove the machine surface can exist

**Prompt**: [tasks/WP01-prove-machine-surface.md](tasks/WP01-prove-machine-surface.md)
**Priority**: P0 — blocking · **Estimated prompt size**: ~260 lines · **Depends on**: none

**Goal**: Establish, against a real deployment, that the host serves raw markdown as text a model can
read. Every machine-facing requirement rests on it.

**Why this is first**: its failure is silent and total. The site can be finished and beautiful while
`/AGENTS.md` serves as a download and the entire reason for the mission fails. This cannot be tested
locally — it is a property of the deployed host — and if it fails, the fallback changes the published
URL map, which changes the guide's own text. That is a much larger conversation, and it should happen in
week one rather than week four.

**Independent test**: a recorded, real HTTP response for a `.md` on a real Pages deployment, with its
content-type, plus a confirmed or amended `contracts/url-map.md`.

- [x] T001 Stand up a throwaway Pages deployment with `.nojekyll` and probe files (WP01)
- [x] T002 Record the actual HTTP response for `.md`, and for `.txt`/extensionless twins (WP01)
- [x] T003 Decide: confirm the URL map, or specify the fallback (WP01)
- [x] T004 Amend `contracts/url-map.md`; escalate if the guide's own text must change (WP01)

**Risks**: The finding may invalidate the URL map. If so, `src/pack/start.md`, `README.md` and
`technical-suggestions.md` all quote addresses to readers — and content is out of scope. Escalate;
do not quietly edit the pack.

## WP02 — Build foundation and the roles declaration

**Prompt**: [tasks/WP02-foundation-and-roles.md](tasks/WP02-foundation-and-roles.md)
**Priority**: P0 — blocking · **Estimated prompt size**: ~370 lines · **Depends on**: none

**Goal**: Stand up the Python build project, and make the site config the single declaration of chapter
order and document roles that everything else derives from.

**Independent test**: `poetry run pytest` green; the role lint fails a pack containing an undeclared
document; `roles.py` resolves `start.md`'s `published_name` to `AGENTS.md`; the provenance check fails an
output file with no source.

- [x] T005 Poetry project, dependencies, dev tooling, click entry point, test harness (WP02)
- [x] T006 `mkdocs.yml`: the nav (ten chapters) and the `not_in_book` declaration (WP02)
- [x] T007 `config.py`: the single base-URL configuration (WP02)
- [x] T008 `roles.py`: Document model, role resolution, `published_name` (WP02)
- [x] T009 `rename.py`: reference rewriting, with the `getting-started.md` trap covered (WP02)
- [x] T010 Role lint — an undeclared document fails the build (WP02)
- [x] T011 Prose drift check — warn on branches, fail on `main`, never fix (WP02)
- [x] T045 Provenance check — every published file traces back to the pack, NFR-003 (WP02)

**Parallel opportunities**: T007, T009 and T045 are independent of the rest once T005 lands.

**Runs in parallel with**: WP01. Nothing here depends on the spike's finding.

**Risks**: `rename.py` is shared by WP03 and WP06 — get the `getting-started.md` substring trap right
once, here, and both consumers inherit the fix.

# Phase 2 — The surfaces

## WP03 — The browsable site

**Prompt**: [tasks/WP03-browsable-site.md](tasks/WP03-browsable-site.md)
**Priority**: P1 · **Estimated prompt size**: ~330 lines · **Depends on**: WP01, WP02

**Goal**: The readable, navigable, attractive site — and the raw markdown surface it publishes alongside.

**Independent test**: `mkdocs build` produces nav in reading order, search, a landing page from the kit's
pitch, an AI pointer on every page, `.nojekyll`, and raw `.md` at parallel paths with the bootstrap
published as `AGENTS.md`.

- [ ] T012 `src/theme/site/`: palette and typography, bounded (WP03)
- [ ] T013 Landing page derived from the kit's pitch (WP03)
- [ ] T014 Per-page AI pointer and `rel="alternate"` metadata (WP03)
- [ ] T015 Raw markdown at parallel paths, with the bootstrap published as `AGENTS.md` (WP03)
- [ ] T016 `.nojekyll`, subpath correctness, responsive and contrast verification (WP03)

**Risks**: Design investment is bounded to palette and typography (NFR-004). The Gygax homage is Out of
Scope (A-004) and this is where it will try to creep in.

## WP04 — The book and the printable PDF

**Prompt**: [tasks/WP04-book-and-pdf.md](tasks/WP04-book-and-pdf.md)
**Priority**: P1 · **Estimated prompt size**: ~380 lines · **Depends on**: WP02

**Goal**: The cover-to-cover read, with the print typography that justified choosing LaTeX.

**Independent test**: a PDF with a title page, a page-numbered ToC, real pagination, A4 body type, and no
construction that assumes clicking.

- [ ] T017 `book.py`: assemble chapters in nav order (WP04)
- [ ] T018 Flatten print-hostile cross-references (WP04)
- [ ] T019 `src/theme/book/`: LaTeX template — title page, ToC with page numbers, A4 (WP04)
- [ ] T020 Pinned fonts and the pandoc/XeLaTeX container invocation (WP04)
- [ ] T021 The single-file HTML book (WP04)
- [ ] T022 Tests for assembly and cross-reference flattening (WP04)

**Parallel opportunities**: T019 and T021 are independent of each other.

**Runs in parallel with**: WP03, WP05, WP06.

**Risks**: This creates the second style system (recorded in plan.md Complexity Tracking). Flattening
cross-references is part of the work, not polish — a printed page cannot follow "see `ethics.md`".

## WP05 — The machine-readable sources

**Prompt**: [tasks/WP05-machine-sources.md](tasks/WP05-machine-sources.md)
**Priority**: P1 · **Estimated prompt size**: ~270 lines · **Depends on**: WP01, WP02

**Goal**: Let a model consume the guide — and, more importantly, discover that there is a procedure to
follow rather than documents to read.

**Independent test**: `llms.txt` leads with the bootstrap as an instruction; `llms-full.txt` is the
chapters in nav order; changing the configured base changes every address.

- [ ] T023 `llms.py`: `llms.txt`, bootstrap first, as a procedure (WP05)
- [ ] T024 `llms-full.txt`: chapters concatenated in nav order (WP05)
- [ ] T025 Every address derives from the configured base (WP05)
- [ ] T026 Tests, including the base-URL swap (SC-006) (WP05)

**Risks**: An index that satisfies the llmstxt convention while burying the bootstrap under alphabetised
chapters defeats the mission.

## WP06 — The pack branch

**Prompt**: [tasks/WP06-pack-branch.md](tasks/WP06-pack-branch.md)
**Priority**: P1 · **Estimated prompt size**: ~340 lines · **Depends on**: WP02

**Goal**: Publish the markdown alone, under the filename models look for, reproducing the branch that
already exists.

**Independent test**: the generated tree is byte-identical to `d024682`; links resolve on the branch;
`git submodule add -b pack …` works from a bare checkout.

- [ ] T027 `packbranch.py`: the orphan mirror tree builder (WP06)
- [ ] T028 Apply rename and reference rewrite to the branch tree (WP06)
- [ ] T029 Reproduction gate against the hand-built `d024682` (WP06)
- [ ] T030 Force-push publisher; read-only contract stated in the commit message (WP06)
- [ ] T031 Tests, including the `getting-started.md` substring trap (WP06)

**Risks**: **Someone is already depending on this branch.** It was hand-built on 2026-07-16 to unblock
the `5g_arg` project, whose `doc/core` submodule points at it. Automation that diverges makes the guide
lie to readers who already followed its published instructions (R-002).

## WP07 — Link integrity across branches

**Prompt**: [tasks/WP07-link-integrity.md](tasks/WP07-link-integrity.md)
**Priority**: P1 · **Estimated prompt size**: ~250 lines · **Depends on**: WP06

**Goal**: Machine-enforce the invariant that makes the whole architecture possible.

**Independent test**: the checker fails a link containing a path separator, and fails a link that
resolves on one branch but not the other.

- [ ] T032 `links.py`: extract links, excluding inline-code examples (WP07)
- [ ] T033 Assert no path separators in any cross-link (C-001) (WP07)
- [ ] T034 Assert resolution on both `main` and `pack` (WP07)
- [ ] T035 Tests, including the historical `README.md` regression (WP07)

**Risks**: Must exclude inline-code examples — the guide *documents* the link convention using inline
code, and those samples are not links to follow. A naive extractor will fail the build on the guide's own
prose.

# Phase 3 — Publication and acceptance

## WP08 — Continuous publication

**Prompt**: [tasks/WP08-continuous-publication.md](tasks/WP08-continuous-publication.md)
**Priority**: P1 · **Estimated prompt size**: ~280 lines · **Depends on**: WP03, WP04, WP05, WP06, WP07

**Goal**: No surface can lag another, with no human step.

**Independent test**: a change pushed to `main` is live on every surface within five minutes; a lint
failure blocks both targets.

- [ ] T036 `publish.yml`: build, lint, deploy Pages (WP08)
- [ ] T037 The pack-branch mirror job (WP08)
- [ ] T038 A lint failure blocks **both** publication targets (WP08)
- [ ] T039 Baked TeX image to protect the 5-minute budget (WP08)
- [ ] T040 Verify rebuild-and-redeploy actually happens on push (WP08)

**Risks**: Needs Pages enabled and permitted to publish from automation (D-002) — an account-level
prerequisite outside the code. Publishing a good site beside a broken branch is worse than publishing
neither.

## WP09 — Behavioural acceptance

**Prompt**: [tasks/WP09-behavioural-acceptance.md](tasks/WP09-behavioural-acceptance.md)
**Priority**: P0 for mission closure · **Estimated prompt size**: ~240 lines · **Depends on**: WP08

**Goal**: Answer the only questions that decide whether the mission succeeded.

**Independent test**: this WP *is* the test.

- [ ] T041 SC-001 — cold bootstrap against a real LLM, verifying *order* (WP09)
- [ ] T042 SC-002 — the published submodule command, from a bare checkout (WP09)
- [ ] T043 SC-003 — print the PDF and read it on paper (WP09)
- [ ] T044 Record results; close the mission or escalate (WP09)

**Risks**: Requires a real model and a real printer — neither is automatable, and T043 needs a human.
SC-001 checks the *order* of events: a model that scaffolds perfectly but asks about identity second has
failed, because the firewall is the guide's central ethical commitment.

---

## Dependency graph

```
WP01 (spike) ─┐
              ├─► WP03 (site) ──┐
WP02 (base) ──┼─► WP05 (llms) ──┤
              ├─► WP04 (book) ──┼─► WP08 (CI) ─► WP09 (acceptance)
              └─► WP06 (pack) ──┤
                       └► WP07 ─┘
```

## Parallelisation

- **Round 1**: WP01 ∥ WP02 — no shared surface, no shared dependency.
- **Round 2**: WP03 ∥ WP04 ∥ WP05 ∥ WP06 — four lanes. WP07 follows WP06.
- **Round 3**: WP08, then WP09.

## MVP scope

**WP01 + WP02 is the honest MVP**, and unusually the spike matters more than any feature. If WP01 finds
the host cannot serve readable markdown, the URL map — and the guide's published text — change, and every
downstream WP's assumptions move. Nothing else should start until WP01 reports.

If a single shippable increment is wanted after that: **WP02 → WP06 → WP07**. That makes the `pack`
branch reproducible and verified by automation, which is the promise the guide is *already making to
readers today* on a branch built by hand.
