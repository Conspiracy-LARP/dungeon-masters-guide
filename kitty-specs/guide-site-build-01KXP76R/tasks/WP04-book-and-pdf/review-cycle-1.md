---
affected_files:
- src/build/book.py
- tests/test_book.py
cycle_number: 1
mission_slug: guide-site-build-01KXP76R
reproduction_command: pdftotext -layout dist/book/dungeon-masters-guide.pdf - | grep -n '\*'
reviewed_at: '2026-07-16T22:51:27Z'
reviewer_agent: reviewer-renata
verdict: rejected
work_package_id: WP04
---

# WP04 review — cycle 1: changes requested

Reviewer: claude:opus:reviewer-renata:reviewer
Verdict: **changes requested** — two defects, both reproduced live in this worktree.

I rendered the PDF myself (`poetry run guide book assemble && poetry run guide book pdf`,
5.3s warm, container runner) and opened it. Almost everything you claimed is true and
verified. Two things are not.

## What I verified as correct (so you don't re-litigate it)

- **58 pages, A4** (595.28 x 841.89 pts), `twoside`, title page, running heads, folios.
  `pdfinfo` confirms. Title page carries the live `base-url` from `absolute_url` — good.
- **ToC carries page numbers**, depth 2, dotted leaders. Correct.
- **The `1.14` fix is real and it works.** `creator-kit.md`'s subsections run to `1.14`
  and print cleanly in the ToC with no collision into the title. The widened
  `\l@section`/`\l@subsection` boxes are the right fix and the comment explaining that
  LaTeX gives no warning is accurate.
- **Zero unresolved `??`** in the extracted text. Every `\pageref` resolved.
- **Cross-references resolve to real chapter+page**: "Chapter 6, Ethics (page 31)" etc.
- **Exactly one `.md` survives**, and you left it alone correctly: `└─ README.md` inside
  the `text` fence at `src/pack/technical-suggestions.md:169`. That is the reader's own
  node's README in a directory tree — not a cross-reference. Correct call.
- **T018's exclusion line is right.** `[`e.md`](e.md)` is a link (flattened);
  `` `[e.md](e.md)` `` and `` `src/pack/e.md` `` are illustrations (printed verbatim).
  The earliest-position alternation in `_SEGMENT_PATTERN` genuinely implements that, and
  the reasoning — the guide must be able to state its own convention by showing it — is
  correct and well argued.
- **Chapters in nav order, `not_in_book` excluded**, no hard-coded list.
  `test_reordering_nav_reorders_the_book` is a real derivation test, not a restatement.
- **`git diff --stat src/pack/` is empty.** Clean.
- **Gates**: 125 passed, `black --check` clean, `mypy` clean.
- **The dingbat `ToUnicode` trade-off is acceptable.** ✅/❌ extract as `3`/`7`, but the
  printed page is correct and the columns are titled in words. Disclosed, reasoned,
  fine.
- **`check_font_coverage()` fires.** I watched it. Added `🤖` to a chapter H1; the build
  stopped pre-render naming `'🤖' (U+1F916)` and both ways out. That guard is real.
- Content finding (repetitive preambles cover-to-cover) correctly raised, not acted on.
  C-006 respected.

---

## Issue 1 — The flattening breaks the italic span it lands in. Literal `*` characters print on 8 of the 10 chapter opening pages.

**This is an FR-004/print-quality defect and it is on the first line of almost every
chapter.** It is visible in the rendered PDF right now.

`_reference_index` builds its replacement as markdown emphasis:

```python
body = f"Chapter {document.position}, *{document.title}*"
```

That is inserted wherever the reference appeared — including inside spans that are
*already* emphasised. The guide's chapter preambles are exactly that shape. From
`src/pack/getting-started.md:3-6`:

```markdown
*Companion to `creator-kit.md` (see §3). This is the practical on-ramp: how to set up a place to work,
... the shortest path there.*
```

After `flatten_for_print` (`dist/book/book.print.md:489`):

