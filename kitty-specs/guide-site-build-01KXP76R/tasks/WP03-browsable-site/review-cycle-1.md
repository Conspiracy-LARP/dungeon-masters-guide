---
affected_files:
- tests/test_site.py
cycle_number: 1
mission_slug: guide-site-build-01KXP76R
reproduction_command:
reviewed_at: '2026-07-16T21:45:00Z'
reviewer_agent: reviewer-renata
verdict: rejected
work_package_id: WP03
---

# WP03 review — cycle 1

**Verdict: changes requested.** Two of the four claimed regression tests do not fire. Both fixes are
one-liners; nothing in the shipped product is wrong.

Credit where it is due, because it shapes what follows. I tried to break the work and mostly could not:

- **`/AGENTS.md` is correct.** Byte-identical to `src/pack/start.md`; `site/start.md` absent; the one
  source reference (`README.md:67`) is rewritten to `AGENTS.md` in the published raw markdown; the
  bootstrap's *page* declares `…/AGENTS.md` as its alternate, via `published_name`, not a special case.
- **The README/index collision fix is real** — `README/index.html` exists *and* `index.html` is the
  kit's pitch, simultaneously. Deleting `_vacate_the_root` fails two tests.
- **The base-swap guard fires.** I hard-coded the deployed host in `main.html`, and separately in
  `site.py`'s PDF link. Both were caught by `test_swapping_the_base_moves_every_generated_address`
  *and* by the source-level host greps. This is a genuine C3/NFR-001 guard.
- **Contrast genuinely meets AA on screen, in both schemes** — measured in Chrome against computed
  styles, via Material's own toggle: light body 15.28:1, links 6.95:1, AI pointer 6.00:1; dark body
  13.84:1, links 7.19:1, AI pointer 6.52:1. The `primary: custom` fix is verified — dark links render
  `#e79a80`, not Material's `#5488e8`. The font fix is verified too: computed family is `Charter`.
- **NFR-002 holds.** All 13 pages at a 320px viewport: `scrollWidth == innerWidth`, zero overflow,
  `storytelling.md` included.
- **NFR-004 is respected** — see the closing note.

---

## Issue 1 (blocking) — the `.gitignore` regression test is vacuous

`tests/test_site.py::test_the_theme_is_not_silently_git_ignored` does not fire. I reverted `.gitignore`
to the unanchored `site/` — the exact bug it exists to catch — and it stayed **green**.

The cause is `git check-ignore`'s default behaviour: it consults the index and **says nothing about
tracked files**. Every file under `src/theme/` is now tracked, so the check is a no-op regardless of
what the pattern says.

The bug it guards is still live. With the unanchored pattern restored:

```
$ git check-ignore src/theme/site/overrides/stylesheets/newfile.css
src/theme/site/overrides/stylesheets/newfile.css          # ignored
$ git add src/theme/site/overrides/stylesheets/newfile.css
The following paths are ignored by one of your .gitignore files:
src/theme/site
```

So a *new* stylesheet or override is still silently unaddable — exactly the failure the anchor fixed —
and the test would not notice. There is a certain irony in the guard against a silent no-op being a
silent no-op.

**Fix** — add `--no-index` to the subprocess call:

```python
ignored = subprocess.run(
    ["git", "check-ignore", "--no-index", *tracked],
    ...
)
```

Verified: with `--no-index`, the reverted `.gitignore` makes the test fail and reports all three theme
files. With the anchor in place it passes. That is a guard that fires.

## Issue 2 (blocking) — the Material-upgrade canary reads the wrong stylesheet

In `test_the_palette_is_not_outranked_by_materials_own_colours`, the second assertion:

```python
assert "data-md-color-primary=custom" not in _material_stylesheet()
```

can never fail. `_material_stylesheet()` globs `main.*.min.css`, which contains **zero** occurrences of
`data-md-color-primary`. All 50 of them — including the rule this whole fix is about —

```
[data-md-color-scheme=slate][data-md-color-primary=indigo]{--md-typeset-a-color:#5488e8}
```

live in the sibling sheet, `palette.ab4e12ef.min.css`. The docstring's claim ("Verified:
`data-md-color-primary=custom` appears nowhere in its CSS") is true of Material overall but is not what
the code checks, so the canary is pointed at a file that could never carry the signal.

