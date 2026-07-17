# Follow-ups — content changes queued behind the build mission

*Stakeholder-directed, 2026-07-16. All of these are **content** (`src/pack/`) or naming, which the
build mission (`guide-site-build-01KXP76R`) is explicitly forbidden to touch (C-006). They are queued
deliberately, not forgotten — the build ships first, then these land in one pass on the merged tree
where `mkdocs.yml`, `llms.py` and `book.py` all coexist.*

## Done, parked on a stash / awaiting merge

1. **`premise.md` — new chapter, position 2.** The unifying idea nobody owned: *what if it were all
   true, and what else would then be true?* Pulls the RAW/Shea lineage and the "impossible mansion"
   passage out of the kit, and adds the entailments (staffed, old, self-contradicting, banal, and
   nobody — not even the conspirators — has the whole picture). Distinct from `philosophy.md` (why we
   do it) and `storytelling.md` (how we tell it).
   *Illuminatus!* publication verified: Dell paperbacks, **September/October/November 1975**; written
   across the late 1960s–early '70s. The old text conflated writing with publication.
2. **`getting-started.md` — rewritten to the real flow.** It described the human doing the setup, which
   predates the bootstrap. Now six steps: blank repo → check out → fire up your agent → *"Please read
   and action <url>"* → it scaffolds and asks for the guardrails → create.
3. **`creator-kit.md`** — H1 → *"Introduction — a shared world of diegetic conspiracy satire"*; stale
   footer ("tell the LLM: Let's begin… Section 3") replaced with a link to `getting-started.md`.

## Queued — needs the merged tree

4. **Site/book/index title → "Conspiracy Larp: Player/Creator's Kit".**
   **Do the single-source fix first.** The title is currently stated in three independent places that
   can drift: `mkdocs.yml` `site_name`, `llms.py` `TITLE`, `book.py` `BOOK_TITLE`. `config.py` exposes
   `site_url`/`nav`/`extra` but **not** `site_name`. Expose it, have `llms.py` and `book.py` consume it,
   then the retitle is one line instead of three. Same class of drift the reading order already fixed.
5. **Rename `creator-kit.md` → `introduction.md`.** Rationale: the *project* is the Creator's Kit; one
   chapter should not claim the name. This is a **bulk edit** — 24 refs in the pack, 28 outside, plus
   `mkdocs.yml` nav and WP02's test fixtures (`conftest.py`, `test_roles.py`, `test_rename.py`,
   `test_provenance.py`). Use the `spec-kitty-bulk-edit-classification` skill. WP07's link checker
   catches any miss on both branches — that is what it is for.
   Also consider: nav label "Creator Kit" → "Introduction".

## The blocker these all share — FIXED (WP08, 2026-07-17)

*Was:* WP06's reproduction gate compared a tree generated from **live `src/pack/`** against `d024682`,
so it asserted "the guide's content never changes again" rather than "the automation reproduces the
hand-built branch" — the mission's signature defect inverted: not a check with no teeth, but a check
biting the wrong thing.

*Now:* `build.packbranch.verify_reproduction()` renders from the hand build's **own inputs**
(`39c2452`, tagged `pack-hand-build-inputs`) and compares against `d024682` (tagged `pack-hand-build`).
The claim is about the generator, with the prose held fixed, so **content edits no longer red it** —
proven in CI both ways: it stayed green when the live pack was edited, and went red when the generator
was mutated to skip either half of the rename.

Both reference commits are now **tagged**. `d024682` was an orphan reachable only as the tip of `pack`,
which CI force-pushes on every push to `main` — the first successful mirror would have orphaned the
gate's own reference and left it reading a commit git is free to collect.

**Content is no longer blocked by this gate.** Land the items above.

## What still blocks a green `main` (WP08 finding, 2026-07-17)

Items 1–3 above have **landed** in `src/pack/`, but their consequences were not finished, and the
gates are correctly reporting it. `guide roles lint`, `guide links check`, `mkdocs build --strict`,
`guide verify provenance` and the reproduction gate **all pass**; `pytest` does not. Six failures, none
of them stale tests — each is the guard doing its job. All need a `src/pack/` or spec edit, which the
build mission is forbidden to make (C-002/C-006):

