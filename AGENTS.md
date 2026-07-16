# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This repo is the **source text of a manual** — the "Dungeon Master's Guide" to a distributed,
permissionless alternate reality game of diegetic conspiracy satire. The markdown documents in
`src/pack/` *are* the product; everything else exists only to render them.

```
src/pack/     THE GUIDE — canonical markdown, flat, nothing else
src/build/    the machinery: site, book, llms.txt
src/theme/    styling
doc/          documentation about the guide (build brief, prompts) — never shipped
CLAUDE.md     this file; AGENTS.md symlinks to it
```

**`src/pack/` is flat on purpose, and must stay flat.** Every cross-link between pack documents is a
bare sibling link (`[ethics.md](ethics.md)`) — around forty of them. That single property is what lets
the same bytes serve the website, the book, the `pack` branch, and GitHub's own rendering without a
rewrite step. Introducing a subdirectory, or a path into a link, breaks all four at once.

Two audiences read this pack, and both matter when editing:

1. **Creators** — people deciding whether and how to join, reading it cover to cover.
2. **LLMs** — a creator pastes `creator-kit.md` into a fresh Claude Code/Codex session and says "let's
   begin," and the model does almost all of the building. Much of the prose is written to be *executed*
   by a model, not merely understood. `story-continuity-checker-prompt.md` is literally a prompt.

Write for both at once. That dual audience is why the tone is discursive rather than terse: it is
persuading a person and briefing a machine in the same paragraph.

## The distinction that governs everything: the membrane

Every artifact in this world falls on one side of a **membrane** (`creator-kit.md` §8):

- **In-world (diegetic)** — the fake intranets, filings, and character blogs a creator builds. The
  audience is meant to encounter these as real. They never break character, carry no "this is satire"
  label, and are salted with deliberate absurdist *tells* (`storytelling.md`).
- **Out-of-world (scaffolding)** — the editor's desk, not the stage. Build systems, deploy configs,
  private lore — **and this entire repository.**

**Everything in this repo is out-of-world.** These documents explain the joke, so by their nature they
shatter the illusion. Never copy this content, or anything that explains the premise, into a
client-facing artifact. If a visitor to a finished node can reach the manifesto, the joke is over.

The corollary for the site build: the guide's own website is openly and unashamedly a manual — no
diegetic costume. It is the one surface in the whole project that is allowed to explain itself.

## Three agent-facing files, two different jobs

Easy to conflate, so keep them straight:

- **`CLAUDE.md`**, with **`AGENTS.md` as a symlink to it** — this file, at the repo root. Instructions
  for an agent *editing the guide* (Claude Code reads `CLAUDE.md`, Codex reads `AGENTS.md`; the symlink
  keeps them identical rather than drifting). Not part of the pack, not in the site build.
- **`src/pack/start.md`** — pack *content*, and the project's machine-facing front door. Instructions
  for an agent *helping a creator build a node*: scaffold the workspace, add the kit as a submodule, run
  the interview. CI publishes it as **`AGENTS.md`** on the `pack` branch and at `/AGENTS.md` on the site,
  because that is the name models look for. It is deliberately not called `AGENTS.md` *here*: nested
  agent-files auto-load, and its first instruction is `mkdir -p my-node/...` — which must never fire at
  a contributor editing the guide. Don't rename it in place.

## The submodule contract

