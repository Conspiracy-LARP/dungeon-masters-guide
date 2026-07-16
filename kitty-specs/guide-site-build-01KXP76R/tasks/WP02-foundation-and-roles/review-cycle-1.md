# WP02 — Review cycle 1

**Verdict**: rejected — one blocking finding. Everything else passes and was independently
verified. Both deviations are **approved**. This is a tightly scoped re-work: one config
line and a `black .` run.

---

## The blocking finding — the `black` gate is vacuous over the entire authoritative surface

`poetry run black --check .` reports "5 files would be left unchanged" and exits 0. There are
**11** Python files. Black's `DEFAULT_EXCLUDES` regex contains `build`, so it silently skips
`src/build/` — the whole package, including `authoritative_surface: src/build/roles.py`.

Reproduce:

```bash
poetry run black --check . --verbose 2>&1 | grep "src/build"
# src/build ignored: matches the --exclude regular expression
```

This is not merely cosmetic. The code inside actually violates black:

```bash
for f in src/build/*.py; do poetry run black --check "$f" --force-exclude '^$' >/dev/null 2>&1 \
  || echo "WOULD REFORMAT: $f"; done
# WOULD REFORMAT: src/build/cli.py
# WOULD REFORMAT: src/build/config.py
# WOULD REFORMAT: src/build/roles.py
```

Why this blocks rather than being a nit:

1. **A declared success criterion is not met.** T005 step 4 requires `poetry run black --check .`
   to run clean, and the WP's constraints require the code follow the repo's black convention.
   The command runs clean only because the tool never looks; the code is not black-formatted.
2. **It propagates.** WP08 wires the `verify` job in CI. As configured, `black --check .` will
   pass forever in CI while checking nothing in `src/build/` — and four lanes (WP03–WP06)
   inherit this `pyproject.toml`.
3. **It is the same defect this WP correctly diagnosed elsewhere.** The headline finding of this
   WP is that `validation.nav.omitted_files` defaults to not-checking, and that
   `provenance.py`'s allow-list must never hold a wildcard, because — in the module's own words —
   a check that returns "ok" for everything "is worse than no check at all because it looks like
   one." That reasoning is right, and it applies here.

### Fix (verified)

Override black's `DEFAULT_EXCLUDES` in `pyproject.toml` so `src/build/` is not skipped:

```toml
[tool.black]
line-length = 100
target-version = ["py311"]
# Override black's DEFAULT_EXCLUDES, which contains "build" and would otherwise silently
# skip src/build/ — the authoritative surface. A formatter that skips the package it is
# meant to format is a gate that only looks like one.
exclude = "/(\\.git|\\.venv|\\.mypy_cache|\\.pytest_cache|site)/"
```

Then `poetry run black .` (reformats the 3 files; the changes are line-wraps only).

I applied exactly this in a scratch copy and confirmed:

- `black --check .` then sees **11** files, not 5;
- after `black .`, **85 tests still pass** and `mypy .` is still clean;
- the reformatting is purely cosmetic.

**Please also add a regression test** in the spirit of the ones already in this WP — e.g. assert
that `black --check` over `src/build/` is non-vacuous (that it reports ≥ 6 files), so the gate
cannot silently re-hollow. The WP already has `test_the_allow_list_does_not_swallow_the_output_root`
and `test_the_allow_list_contains_no_wildcards` doing precisely this job for provenance; this is
the same guard for the formatter.

---

## The two deviations — both APPROVED, independently reproduced

### Deviation 1 — theme hooks not pre-declared: **correct, keep it**

Both claims verified against MkDocs 1.6.1.

- **`theme.custom_dir` is validated eagerly — confirmed.** Adding
  `custom_dir: src/theme/site/overrides` (the directory does not exist; `src/theme/` holds only
  `.gitkeep`) aborts at config load:
  `ERROR - Config value 'theme': The path set in custom_dir (...) does not exist.` /
  `Aborted with a configuration error!`, exit 1. It cannot precede the directory it names, and
  it would have broken WP04/WP05/WP06, which depend on this lane.
- **`extra_css` resolves relative to `docs_dir` — confirmed.** With
  `extra_css: [stylesheets/extra.css]`, a stylesheet at `src/theme/site/overrides/stylesheets/`
  was **not** copied to the output; the same file at `src/pack/stylesheets/` **was** (appearing at
  `out/stylesheets/extra.css`). The `<link>` is emitted either way, so declaring it without
  writing into `src/pack/` yields a silent 404. Requiring build assets in `src/pack/` does violate
  C-002/C-006.