| Failing test | Real finding |
|---|---|
| `test_real_pack_has_no_prose_drift` | `README.md` and `creator-kit.md` never list `premise.md`. A reader of the prose would not learn the chapter exists. |
| `test_check_drift_cli_on_main_exits_zero_when_there_is_no_drift` | Same root cause. `guide roles check-drift` warns on a branch but **fails on `main`** — so this alone reds the pipeline after merge. |
| `test_the_pack_declares_no_absolute_address_of_itself` | `getting-started.md` and `start.md` now quote the deployed base URL. The rewritten flow ("Please read and action `<url>`") needs it — but it makes changing the domain a **content** change, breaking SC-006's one-value promise. **A decision, not a typo.** |
| `test_swapping_the_base_moves_every_generated_address` | Consequence of the above: those addresses survive a base swap. |
| `test_real_pack_declares_ten_chapters` | `mkdocs.yml` `nav` now has **11** chapters; `doc/build.md` still specifies **ten** and never mentions `premise.md`. The declaration has drifted from the spec — fix `doc/build.md` (§ reading order and "the ten documents"), then the test. |
| `test_the_theme_is_material_lightly_dressed` | `extra.css` (the version stamp) is a third stylesheet. The stakeholder asked for the stamp, so this is the "requirement or project?" question the test exists to raise — answer it and update the allow-list. |

Also pre-existing and unrelated to content: `mypy` reports
`cli.py:21: Incompatible import of "DEFAULT_OUTPUT_DIR"` (a `Path` imported over a `str`).

---

## Period artifacts as SVG assets in the pack (agreed 2026-07-17, not started)

**Why:** `worked-example.md`'s subject is manufacturing evidence, and its own argument is that upholstery
(dates, chrome, screenshots) is what makes a theory feel researched. A chapter making that case while
shipping only ASCII is arguing for something it declines to demonstrate. Stakeholder: *"an excerpt with a
screenshot lands harder."* Agreed; ASCII mocks are live and correct in the meantime, nothing is blocked.

**Decision already taken: SVG, not PNG.** It is text, so it diffs and reviews in git; it scales; it is
authored directly rather than screenshotted; and it avoids putting the first binary in the pack.

**This is not as radical as it first looks.** "Flat" forbids *subdirectories*, not non-markdown files.
`src/pack/hansard-1926.svg` referenced as `![...](hansard-1926.svg)` **is** a bare sibling link. It obeys
C-001 rather than breaking it, and resolves on the site, the pack branch and GitHub alike.

**What must change, and the trap in each:**

1. `build/packbranch.py` — `render_documents()` / `build_tree()` glob `*.md`. Assets are silently
   dropped, so the branch would ship markdown pointing at images that do not exist. **This is the
   contract `5g_arg` depends on via its `doc/core` submodule.** Reproduction gate applies.
2. `build/roles.py` / `guide roles lint` — requires every document declared. Assets need an *explicit*
   exemption. An accidental one (the glob simply not matching) means the lint quietly stops meaning what
   it says, which is this mission's signature defect.
3. `llms.txt` / `llms-full.txt` — an image is invisible to the LLM audience, which is half this project's
   readership. **Keep the ASCII mocks.** They are not a fallback; they are the correct machine-readable
   form. The SVG is the human-facing one. Both, not either.
4. `book.py` — inlines content; an external asset reference needs handling. Note the glyph check already
   rejects box-drawing characters, so SVG text must use fonts the book carries.

**Acceptance:** `git submodule add -b pack <repo> doc/core` still yields working images; `llms-full.txt`
still conveys every artifact in text; `guide roles lint` fails if an asset is undeclared; the book
renders. Do not start this without room to hold the pack-branch contract, the four surfaces and the
reproduction gate in context at once.

## The preservation track belongs in storytelling.md (raised 2026-07-17, not started)

`worked-example.md` now carries a formal principle that outgrows it: an unpreserved record and a
character's interior thoughts are the same category error. Both are things nobody in the world could have
found, and publishing either walks an omniscient narrator back through the membrane. The consequence is a
construction rule — the chronology has two tracks, what happened and what happened to the evidence, and
the second decides what the reader is permitted to see.

This is a general storytelling law, not a fact about the illiteracy node, so by the hub-and-spoke rule it
belongs in `storytelling.md` (which owns "show, don't tell" and the realism engine), with the chapter
demonstrating rather than stating it. Left in place for now because the chapter is the only surface that
currently shows it working. If `storytelling.md` takes it, check the kit's §6 summary still tells the
truth.
