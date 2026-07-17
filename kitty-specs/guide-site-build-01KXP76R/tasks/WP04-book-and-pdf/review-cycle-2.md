---
affected_files:
- src/build/book.py
- tests/test_book.py
cycle_number: 2
mission_slug: guide-site-build-01KXP76R
reproduction_command: pdftotext -layout dist/book/dungeon-masters-guide.pdf - | grep -n '\*'
reviewed_at: '2026-07-17T00:30:00Z'
reviewer_agent: reviewer-renata
verdict: approved
work_package_id: WP04
---

# WP04 review — cycle 2 (re-review of the cycle-1 fix)

Verdict: **approved**. Both cycle-1 defects are fixed, I watched both guards fire, and
nothing regressed. Scope held to the two defects; everything cycle 1 approved is settled
and was not relitigated.

## Issue 1 — emphasis-safe flattening: **fixed**

`_emphasised_title()` now emits raw inline LaTeX `\emph{...}` (a pandoc `RawInline`),
which composes inside `\emph`, `\textbf`, or nothing at all. `_reference_index` routes
both reference kinds through it, so no replacement can carry a markdown delimiter.

**I made the guard fire.** Reverting `_emphasised_title` to `f"*{title}*"`:

```
13 failed, 124 passed
Flattening introduced 2 markdown '*' delimiter(s) (2 → 4)
```

— matching the reported 13 exactly. On the whole assembled book the same guard reports
`introduced 8 markdown '*' delimiter(s) (14 → 22)`. Restored, and the tree is clean.

`check_emphasis_safety()` is the right shape, and the inequality is the reason. Stating it
as "delimiters may fall, never rise" makes it **total over the document** rather than a
pattern-match on the shapes we happened to remember — any future replacement that reaches
for `*` fails the build instead of reaching a page. An equality would have failed on the
pack's own `[**ethics.md**](ethics.md)` house style and been switched off within a week.
It is also correctly scoped to the *delta*: it polices what the transform introduces, not
whether the authored prose is well-formed. That boundary is exactly right, and it is what
makes the page-45 call below coherent rather than convenient.

`test_pandoc_reads_the_flattened_preamble_as_one_emphasis_span` asks the only authority
that counts — pandoc's own reader, via the pinned image — for a single `Emph` node. I
confirmed it genuinely executes against the pinned image rather than skipping.

**On the page**: stray-asterisk lines in the extracted PDF text fell from **22 → 3**. PDF
pages 19, 21, 27, 33, 37, 41, 47 are now clean. Of the surviving 3, one is
`*.some-platform.com` inside a fence (legitimate, as cycle 1 noted) and two are page 45,
below.

## Issue 2 — the missing-glyph regex: **fixed**

`_MISSING_CHARACTER` now matches the substring anywhere on the line, with a comment that
names the trap (the build hears the warning from *pandoc*, which relays it with its own
severity prefix — not from XeLaTeX).

**I reproduced the end-to-end proof.** Added `🤖` to `COVERED_CHARACTERS` without
`fc-list` — the exact mistake the allow-list's own docstring warns of, blinding the
pre-render guard — plus `🤖` in a chapter H1. Cycle 1 printed `OK` here with the emoji
absent from the PDF. Now:

```
Rendering the PDF produced a PDF with characters silently dropped — XeLaTeX logged 2
'Missing character' warning(s) and exited 0:
  [WARNING] Missing character: There is no 🤖 (U+1F916) (U+1F916) in font DejaVu Sans Bold/OT:script=l
  [WARNING] Missing character: There is no 🤖 (U+1F916) (U+1F916) in font DejaVu Serif Bold/OT:script=
=== EXIT CODE: 1 ===
```

Both mutations reverted. The tests use **captured** log lines, prefix and all — the
distinction that matters, since an invented line would have passed against the broken
regex too. `test_the_missing_character_pattern_is_not_anchored_past_pandocs_prefix`
asserts the old anchored pattern matched nothing, which documents the trap for the next
person to tidy the regex. `test_the_missing_glyph_guard_fires_against_the_real_toolchain`
drives the real image through `_run` and covers the whole failed path including pandoc's
exit code of zero.

## The page-45 attribution: **it holds**

I verified this independently rather than taking the claim. Extracted
`src/pack/worked-example.md:3-6` and rendered it through the pinned image with **zero
flattening** — raw bytes from the pack, no code involved:

```latex
\emph{Companion to \texttt{creator-kit.md}. ... The point is not }what* was
built but the \textbf{shape of how it grew}: ... exactly right.*
```

Identical failure mode: the outer span closes early at `}what*` and `right.*` is stranded.
The source authors `*what*` nested inside an outer `*...*` span, and markdown has no such
reading. This is an **authored content defect, not a code defect**, and
`check_emphasis_safety` correctly does not fire because the transform introduced nothing.

**Their reasoning for declining is sound and I endorse it.** C-002/C-006 forbid writing to
`src/pack/`. A build gate on authored-malformed emphasis would be a gate whose only
resolution path is forbidden to whoever trips it — it would hard-block WP08's deployment
on prose they are not permitted to fix, which is a stakeholder call and not theirs to
make. That is the same reasoning their own test docstring gives for the inequality: a
check that fails on what you cannot fix gets switched off as fast as one that fails on
nothing. Raising it as a finding was the correct disposition. They were also right to
treat the code fix as independent of the content instance.

## Gates

- `poetry run pytest`: **137 passed** (up from 125), no skips.
- `black --check`: 14 files unchanged. `mypy`: clean, 7 source files.
- `git diff --stat src/pack/` vs mission base: **empty**.
- PDF: 58pp, A4 (595.28 x 841.89 pts), **zero** unresolved `??`.
- HTML book unaffected: `book.web.md` has **zero** `\emph`; `book.print.md` has 51. (The
  two `emph` greps in `book.html` are the authored word "emphatically".)

## Anti-pattern checklist

| # | Item | Verdict |
|---|---|---|
| 1 | Dead code | **PASS** (was FAIL) — `_report_missing_glyphs` now fires against real output; watched it. |
| 2 | Synthetic-fixture test | PASS — log lines captured, not composed; the e2e test drives the real image. |
| 3 | Silent empty return | PASS — `_pandoc_ast` returns `None` to let the caller skip cleanly; documented. |
| 4 | FR coverage | **PASS** (was FAIL) — FR-004 now tested for what the replacement produces at its landing site. |
| 5 | Frozen surface | PASS — `src/pack/` diff empty. |
| 6 | Locked decision | PASS. |
| 7 | Shared-file ownership | PASS — `cli.py` additive. |
| 8 | Production fragility | PASS — build-time fail-loud raises. |

## Not blocking

- `check_emphasis_safety` also polices `_`. `_tex_escape` renders an underscore in a
  chapter title as `\_`, inserted afresh at each reference site, so a future title
  containing `_` would trip the guard. It fails loud with a clear message and no current
  title is affected — noted for whoever adds one.
- Credit: they fixed the cycle-1 `nonstopmode` comment nit unprompted, and the replacement
  comment is accurate about why the flag is there (CI hanging on stdin, not `\pageref`).

## Artifact repair

`review-cycle-1.md` was missing the YAML frontmatter every sibling review carries, so
`move-task` could not parse its verdict and refused the transition. I added the
frontmatter recording its actual verdict (`rejected`) unchanged; the prose is untouched.