This matters because it is the half of the test with a shelf life. The first half — asserting
`primary: custom` in `mkdocs.yml` — **does** fire; I flipped it to `indigo` and it failed correctly. But
the day Material ships rules for `primary: custom`, the palette is silently outranked again, the
measured ratios stop describing the screen, and this test stays green. That is the same failure mode,
returning by the same door.

**Fix** — have `_material_stylesheet()` read the palette sheet as well:

```python
sheets = sorted((Path(spec.origin).parent / "templates" / "assets" / "stylesheets").glob("*.min.css"))
assert sheets, "Material's stylesheets are not where they have always been"
return "".join(sheet.read_text(encoding="utf-8") for sheet in sheets)
```

Verified: the concatenation contains `data-md-color-primary`, so the canary becomes capable of firing.
Note `test_the_font_stack_is_declared_where_material_can_see_it` also uses this helper — check the
`--md-text-font-family` regex still resolves to `body` against the concatenated text (it did when I
tried it, but please confirm rather than take my word).

## Issue 3 (non-blocking, advisory) — the table guard over-claims

`test_the_wide_tables_can_scroll_inside_themselves` asserts no `<table>` carries a class, on the stated
grounds that a classed table "starts pushing the page sideways on a phone". I tested that claim by
adding a class to `storytelling.md`'s tells table in a live 320px viewport. Containment does drop as
described — `display` goes `inline-block → table`, `overflow-x` `auto → hidden`, `max-width`
`100% → none` — but the **page still does not scroll**: at 320px the table's content wraps and fits in
286px. The failure the docstring describes does not reproduce against the real content.

So the mechanism is correctly identified but is not what is saving NFR-002 here; text wrapping is. The
test is a harmless canary, not the guard it presents itself as, and `overflow-wrap: break-word` in
`typography.css` is arguably doing the real work. No change required — but please soften the docstring
so the next reader does not over-trust it. NFR-002 itself is verified and holds.

---

## Anti-pattern checklist

| # | Item | Result |
|---|---|---|
| 1 | Dead code | **PASS** — `on_config`/`on_files`/`on_page_context`/`on_post_build` are MkDocs hook entry points, wired via `hooks:` in `mkdocs.yml` and exercised by real builds; every other symbol has a production caller. |
| 2 | Synthetic-fixture test | **PASS** for the FRs — the `site` fixture builds the real site from the real pack; deleting the implementation fails the tests. (Issues 1–2 are vacuous *guards*, not FR tests.) |
| 3 | Silent empty return | **PASS** — every `except` in `site.py` re-raises as `SiteError`/`PluginError`. No silent returns. |
| 4 | FR coverage | **PASS** — FR-001, FR-002, FR-007, FR-008 each have behavioural assertions against the built output. |
| 5 | Frozen surface | **PASS** — `git log … -- src/pack/` is empty; `git diff --stat src/pack/` is empty. |
| 6 | Locked decision | **PASS** — `--strict` intact, `extra_css` absent, CSS ships via `custom_dir`, no `index.md` in the pack, no hard-coded hostname. |
| 7 | Shared-file ownership | **PASS with note** — `mkdocs.yml` is WP02's and is depended on by WP04–WP07. The edits (`hooks`, `validation.links`, `theme.custom_dir`, `palette`, `font`, `plugins`) are explicitly sanctioned by T016. `.gitignore` is unowned; the anchor fix is justified. Flag to WP04–WP07 on rebase. |
| 8 | Production fragility | **PASS** — the new `raise`s are build-time `PluginError`s on a deterministic derivation, which is the loud failure T013/T015 asked for. No transient-race path. |

## Gates

`pytest` 139 passed · `black --check` clean · `mypy` clean · `guide roles lint` OK (12 documents) ·
`guide verify provenance --output site` OK · `mkdocs build --strict` exit 0 · `.nojekyll` present ·
no root-relative link drops the subpath (every one carries `/dungeon-masters-guide/`).

## On NFR-004 — the design budget

Asked honestly: **yes, this is Material with a good palette and good type.** It has not become a
project. `palette.css` is *two* rules — the two scheme blocks — setting nothing but Material's own
custom properties. `typography.css` is twelve: the font stacks, a measure cap, an h1–h4 scale, a
blockquote tweak, and the `.guide-ai-pointer`, which FR-002 requires and which is one line of text with
a left rule rather than a component. No JavaScript, one template override, no layout changes. The
comment-to-rule ratio is high, but the comments are load-bearing — they are where the three cascade
traps are recorded. I would not ask for a single line back.

Fix Issues 1 and 2 and this is an approve.
