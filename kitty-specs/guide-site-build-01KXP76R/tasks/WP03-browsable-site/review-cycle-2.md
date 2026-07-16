---
affected_files: []
cycle_number: 2
mission_slug: guide-site-build-01KXP76R
reproduction_command:
reviewed_at: '2026-07-16T23:05:00Z'
reviewer_agent: reviewer-renata
verdict: approved
work_package_id: WP03
---

# WP03 review — cycle 2

**Verdict: approved.** Both cycle-1 findings are fixed, and I watched each guard go red myself. The
diff is `tests/test_site.py` and nothing else; the product cycle 1 approved is untouched.

The bar I set for myself: this mission has now found the same defect seven times — a check that
reports success without looking. So a *fixed* guard is not approved on a report that it fires. It is
approved when I have broken the thing it guards and seen the failure with my own eyes. Both were.

## Issue 1 (was blocking) — the `.gitignore` guard now fires

`--no-index` is in place. Reproduced, in full:

- Baseline, anchored `/site/`: **green**.
- Reverted `.gitignore` to the unanchored `site/` — the exact bug: **red**, naming all three files.
  ```
  AssertionError: git ignores part of the theme, so it cannot be committed and the site will
  build without it:
    src/theme/site/overrides/main.html
    src/theme/site/overrides/stylesheets/typography.css
    src/theme/site/overrides/stylesheets/palette.css
  ```
- Restored the anchor: **green**. Working tree clean.

I also ran the two code paths side by side against the tracked theme files, with the unanchored
pattern in place — this is the whole finding in four lines:

```
$ git check-ignore <three theme files>              # the OLD call
$ echo $?
1                                                    # nothing ignored → old test GREEN on the bug
$ git check-ignore --no-index <three theme files>    # the NEW call
src/theme/site/overrides/main.html
src/theme/site/overrides/stylesheets/palette.css
src/theme/site/overrides/stylesheets/typography.css  # → new test RED on the bug
```

And the underlying bug is still live under the unanchored pattern, which is why the anchor matters:

```
$ git check-ignore -v src/theme/site/overrides/stylesheets/reviewer-probe.css
.gitignore:9:site/	src/theme/site/overrides/stylesheets/reviewer-probe.css
$ git add src/theme/site/overrides/stylesheets/reviewer-probe.css
The following paths are ignored by one of your .gitignore files:
src/theme/site
$ echo $?
1
```

A new override added tomorrow is still silently unaddable. The existing files being tracked does
nothing for the next contributor — which is precisely what `--no-index` now asks about.

## Issue 2 (was blocking) — the Material canary now fires

The helper globs `*.min.css` and concatenates. The haystack claim checks out exactly as reported:

| haystack | `data-md-color-primary` occurrences |
|---|---|
| `main.*.min.css` (the OLD glob) | **0** |
| `*.min.css` concatenated (the fix) | **50** |

So the old assertion searched a haystack in which the needle could not exist. Mutation, simulating the
future Material upgrade this canary exists for — appending to `palette.ab4e12ef.min.css`:

```
[data-md-color-scheme=slate][data-md-color-primary=custom]{--md-typeset-a-color:#5488e8}
```

**Red**, with the right message: *"Material now ships rules for `primary: custom`, which may outrank
palette.css. Re-check the rendered colours in a browser."* Restored the sheet: **green**.

The config half fires independently: flipping `primary: custom` → `indigo` in `mkdocs.yml` fails on
the `'default'` scheme. Both halves have teeth.

## Issue 3 (was advisory) — the table guard

Addressed, and addressed better than I asked. I suggested softening the docstring; they also
**renamed** the test to `test_no_table_opts_out_of_materials_containment`, on the reasoning that the
old name (`test_the_wide_tables_can_scroll_inside_themselves`) made the same over-claim as the
docstring and would outlive it. That is right — the name is the part that gets read.

Judged against the ask: the docstring now describes what the test actually pins (no table carries a
class, so none falls out of Material's `:not([class])` containment), and explicitly disclaims being
the NFR-002 guard — it records that the page does not scroll at 320px even with containment dropped,
that `overflow-wrap: break-word` does the real work on today's content, and it points the reader to
where NFR-002 *is* verified. No over-claim survives.

## The font test — premise checked, not assumed

Reported: `main.*` sorts before `palette.*`, so the first match is still Material's. True, but the
test is safe for a stronger reason than sort order: `palette.*.min.css` contains **zero** occurrences
of `--md-text-font-family` (all 5 are in `main`). The glob change cannot affect this test at all,
whatever the ordering. First match in the concatenation resolves to `'body'`, at offset 3286 — inside
`main`. Green.

## Mutation hygiene

I mutated `.venv` Material CSS, `mkdocs.yml` and `.gitignore` during this review, and restored all
three. I did not verify the `.venv` restore against my own backup — my backup was taken after the
implementer's session, so it would have preserved any mutation they left. Checked against the
pristine wheel instead (`mkdocs_material-9.7.6-py3-none-any.whl`, from the Poetry artifact cache):

```
main.484c7ddc.min.css     wheel=484c7ddccf764ac5  installed=484c7ddccf764ac5  MATCH
palette.ab4e12ef.min.css  wheel=ab4e12ef511f9c36  installed=ab4e12ef511f9c36  MATCH
```

Byte-identical. Nothing survives in `.venv` from either session. Working tree carries only untracked
`.spec-kitty/`; commit `498bee7` touches `tests/test_site.py` and nothing else; `git diff --stat
src/pack/` against the mission base is empty.

## Gates

`pytest` **139 passed** · `black --check` clean (14 files) · `mypy` clean (14 source files) ·
`mkdocs build --strict` exit 0.

## Note on the artifact

`review-cycle-1.md` shipped without its YAML frontmatter, so the verdict was unparseable and the
state gate refused to act on it. I added it, recording cycle 1's actual verdict (`rejected` — the
document says "changes requested" in its first line). Content unchanged. Worth noticing that this is
the same shape as the finding itself: a record that reads as authoritative while carrying nothing a
machine could check.
