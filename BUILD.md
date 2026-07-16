# BUILD — handoff prompt: compile this pack into a website

*This file is a task brief for an LLM/agent taking over the site build. It is **not** part of the
creator-facing manifesto — it's build scaffolding (out-of-world). The markdown documents in this folder
are the product; your job is to render them, never to rewrite them.*

---

## Goal

Turn the markdown documents in this repository into three outputs, **all compiled from the same markdown
so they never drift**:

1. **A browsable human website** — a readable, navigable "Dungeon Master's Guide."
2. **A single-file "book" edition** — the whole guide as one typeset document (HTML + PDF), for reading
   cover to cover.
3. **An LLM-friendly source** — the raw markdown, surfaced so an AI handed the site URL is pointed
   straight at it.

## Framing — it's a Dungeon Master's Guide

This site is the project's **out-of-world** layer: unlike the fictional "nodes" the pack teaches people to
build, the guide itself is openly and unashamedly a manual. No diegetic costume, no period disguise. The
spirit to aim for is Gary Gygax's *AD&D 2nd-edition Dungeon Master's Guide*: it taught someone who had
never refereed a game the **principles** of running a good one, not merely the rules. You may give the
site a tasteful "referee's manual" aesthetic as an homage, but readability comes first.

## Hard requirement — single source of truth

- The `.md` files in this folder are **canonical**. Do not hand-write HTML and do not fork the content.
- The site is **generated** from the markdown by a build step, and **auto-rebuilds on every push** (CI or
  the host's own build), so the web, book, and LLM outputs are always the same bytes rendered three ways.
- If you need per-page metadata (nav order, titles), prefer a small config/front-matter approach over
  editing prose.

## Output 1 — the browsable site

- Suggested tool: **MkDocs + Material** (Python, fits the stack; built-in search, nav, and a "view/edit
  source" link per page). **Astro Starlight** is a fine, more polished alternative if you prefer.
- Landing page: the "What is this?" pitch from `creator-kit.md`.
- Left-nav / reading order (mirror `README.md` and the kit's companion map):
  1. `creator-kit.md` (the hub / quick read)
  2. `storytelling.md`
  3. `philosophy.md`
  4. `improvisation.md`
  5. `ethics.md`
  6. `communications.md`
  7. `worked-example.md`
  8. `technical-suggestions.md`
  9. `story-continuity-checker-prompt.md`
- Every page carries a visible **"🤖 Reading this as an AI? The clean markdown source is here →"** link to
  its own `.md`, plus a `<link rel="alternate" type="text/markdown" href="…">` in the head.

## Output 2 — the "book" edition

- Compile all documents, in the reading order above, into **one long typeset page** and a **PDF** (pandoc
  is the natural tool). This is the cover-to-cover Gygax read.

## Output 3 — the LLM source

- Generate **`llms-full.txt`** (the entire pack concatenated into one markdown file, in reading order) and
  a short **`llms.txt`** index of links, per the [llmstxt.org](https://llmstxt.org) convention.
- Serve each raw `.md` at a parallel URL (e.g. `/creator-kit.md`) so any page's source is one fetch away.

## Hosting

- Static output, deployed to **Cloudflare Pages** or **Fly** (cheap; auto-rebuild on push). This eats our
  own dog food — see `technical-suggestions.md`.

## Definition of done

- [ ] Browsable site builds from the markdown, with search, nav in reading order, and per-page raw-markdown links.
- [ ] Single-file HTML "book" + PDF generated from the same markdown.
- [ ] `llms.txt` + `llms-full.txt` generated; raw `.md` served at parallel URLs; AI pointer on every page.
- [ ] CI/host rebuilds and redeploys on every push (verified).
- [ ] Zero hand-authored content — everything traces back to a `.md` file in this folder.