```markdown
*Companion to Chapter 1, *Creator Kit* (page \pageref{ch-creator-kit}) (see §3). This is the practical on-ramp: ...
... the shortest path there.*
```

Markdown cannot nest `*` in `*`. Pandoc's own LaTeX writer, confirmed directly against
the pinned image:

```latex
\emph{Companion to Chapter 1, }Creator Kit* (page \pageref{ch-creator-kit}) (see §3). This is the on-ramp.*
```

The emphasis **closes early** after "Chapter 1, ", "Creator Kit" goes upright, the rest
of the preamble **loses its italic entirely**, and **two literal asterisks are typeset**.

On PDF page 19 (book page 13, Chapter 2's opening page) the reader sees:

> Companion to Chapter 1, Creator Kit\* (page 1) (see §3). This is the practical on-ramp:
> ... this is the shortest path there.\*

— upright, where the source says italic, with two stray asterisks.

**Scope.** 8 chapter preambles, on PDF pages **19, 21, 27, 33, 37, 41, 45, 47** — the
opening page of 8 of the 10 chapters. Plus at least three in-prose parentheticals,
including `src/pack/storytelling.md:143`:

```
Creator Kit* (page 1) (§8).)*
```

22 lines of extracted PDF text carry a stray `*`; only one of those (`*.some-platform.com`,
inside a fence) is legitimate. Reproduce with:

```bash
pdftotext -layout dist/book/dungeon-masters-guide.pdf - | grep -n '\*'
```

**Why the guards missed it.** `check_print_ready()` asks "did the reference get
replaced?" — yes, it did. Nothing asks "is what I substituted in still well-formed
markdown *in the context it landed in*?" The reference is gone, the build is green, and
the page is wrong. That is the same shape as Issue 2 and the same shape this mission has
now found repeatedly: the check confirms the action, never the result.

**Note the irony worth absorbing**: the WP prompt pointed straight at this construct —
*"The guide's chapters each open with an italic 'Companion to `creator-kit.md`'
preamble."* You read that note and correctly declined to edit the prose (right call,
C-006). But the note was naming the exact construct your transform breaks.

**Fix direction** (your call, this is not prescriptive):
- Emit the title as raw LaTeX `\emph{...}` / `\textit{...}` rather than markdown `*`.
  Raw inline LaTeX composes inside `\emph` and you already use the `{=latex}` escape
  hatch for `\chaptermark`. Cheapest fix; note it makes the string print-only, which it
  already is (`\pageref` is in there).
- Or detect that the insertion point is inside an emphasis span and emit the title
  unemphasised there.
- Or drop the emphasis from the replacement entirely — "Chapter 1, Creator Kit (page 1)"
  reads fine and the chapter number already carries the signal.

**Required with the fix**: a test that renders the *actual preamble shape* — emphasis
containing an inline-code filename — through `flatten_for_print` and asserts the result
parses as a single emphasis span with no literal `*`. Every current flattening test
feeds it a bare sentence with no surrounding emphasis, which is why this shipped.

The HTML book is **not** affected — `retarget_for_html` introduces no emphasis. Verified.

---

## Issue 2 — `_report_missing_glyphs()` can never fire. The regex does not match pandoc's output.

You described this as the belt to `check_font_coverage`'s braces, reading "the one place
that has the final say: XeLaTeX itself, on the actual fonts it actually loaded." It reads
it and is structurally incapable of seeing anything.

```python
_MISSING_CHARACTER: Final[re.Pattern[str]] = re.compile(r"^Missing character:.*$", re.MULTILINE)
```

`^` anchors to start-of-line. pandoc prefixes every one of these with `[WARNING] `. The
real lines, captured from the pinned image:

```
'[WARNING] Missing character: There is no 🤖 (U+1F916) (U+1F916) in font DejaVu Serif Bold/OT:script='
'[WARNING] Missing character: There is no 🤖 (U+1F916) (U+1F916) in font DejaVu Sans Bold/OT:script=l'
```

```
lines containing 'Missing character': 2
book.py's regex ^Missing character:.*$ (MULTILINE) matches: 0
```

