# Phase 1 — Data Model

**Mission**: `guide-site-build-01KXP76R`

There is no database and no runtime state (C-004). The "data model" here is the small set of entities the
build reasons about, and — more importantly — the **invariants** that must hold over them. Those
invariants are the design; everything else is derivation.

---

## Entities

### Document

One markdown file in `src/pack/`.

| Field | Type | Source | Notes |
|---|---|---|---|
| `filename` | string | filesystem | e.g. `ethics.md`. Flat — never contains a path separator (C-001) |
| `role` | enum: `chapter` \| `not_in_book` | the nav declaration | **Required.** Absent → build fails (FR-011) |
| `position` | int \| null | order within nav | Set for `chapter`; null for `not_in_book` |
| `title` | string | nav declaration, else first H1 | Used in site nav, book ToC, `llms.txt` |
| `published_name` | string | derived | Same as `filename` on `main`; `start.md` becomes `AGENTS.md` on the pack branch (FR-010) |

**Validation rules**

- Every `.md` in `src/pack/` resolves to exactly one `role`. Neither → error (FR-011, mitigates R-003).
- `chapter` documents have contiguous positions starting at 1.
- `not_in_book` is currently exactly `{README.md, start.md}`; the set is declared, not inferred.
- `filename` contains no `/`. A pack that is not flat is a build failure (C-001).

### Reading order

The ordered sequence of `chapter` documents. **Declared once**, in the site config's `nav:` (R5).
Not an entity the build stores — an entity it *reads*, and from which the book, `llms-full.txt`, and
`llms.txt` all derive. Its authority is the point: the order cannot disagree with itself.

### Cross-reference

A relative markdown link from one Document to another.

| Field | Type | Notes |
|---|---|---|
| `source` | Document | where the link is written |
| `target` | string | a bare filename — `ethics.md`, never `src/pack/ethics.md` |
| `context` | enum: `prose` \| `code_example` | links inside backticks/fences are illustrative, not real |

**Validation rules — the load-bearing invariant (C-001, FR-013)**

1. `target` contains no path separator.
2. `target` resolves on `main`, where the bootstrap is `start.md`.
3. `target` resolves on the pack branch, where it is `AGENTS.md`.

Rule 3 is not redundant with rule 2. They have already disagreed once in this project's history: a
`README.md` link to `AGENTS.md` resolved on the pack branch and 404'd on `main`. The checker must
evaluate both branches, and must exclude `context: code_example` — the guide *documents* the link
convention using inline code, and those samples are not links to follow.

### Surface

A published rendering. Not stored; enumerated here because "no two surfaces may disagree" (SC-004) is
only meaningful against a closed list.

| Surface | Derived from | Contract |
|---|---|---|
| Site pages | all Documents | `contracts/url-map.md` |
| Book (single-file HTML + PDF) | `chapter` Documents, in order | `contracts/url-map.md` |
| `llms.txt` | roles + order + base URL | `contracts/llms-txt.md` |
| `llms-full.txt` | `chapter` Documents, in order | `contracts/url-map.md` |
| Raw markdown | all Documents, byte-identical | `contracts/url-map.md` |
| Pack branch | all Documents, renamed + rewritten | `contracts/pack-branch.md` |

**Invariant**: every Surface derives from `src/pack/`. No Surface has hand-authored content (NFR-003).
This is what makes SC-004 ("no two surfaces can disagree") true by construction rather than by vigilance.

### Base URL

One configured value (NFR-001). Every absolute address in every Surface derives from it.

- Today: `https://conspiracy-larp.github.io/dungeon-masters-guide/` — note the subpath (C-003).
- Changing it to a custom domain must be a one-value edit, verified by editing it and rebuilding (SC-006).
- **No component may hard-code a hostname.** That is the whole mechanism by which C-003 stays reversible.

---

## State transitions

The only lifecycle is the publication pipeline, and it is strictly one-way:

```
source change on main
      │
      ▼
  roles resolved ──── unresolved role ──► BUILD FAILS (FR-011)
      │
      ▼
  links checked ───── path in a link, or ──► BUILD FAILS (C-001, FR-013)
      │               unresolved on either branch
      ▼
  surfaces generated
      │
      ├──► Pages deployment (site, book, PDF, llms.*, raw .md)
      └──► pack branch force-pushed (orphan mirror)
      │
      ▼
  live within 5 minutes (NFR-005)
```

**Atomicity note**: the two publication targets are *not* atomic with respect to each other — Pages and
the pack branch are separate operations. A creator could fetch the branch in the seconds between them.
This is acceptable: both derive from the same commit, so the worst case is a consumer briefly holding the
previous tip. It is recorded rather than solved, because solving it would require coordination the
project's stateless-static constraint (C-004) forbids.

**Failure semantics**: a lint failure must block **both** targets. Publishing a valid site alongside a
broken branch, or vice versa, is worse than publishing neither — it is precisely how a surface starts
disagreeing with the guide's own text (R-002).
