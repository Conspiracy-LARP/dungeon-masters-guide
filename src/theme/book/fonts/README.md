# Fonts, licences, and the pinned toolchain

What the printable book (FR-004) is set in, where those fonts come from, what their
licences permit, and how long the render takes. Written for two readers: whoever changes
the typography, and whoever has to answer a licensing question about a public repo.

## There are no font files in this directory, and that is the decision

This directory carries no `.ttf` or `.otf`. **The fonts are pinned by pinning the image
they live in**, not by committing binaries next to this file.

`src/build/book.py` pins:

```
pandoc/extra:3.8-ubuntu@sha256:21ce6c5a9ce8311bdc257902811e794d66a585bc5da6d8df755f013a54695d69
```

`poetry run guide book image` prints it; that is the string WP08 wires into CI.

Pinning by **digest**, not by tag. A tag moves. The day `pandoc/extra:3.8-ubuntu` is
rebuilt with a different font package, the book's line breaks change and nobody touched
the pack — which is exactly the drift NFR-003 exists to make impossible. A digest cannot
move.

Why not commit the font files, which is the more obvious reading of "pin the fonts"?

- The image has to be pinned **anyway** — it carries XeLaTeX and every LaTeX package
  `template.tex` loads. A pinned image plus committed fonts is two pins for one job, and
  the pair can disagree.
- Committed fonts still need the image to have `fontconfig` see them, so it buys nothing
  a `\setmainfont` name does not already buy.
- Font binaries in a public repo are a redistribution act, and this one does not need to
  be performed. The image already carries the fonts under a licence that permits its own
  distribution; we depend on it rather than becoming a second distributor.

The property that actually matters — *the fonts are the same on every machine, and are
not the ones the developer or the CI runner happens to have installed* — is delivered by
the digest.

## What the book is set in

Declared in `src/theme/book/template.tex`. All three ship in the pinned image as Debian
packages `fonts-dejavu-core` and `fonts-dejavu-mono`, version 2.37-8.

| Role | Typeface | Where it is used |
|---|---|---|
| Body | **DejaVu Serif** (scaled 0.92) | Running text. Scaled because DejaVu's x-height is large; 11pt of it reads like 12pt of a Times-alike, so 11pt/0.92 lands on a comfortable A4 measure of roughly 68 characters. |
| Headings | **DejaVu Sans** (scaled 0.92) | Chapter and section heads, running heads, folios. A sans/serif split, echoing the site's Material theme without pretending to match it. |
| Code | **DejaVu Sans Mono** (scaled 0.82) | Fenced blocks and inline code. |

**DejaVu Sans Mono is not a default — it is a requirement.** It is the only mono in the
image carrying the box-drawing characters (U+2500 `─`, U+251C `├`, U+2502 `│`, U+2514
`└`) that the directory trees in `technical-suggestions.md` and `start.md` are drawn
with. Those trees live inside code fences, where verbatim is verbatim and no substitution
can reach them, so the font either has the glyphs or the trees print as holes. Verified
in the image, not assumed:

```bash
docker run --rm --entrypoint fc-list \
  pandoc/extra:3.8-ubuntu ":charset=2500:family=DejaVu Sans Mono" family
```

### Licence

**Bitstream Vera Fonts Copyright** (DejaVu changes are in the public domain).
Copyright © 2003 Bitstream, Inc. Full text in the image at
`/usr/share/doc/fonts-dejavu-core/copyright`; upstream at
<https://dejavu-fonts.github.io/License.html>.

A permissive, MIT-style font licence. It permits use, copying, modification and
redistribution, with two conditions worth naming because they are the ones people trip
over:

1. A **modified** font may not keep a name containing "Bitstream" or "Vera".
2. The Font Software **may not be sold on its own**, though it may be sold as part of a
   larger package.

Neither binds this repository as it stands: we redistribute no font files and modify
nothing. **Both would bind it the moment someone commits a `.ttf` into this directory** —
which is one more reason not to. If that ever happens, the copyright notice and
permission notice must travel with the files, per condition 1 of the licence text.

The rendered PDF **embeds subsets of these fonts**, which the licence expressly permits
("reproduce and distribute", and the fonts as part of a larger work). Publishing the PDF
is fine.

## Emoji: a substitution, not a font

The guide uses two emoji — ✅ and ❌, in the good-tell/bad-tell table in
`storytelling.md`. **The pinned image's fonts cover neither** (`fc-list ":charset=2705"`
returns nothing), and no emoji font was added. `src/build/book.py`'s
`PRINT_SUBSTITUTIONS` replaces them with pifont dingbats — `\ding{51}` and `\ding{55}` —
before XeLaTeX sees a byte.

