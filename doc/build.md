# BUILD — handoff prompt: compile this pack into a website

*This file is a task brief for an LLM/agent taking over the site build. It is **not** part of the
creator-facing manifesto — it's build scaffolding (out-of-world), which is why it lives in `doc/`. The
markdown documents in `src/pack/` are the product; your job is to render them, never to rewrite them.*

---

## Goal

Turn the markdown documents in `src/pack/` into four outputs, **all compiled from the same markdown so
they never drift**:

1. **A browsable human website** — a readable, navigable, genuinely attractive "Dungeon Master's Guide."
2. **A single-file "book" edition** — the whole guide as one typeset document (HTML + PDF), for people
   who print things out and read them cover to cover. The PDF is a first-class output, not an
   afterthought: it must be typeset, paginated, and pleasant on paper.
3. **An LLM-friendly source** — the raw markdown, surfaced so an AI handed the site URL is pointed
   straight at it.
4. **The `pack` branch** — the markdown alone, for creators to add as a git submodule.

And, cutting across all four, **the one URL**:

> **`/AGENTS.md` must be a complete, self-contained bootstrap.** A creator should be able to say to any
> LLM — with no other context, no repo checked out, nothing — *"read https://<domain>/AGENTS.md and do
> what it says,"* and the model should scaffold their directory structure, add the kit as a submodule,
> and open the interview. This is the project's front door for machines, and it is the single most
> load-bearing URL on the site. It is `src/pack/start.md`, published under its conventional name.
>
> **Its acceptance test is behavioural, not structural:** take a fresh LLM session, give it nothing but
> that URL, and see whether a correct `my-node/` appears with the kit in `doc/core/` and the identity
> firewall asked about *first*. If it doesn't, the build isn't done — no matter how well the site
> renders.

## Framing — it's a Dungeon Master's Guide

This site is the project's **out-of-world** layer: unlike the fictional "nodes" the pack teaches people to
build, the guide itself is openly and unashamedly a manual. No diegetic costume, no period disguise. The
spirit to aim for is Gary Gygax's *AD&D 2nd-edition Dungeon Master's Guide*: it taught someone who had
never refereed a game the **principles** of running a good one, not merely the rules. You may give the
site a tasteful "referee's manual" aesthetic as an homage, but readability comes first.

## Hard requirement — single source of truth