Two places the rationale is slightly overstated — worth correcting in the contract, but they do
not change the conclusion, and I am not blocking on them:

- `extra_css` naming a missing file does **not** abort the build (exit 0, silently broken link).
  The "aborts every build" argument is true of `custom_dir` only.
- "failing the role lint as an undeclared document" is **not** what would happen: `_pack_files`
  globs `*.md` only, so a `.css` under `src/pack/` sails through the lint untouched. That makes
  the C-002/C-006 argument *stronger*, not weaker — nothing would catch it.

The `mkdocs.yml` comment block handing WP03 the `custom_dir` route is good work and should stay.

### Deviation 2 — `validation.nav.omitted_files: warn`: **correct, a genuine strengthening of FR-011**

Reproduced exactly as reported, on MkDocs 1.6.1, with the real pack plus one undeclared
`sneaky-new-doc.md`:

| config | result |
|---|---|
| **with** `validation.nav.omitted_files: warn` (as shipped) | `Aborted with 1 warnings in strict mode!` — **exit 1** |
| **without** it (the original subtask's config) | `INFO - The following pages exist in the docs directory, but are not included in the "nav" configuration: - sneaky-new-doc.md` — **exit 0** |

The finding is correct and material: without this key, FR-011 would have had no teeth in the
build, and anyone running `mkdocs serve` would have seen nothing. Catching this against a real
build rather than accepting the spec's claim is exactly right, and updating
`contracts/roles-declaration.md` with the correction was the right follow-through.

---

## Everything else — verified, passing

| Check | Result |
|---|---|
| `poetry install`, `poetry run pytest` | 85 passed |
| `poetry run mypy .` (strict) | clean, 11 files — `files=` is explicit, so no exclusion problem |
| `poetry run guide roles lint` (real pack) | `OK: 12 documents, all declared (10 chapters, 2 not in the book)`, exit 0 |
| `poetry run guide roles check-drift` (real pack) | `OK: the prose lists agree with the declaration`, exit 0 |
| **Exactly one chapter list** | Yes. `story-continuity-checker-prompt.md` appears nowhere in `src/build/`; guarded by `test_the_reading_order_is_declared_exactly_once`. |
| **`getting-started.md` survives the rename** | Yes. `(?<![\w\-])start\.md(?!\w)(?!\.\w)`. Verified both halves of the lookahead: `start.md.bak` is **not** rewritten, `read start.md.` **is**. `test_real_bootstrap_text_shape_is_rewritten_safely` mirrors the live 3-reference case in `src/pack/start.md`. Also covers `restart.md`, `quickstart.md`, `jumpstart.md`, `start.markdown`, and idempotency. |
| **Role lint FAILS on all three modes** | Verified by direct experiment against a mutated copy of the real pack: in neither list → `RoleError` naming `sneaky.md`; in both → `RoleError` naming `ethics.md`; declaration naming a missing file → `RoleError` naming `ghost.md`. All name the file with an actionable message; CLI exits 1. The bonus `not_in_nav` vs `not_in_book` agreement check is a good call. |
| **T045 provenance is not vacuous** | Verified by experiment: planted `about-us.html` and `marketing/promo.html` in an output dir → both reported, **exit 1**. Allow-list is 9 explicit filenames + 3 explicit directory prefixes, no wildcards, and guarded by three tests (`..._contains_no_wildcards`, `..._stays_small`, `..._does_not_swallow_the_output_root`). |
| **No hard-coded hostname** | Only `config.py` names the host, as `DEFAULT_BASE_URL`. Enforced by `test_no_module_hard_codes_a_hostname`. `absolute_url()` rejects both full URLs and root-relative paths, and `load_config` rejects a `site_url` without a trailing slash — good, that turns C-003 into a failure rather than a subtle wrong join. |
| **`git diff --stat src/pack/` empty** | Empty, and `git status --porcelain src/pack/` is clean. `test_drift_check_writes_nothing_to_the_pack` asserts it by bytes. |
| **T011 strictness as specified** | Implemented exactly: `drift_is_fatal` is `True` for `main` only; `main` → exit 1, feature branch → exit 0 with `WILL fail on main`. Both directions tested via injected findings, since the real pack has no drift. Not re-litigated. |

`tests/__init__.py` outside `owned_files`: **acceptable.** One line, inside the lane's `tests/`
scope, required by `pythonpath = ["src", "."]` for `tests` to import as a package. Not a finding.

The quality of this work is high — the reasoning in the docstrings, the two findings raised
against real builds rather than assumed, and the tests that guard the guards are all well above
bar. The single blocking item is a small one, and the fix above is verified end to end.