The reasoning is in the code. Briefly: the book is printed, so a colour emoji is grey ink
anyway; a dingbat sits on the baseline with the surrounding text instead of riding above
it like a sticker; and it keeps a font dependency out of a decision whose purpose is to
remove font dependencies. The HTML book (FR-003) keeps the real emoji — browsers have
fonts for them.

**The trade-off, stated because it is real.** Pifont's dingbats come from ZapfDingbats,
whose encoding carries no `ToUnicode` mapping. In the PDF's *text layer* the marks
extract as `3` and `7` — copy-and-paste and a screen reader get those, not ✓ and ✗. The
printed page is correct, which is what this output is for (SC-003), and the table's two
columns are titled in words as well as marks, so the meaning survives extraction. If the
PDF ever needs to be accessible as a first-class requirement, this is the thing to
revisit — add an emoji font, or map the glyphs.

### If a new character appears in the guide

XeLaTeX does **not** fail on a glyph it cannot find. It writes `Missing character` to the
log and typesets nothing: the text silently vanishes from the printed page, at the end of
a green build. Two guards stand in the way, and both are in `src/build/book.py`:

- `check_font_coverage()` runs **before** the render, over the print intermediate. Every
  non-ASCII character must be in `COVERED_CHARACTERS` — an allow-list verified against
  this image with `fc-list` — or the build fails naming the character and its code point.
- `_report_missing_glyphs()` runs **after**, and fails on `Missing character` in
  XeLaTeX's own log. Belt and braces, because the log is the only thing that knows what
  fonts were really loaded.

So the answer to "someone added a character the fonts lack" is a red build with a
readable message, not a hole on page 40. To resolve one: add a substitution to
`PRINT_SUBSTITUTIONS`, or add a font to `template.tex`, verify with `fc-list` inside the
image, and add the character to `COVERED_CHARACTERS`.

## Build duration — for WP08 and the NFR-005 budget

NFR-005 gives the **whole pipeline** five minutes. Measured on this repo's real pack (ten
chapters, 58 pages), Apple M-series, Docker Desktop:

| Step | Warm image | Cold |
|---|---|---|
| `guide book assemble` | < 0.5 s | — |
| `guide book html` | ~0.9 s | — |
| `guide book pdf` (three XeLaTeX passes) | **~5 s** | — |
| `docker pull` of the pinned image | 0 s (cached) | **~58 s**, 1.1 GB |
| **Book total** | **~6 s** | **~65 s** |

The render is not the risk; **the pull is**. Notes for whoever wires CI:

- **Cache the image, or run the job inside it.** GitHub Actions' `container:` key does
  the latter and is the tidier answer — inside the image `guide book pdf --runner local`
  uses the pinned pandoc directly, with no docker-in-docker.
- Do **not** install TeX per run. `apt-get install texlive-*` is minutes, and it would
  spend NFR-005's budget before pandoc reads a byte. That is the whole reason a prebuilt
  image was specified (T020).
- The book should be treated as a **~60-second worst case** in the pipeline budget, and
  ~6 s once the image is cached.
- `book.py`'s `EXPECTED_PDF_SECONDS` is set to 25 — five times the measured render, as
  headroom for a CI runner slower than a developer laptop. `guide book pdf` warns past
  double that; if it fires on a warm image, the render has regressed and WP08 should
  hear about it.

## Changing any of this

The image, the font names, `COVERED_CHARACTERS` and this file are one decision in four
places. To move to a new image:

1. Pull it and read its digest.
2. Confirm the three DejaVu families are present (`fc-list : family`).
3. Re-verify glyph coverage for every character in `COVERED_CHARACTERS`.
4. Confirm the LaTeX packages `template.tex` loads are present (`kpsewhich`). The current
   image has no `tocloft`, no `newunicodechar` and no `ragged2e`; the template works
   around all three rather than depending on them.
5. Update `PANDOC_IMAGE_DIGEST` in `src/build/book.py`, and update this file.

And note the standing cost, recorded in `plan.md` § Complexity Tracking: `template.tex`
is a **second style system**, independent of the site's CSS (WP03). The shared decisions
— palette, the serif/sans split — are declared at the top of `template.tex` and mirrored
in `src/theme/book/book.css`. Exact parity is not the requirement (NFR-004); noticing
when they drift is.