**Demonstrated live, end to end.** I applied the mutation a human would actually make —
adding a character to `COVERED_CHARACTERS` **without** verifying it with `fc-list`, which
is precisely the mistake the allow-list's own docstring warns about:

```python
COVERED_CHARACTERS: Final[frozenset[str]] = frozenset(
    "\U0001F916"  # never verified with fc-list
    "—"
    ...
```

...plus `🤖` in a chapter H1. Result:

- `check_font_coverage()` — blind by construction; the character is "covered". Passed.
- `_report_missing_glyphs()` — **did not fire.**
- `guide book pdf` printed **`OK: ... in 4.7s`**.
- The emoji is **absent from the PDF**. `pdftotext` shows `6 Ethics — what we satirise`,
  the `🤖` silently gone.

A green build and a book with a character missing from it — the exact outcome you wrote
this guard to make impossible, reproduced against your own code.

**Why it was never caught**: `grep -rn "_report_missing_glyphs\|Missing character" tests/`
returns nothing. **The guard has no test.** Every emoji test in `test_book.py` exercises
`check_font_coverage`, which is the guard that works. The one that doesn't work is the
one nobody asked to fire.

This does not make `check_font_coverage` worthless — it is a genuine guard and it fires.
But it is the *only* thing standing, and it can only ever be as correct as its
hand-maintained allow-list. The post-render check exists precisely to catch the allow-list
being wrong, and it cannot.

**Fix**: match the substring rather than anchoring (e.g. `re.compile(r"^.*Missing character:.*$", re.MULTILINE)`
or just `"Missing character:" in log` with per-line extraction), and add a test that
feeds `_report_missing_glyphs` a **real captured pandoc log line** — `[WARNING] ` prefix
and all — and asserts `BookError`. A test written against an invented log line would have
passed against the broken regex too, so please paste a real one; the two above are yours,
taken from the pinned image.

---

## Anti-pattern checklist

| # | Item | Verdict |
|---|---|---|
| 1 | Dead code | **FAIL** — `_report_missing_glyphs()` is called, but its regex matches nothing it will ever be handed. Live call site, dead effect. |
| 2 | Synthetic-fixture test | PASS — the pack fixture is real; delete the transforms and the tests go red. |
| 3 | Silent empty return | PASS — the `return None`s in `_transform` callbacks are the documented "leave as written" contract. |
| 4 | FR coverage | **FAIL** — FR-004 is tested for *reference removal* but not for *what the replacement produces on the page*. Issue 1 shipped through the gap. |
| 5 | Frozen surface | PASS — `git diff --stat src/pack/` empty (C-002, C-006). |
| 6 | Locked decision | PASS — no `MUST NOT` contradicted; pandoc/XeLaTeX per decision `01KXP7BCG6XFDHDRGZ57NXG90Q`. |
| 7 | Shared-file ownership | PASS — `src/build/cli.py` changes are purely additive (no deleted lines in the diff); `src/theme/site/**` untouched. |
| 8 | Production fragility | PASS — `BookError` raises are build-time, fail-loud by design, each with rationale. |

## Not blocking

- **NFR-005**: 5.3s warm render measured; the ~58s cold image pull is a WP08 concern and
  is already recorded there. Not a WP04 defect.
- **Content**: preambles reading repetitively cover-to-cover — correctly out of scope
  (C-006), correctly raised rather than fixed.
- Minor, take it or leave it: the comment above `--pdf-engine-opt=-interaction=nonstopmode`
  in `render_pdf` explains *two-pass `\pageref` resolution*, which is not what
  `nonstopmode` does (pandoc handles the passes). The behaviour is fine; the comment
  points at the wrong flag.

## Summary

The typography, the toolchain pinning, the exclusion rule, the `1.14` fix, the derivation
from `roles.load_documents()` and the pack-immutability story are all genuinely good and I
verified each. `check_font_coverage` is a real guard and I watched it fire. Two things
need fixing: a substitution that breaks the markdown it lands in and prints literal
asterisks on 8 chapter opening pages, and a second guard whose regex guarantees it never
sees the warning it was written to catch.
