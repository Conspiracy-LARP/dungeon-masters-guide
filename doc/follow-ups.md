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

## The blocker these all share

**WP06's reproduction gate reds on ANY content change** — proven, not predicted:
`test_generated_tree_reproduces_the_hand_built_branch` compares **live `src/pack/`** against `d024682`,
so it asserts "the guide's content never changes again" rather than "the automation reproduces the
hand-built branch". C-005 asked for a one-time proof *before* the automation takes over; WP06's own
prompt said to compare against `d024682`'s **inputs** (regenerate from that commit's `src/pack/`).

**Fix that gate before landing any content**, or the first legitimate edit reds CI. This is the ninth
instance of the mission's signature defect, inverted: not a check with no teeth, but a check biting the
wrong thing.
