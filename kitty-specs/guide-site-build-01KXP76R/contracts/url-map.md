# Contract — the published URL map

**Mission**: `guide-site-build-01KXP76R` · Serves FR-001..FR-008, NFR-001, C-003

Every address derives from one configured **base** (NFR-001). Today:
`https://conspiracy-larp.github.io/dungeon-masters-guide/` — a project site on a **subpath**, not a
domain root. `{base}` below stands for that value. No component may hard-code a hostname.

## The contract

| Address | Content | Audience | Requirement |
|---|---|---|---|
| `{base}` | Landing page — the kit's "What is this?" pitch | humans | FR-001 |
| `{base}<chapter>/` | One chapter as a page, nav in reading order, searchable | humans | FR-001 |
| `{base}AGENTS.md` | **The bootstrap.** Self-contained; the one address handed to a model | machines | FR-008 |
| `{base}llms.txt` | Index; bootstrap is the first and most prominent entry | machines | FR-005 |
| `{base}llms-full.txt` | Every chapter concatenated, reading order | machines | FR-006 |
| `{base}<doc>.md` | Raw markdown, byte-identical to source, for every document | machines | FR-007 |
| `{base}dungeon-masters-guide.pdf` | The printable book, linked prominently from the site | humans | FR-004 |
| `{base}.nojekyll` | Present (empty) — stops Jekyll processing the output | — | FR-012 |

## Conditions the contract depends on

**C1 — `.md` must be served as readable text.** Not a download, not converted to HTML. This is the
condition the whole machine column rests on, it is decided by the host rather than by us, and its
failure is invisible from the site.

> **CONFIRMED 2026-07-16 by WP01** against the real deployment. GitHub Pages serves `.md` from the
> project-site subpath as **`content-type: text/markdown; charset=utf-8`**, with **no
> `Content-Disposition`**, body delivered as markdown **source**. A plain GET returns readable text.
> **The map above stands unchanged; no fallback is adopted and the Amendment rule is not triggered.**
> Verbatim headers and reasoning: `spike/FINDINGS.md`. Risk R-001 does not materialise.
>
> Two notes for downstream work:
> - **`.txt` twins are a proven escape hatch** (`text/plain; charset=utf-8`) if GitHub ever remaps `.md`.
>   **Extensionless twins are not** — they serve as `application/octet-stream`, i.e. worse than the
>   problem they would solve. Strike them from the fallback order in R3.
> - The content-type is the host's choice and is **not pinned by anything in this repo**. This is a
>   snapshot, not a guarantee; if it ever changes, the machine column fails silently while the site looks
>   perfect.

**C2 — the subpath is real.** `{base}` ends in `/dungeon-masters-guide/`. Every generated link —
`llms.txt` entries, per-page raw-markdown pointers, the PDF link — must be subpath-correct. Root-relative
links (`/AGENTS.md`) are wrong here and will 404.

**C3 — one base, one edit.** Adding a custom domain later changes `{base}` and nothing else (SC-006).

## Amendment rule

If IC-01 finds C1 does not hold, this contract changes — probably by adding extensionless or `.txt`
twins and repointing `llms.txt` at them. **That would also change the guide's own published text**,
because `src/pack/start.md`, `README.md` and `technical-suggestions.md` all quote addresses and commands
to readers. Amending this contract is therefore never a build-only change; it is a content change too,
and content is Out of Scope for this mission (C-006). Escalate rather than quietly edit the pack.