- The `.md` files in `src/pack/` are **canonical**. Do not hand-write HTML and do not fork the content.
  `src/pack/` contains the guide and nothing else, which makes that rule mechanically checkable: nothing
  outside it reaches any output, and every file inside it has a declared role (see "Which documents are
  chapters").
- The site is **generated** from the markdown by a build step, and **auto-rebuilds on every push** (CI or
  the host's own build), so the web, book, LLM, and submodule outputs are always the same bytes rendered
  four ways.
- If you need per-page metadata (nav order, titles), prefer a small config/front-matter approach over
  editing prose.

## Output 1 — the browsable site

- Suggested tool: **MkDocs + Material** (Python, fits the stack; built-in search, nav, and a "view/edit
  source" link per page). **Astro Starlight** is a fine, more polished alternative if you prefer.
- Landing page: the "What is this?" pitch from `creator-kit.md`.
- Left-nav / reading order (mirror `src/pack/README.md` and the kit's companion map):
  1. `creator-kit.md` (the introduction / hub — the quick read)
  2. `premise.md` (the world itself — added 2026-07-17)
  3. `getting-started.md`
  3. `storytelling.md`
  4. `philosophy.md`
  5. `improvisation.md`
  6. `ethics.md`
  7. `communications.md`
  8. `worked-example.md`
  9. `technical-suggestions.md`
  10. `story-continuity-checker-prompt.md`
- Every page carries a visible **"🤖 Reading this as an AI? The clean markdown source is here →"** link to
  its own `.md`, plus a `<link rel="alternate" type="text/markdown" href="…">` in the head.

### Which documents are chapters

`src/pack/` contains the guide and nothing else, but not every file is a *chapter*:

- **Chapters** — the eleven documents in the reading order above, in that order.
- **Not chapters, still published** — `README.md` (the pack's own index; the front door of the `pack`
  branch) and `start.md` (the machine bootstrap, published as `/AGENTS.md`). Both ship as pages and raw
  markdown; neither belongs in the printed book's flow.

Lint this rather than trusting it: every `.md` in `src/pack/` must be either a chapter or on the short
not-a-chapter list. A new document that is silently neither is the failure mode.

## Output 2 — the "book" edition

- Compile all chapters, in the reading order above, into **one long typeset page** and a **PDF** (pandoc
  is the natural tool). This is the cover-to-cover Gygax read.
- The PDF is for **printing**: real pagination, a title page, a table of contents with page numbers,
  readable body type at A4/Letter, and no hyperlink-dependent constructions (a reader on paper cannot
  click "see `ethics.md`"). Cross-references should resolve to something a printed page can follow.
- Link it prominently from the site; a reader who wants the book should not have to hunt.

## Output 3 — the LLM source

- Generate **`llms-full.txt`** (the entire pack concatenated into one markdown file, in reading order) and
  a short **`llms.txt`** index of links, per the [llmstxt.org](https://llmstxt.org) convention.
- Serve each raw `.md` at a parallel URL (e.g. `/creator-kit.md`) so any page's source is one fetch away.

## Hosting

The whole guide is **stateless static content** — no server, no database, nothing to keep alive.

- **GitHub Pages** is the default: the source already lives there, it's free, and it rebuilds on push
  with no extra infrastructure. **Fly** is the alternative if we ever outgrow it (we won't; it's a book).
- **No custom domain yet.** Publish on the platform's own hostname — for Pages that means
  `https://conspiracy-larp.github.io/dungeon-masters-guide/`. A domain can be bolted on later without
  touching the build, *provided* you don't hard-code the hostname anywhere; generate absolute URLs from
  one configured base so switching later is a one-line change.
- Two Pages-specific gotchas, both of which break requirements if missed:
  1. **Add `.nojekyll`.** Otherwise Jekyll processes the site and can mangle or hide files.
  2. **It's a project site, served from a subpath** (`/dungeon-masters-guide/`), not the domain root. So
     the one URL is `…github.io/dungeon-masters-guide/AGENTS.md`. Every generated link — `llms.txt`
     entries, the raw-markdown pointers — must be subpath-correct, and `.md` must be served as text a
     model can read rather than downloaded or rendered as HTML.

This eats our own dog food — see `technical-suggestions.md`, which tells creators to do the same.

## Output 4 — the `pack` branch (the submodule payload)

Creators consume the guide by adding it as a **git submodule on their own desk** (`doc/core/`), and they
want the markdown *only* — not the build machinery, not `doc/`. A submodule can't take a subdirectory, so
CI must publish one:

- On every push to the default branch, mirror the **contents of `src/pack/`** to a `pack` branch — flat,
  markdown only, no `src/`, no `doc/`, no build files. A `git subtree split --prefix=src/pack` (or an
  equivalent orphan-branch job) is the natural tool.
- **Rename `start.md` → `AGENTS.md` on the branch, and rewrite references to it.** That is the
  convention models look for, so it must be the name at the branch root and therefore at
  `doc/core/AGENTS.md` in a creator's project. It is deliberately *not* called `AGENTS.md` in this repo:
  nested agent-files auto-load, and a document whose first instruction is `mkdir -p my-node/...` must
  never load into a contributor editing the guide.
  The rename is a two-part job — get both, or you ship broken links:
  1. `git mv start.md AGENTS.md` on the branch.
  2. Rewrite `start.md` → `AGENTS.md` in link targets and inline references across the branch's markdown
     (today: `README.md`). The invariant to preserve is that **links resolve on every branch** — they
     say `start.md` on `main`, where that file exists, and `AGENTS.md` on `pack`, where it exists.
     A link-check on both branches is the test.
- Consumers then run `git submodule add -b pack <repo> doc/core`, giving them `doc/core/creator-kit.md`
  and friends. The pack's own `README.md` is the front door of that branch, so it must stand alone —
  never reference `doc/`, `src/`, or anything that isn't on the branch.
- The cross-links between pack documents are bare sibling links (`[ethics.md](ethics.md)`). They resolve
  on the `pack` branch, on GitHub, and in the built site alike. **Don't introduce paths into them** — it
  is the one property that lets the same bytes serve all four outputs.

---

## The URL map

What must exist, once deployed:

| URL | What | For |
|---|---|---|
| `/` | the site landing (the kit's "What is this?" pitch) | humans |
| `/<doc>/` | each chapter as a page | humans |
| `/AGENTS.md` | **the bootstrap** — the one URL you hand an LLM | machines |
| `/llms.txt` | index of links, per llmstxt.org; links `/AGENTS.md` first | machines |
| `/llms-full.txt` | the whole pack concatenated in reading order | machines |
| `/<doc>.md` | raw markdown for every document | machines |
| `/dungeon-masters-guide.pdf` | the printable book | humans |
| the `pack` branch | flat markdown, `start.md` renamed to `AGENTS.md` | creators' submodules |

`/llms.txt` should open by pointing at `/AGENTS.md` — an LLM that lands on the index should be told
immediately that there is a procedure it can follow, not just a pile of documents it can read.

---

## Definition of done

Structural:

- [ ] Browsable site builds from the markdown, with search, nav in reading order, and per-page raw-markdown links.
- [ ] Single-file HTML "book" + a **printable** PDF (title page, ToC with page numbers, real pagination)
      generated from the same markdown, and linked prominently from the site.
- [ ] `llms.txt` + `llms-full.txt` generated; raw `.md` served at parallel URLs; AI pointer on every page.
- [ ] `/AGENTS.md` served, and `/llms.txt` points at it first.
- [ ] The `pack` branch is published by CI: flat markdown only, `start.md` renamed to `AGENTS.md`.
- [ ] Every `.md` in `src/pack/` is either a chapter or on the not-a-chapter list — linted, not assumed.
- [ ] CI/host rebuilds and redeploys on every push (verified).
- [ ] Zero hand-authored content — everything traces back to a `.md` file in `src/pack/`.

Behavioural — the tests that actually matter:

- [ ] **The bootstrap works cold.** A fresh LLM session, given nothing but `https://<domain>/AGENTS.md`,
      produces a correct `my-node/` with the kit at `doc/core/`, and asks about the identity firewall
      *before* writing anything. Run this for real against a real model; it is the point of the project's
      machine-facing surface.
- [ ] **The submodule command in the guide actually runs.** `git submodule add -b pack <repo> doc/core`
      succeeds against the published branch. Until CI publishes `pack`, the instructions in
      `start.md`, `README.md`, and `technical-suggestions.md` describe something that does not exist.
- [ ] **The PDF is readable on paper** — printed, not just previewed.