Creators consume the guide as a git submodule at **`doc/core/`** in their own private project, tracking
the **`pack` branch** — a CI-published mirror of `src/pack/`, flat markdown only, no build machinery and
no meta-docs (a submodule can't take a subdirectory, hence the branch). See `doc/build.md`.

Two things follow, and both are easy to break:

- **`src/pack/README.md` is the front door of the `pack` branch.** It must stand alone: never reference
  `doc/`, `src/`, or anything that won't exist on that branch.
- **Keep pack prose path-agnostic.** Documents say "the kit", not "`core/`", so the text doesn't lie when
  someone checks it out somewhere else. `technical-suggestions.md` § "A suggested project layout" is the
  one place that shows real paths.

Also: **nothing here is enforced on anyone.** There is no canon-keeper, no gate. Documents are phrased as
"shared references you follow as much as you personally want to." Preserve that register — an edit that
turns a suggestion into a rule contradicts the project's founding premise (`creator-kit.md` §1).

## The hub-and-spoke rule: one kit section per companion file

`creator-kit.md` is the hub — the "quick read" that summarises each theme in a paragraph or two and then
delegates to a companion document that expands it. **The invariant: each companion file is pointed at by
exactly one kit section.** Two sections delegating to the same file means the kit is repeating itself,
and the fix is to merge those sections, not to add a third pointer. Current mapping:

| Kit section | Companion |
|---|---|
| §0 The mission | `philosophy.md` |
| §2 Why now — the LLM does the building | `technical-suggestions.md` |
| §3 Getting started | `getting-started.md` |
| §4 The engine — "yes, and" | `improvisation.md` |
| §6 How we tell it | `storytelling.md` |
| §7 Ethics | `ethics.md` |
| §9 Build your node | `worked-example.md` |
| §10 How we communicate | `communications.md` |
| §12 The LLM as co-author | `story-continuity-checker-prompt.md` |

§§1, 5, 8, 11, 13 are kit-native — no companion, full text lives in the kit.

The kit's own §6 is the one that fought this hardest: the realism engine, "show, don't tell," and the
plausible-deniability tells were three separate sections all delegating to `storytelling.md`. They are
now one. Keep it that way.

If you expand a theme in a companion, check that the kit's one-paragraph summary still tells the truth.

### The same map is duplicated in four places

The list of documents and what each is for appears, in different words and different orders, in:

| Location | Purpose of its list |
|---|---|
| `src/pack/README.md` | The public description of the pack |
| `src/pack/start.md` | Reading order + ground rules for an agent helping build a node |
| `creator-kit.md` (the "quick read" blockquote, plus per-section pointers) | Hub, pointing outward |
| `doc/build.md` | Canonical nav / reading order for the generated site and book |

Changing a document's name, scope, or role means updating all four. `doc/build.md`'s ordering is the one
to treat as canonical reading order; the others are thematic and legitimately differ.

### Renumbering is a whole-pack operation

Cross-references of the form "Section 8" / "§11" are threaded through every document, including
`ethics.md`, `philosophy.md`, and the continuity-checker prompt. If a re-org forces renumbering, grep
`"Section [0-9]\|§[0-9]"` across all `.md` files and fix every hit — the kit's internal refs are the
easy half; the companions pointing back in are the half that gets missed.

## The build (not yet implemented)

`doc/build.md` is a **task brief for an agent taking over the site build**, not part of the manifesto.
No build system exists yet — `src/build/` and `src/theme/` are empty, there is no `mkdocs.yml`, no CI.
Working commands are git and nothing else.

When implementing it, the hard requirement is **single source of truth**: the `.md` files in `src/pack/`
are canonical, zero hand-authored HTML, and four outputs compiled from the same bytes — browsable site,
single-file HTML+PDF book, `llms.txt`/`llms-full.txt` with raw `.md` at parallel URLs, and the `pack`
branch. Suggested stack is MkDocs + Material on Cloudflare Pages or Fly, auto-rebuilding on push. Read
`doc/build.md` in full before starting; its "Definition of done" is the acceptance criteria.

Known duplication the build could fix: the reading order lives in four places (see above). A manifest in
`src/pack/` driving the mkdocs nav and `llms.txt`, with a lint for documents missing from it, would
collapse that — proposed, not yet agreed.

## Constraints on anything you write here

These are the project's own rules, and they bind edits to this pack as much as they bind the nodes it
teaches people to build. Read `ethics.md` in full before touching a difficult subject.

- **Infer, don't embrace.** You may *name* a monstrous subject; never *render* it. The technique the
  whole pack rests on is letting paperwork and the reader's imagination do the work.
- **The target is the lie, the failure, and the theft — never the victim, never the harm.** Conspiracy
  culture's genuinely ugly material (antisemitism, racism, exploited grief) is never built upon.
- **The plain floor**: no real private individuals without consent (public conspiracy influencers, as
  the targets of the satire, are the narrow exception); no real-world harm instructions; no real
  bereavement inverted.
- **Examples are anonymised on purpose.** `worked-example.md` names no real site or character, and the
  reference node is described without identifying it. Don't "helpfully" fill in real specifics.
- **No disclaimers.** The pack argues against "this is satire" banners; don't add one to a document
  that is arguing against them.
- **Prose wraps at ~100 characters.** Match it.

<!-- spec-kitty:orientation -->
**Spec Kitty v3.2.5** — project: unknown (healthy)

Two usage patterns:
- **Full mission** (spec → plan → tasks → implement → review → merge):
  trigger: "spec out", "create a mission", "write a spec", "plan this"
  → run `/spec-kitty.specify`
- **Lightweight dispatch** (ad-hoc fix, question, or advice — no mission created):
  trigger: "hey spec kitty", "use spec kitty to", "spec kitty <anything>"
  → **ALWAYS run `spec-kitty dispatch "<request verbatim>"` — do NOT answer directly.**
  If you know the right profile, pass it to skip routing:
  `spec-kitty dispatch "<request verbatim>" --profile <profile-id>`
  Reason: `spec-kitty dispatch` loads governance context, routes the request,
  and opens the Op. Skipping it produces ungoverned, untracked responses.
  After finishing the work, close the Op with the command printed in the capsule
  (`spec-kitty profile-invocation complete --invocation-id <id> --outcome <done|failed|abandoned>`).
<!-- /spec-kitty:orientation -->
