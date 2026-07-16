# The Dungeon Master's Guide

The contributor's guide to a distributed, permissionless alternate reality game of diegetic conspiracy
satire. It is a book about how to build and extend the game — written for **player-contributors**:
creative people who want to make a corner of the world, and the LLMs that will do most of the building
for them.

**If you came here to read the guide, start at [`src/pack/README.md`](src/pack/README.md)** — or read
[`src/pack/creator-kit.md`](src/pack/creator-kit.md) top to bottom, which is the whole gist in one
sitting.

This repository is the *source* of that guide. The text is the product; everything else exists to
render it.

## Layout

```
src/pack/     THE GUIDE — canonical markdown, flat. Nothing else lives here.
src/build/    the machinery that compiles it: site, book, LLM-optimised text
src/theme/    the "referee's manual" styling
doc/          documentation about the guide — how it's built and how to work on it
doc/prompts/  saved LLM prompts about building the guide
```

The `src/` ↔ `doc/` split is the guide's own advice applied to itself: `doc/` is the editor's desk,
`src/pack/` is the stage.

## Three outputs, one source

`src/pack/` compiles to a browsable website, a single-file typeset book (HTML + PDF), and an
LLM-optimised source (`llms.txt` / `llms-full.txt`, plus the raw markdown at parallel URLs) — all from
the same bytes, so they can never drift. **[`doc/build.md`](doc/build.md)** is the brief for that build
and the place to start if you're implementing it.

## Using the guide in your own project

Creators keep a private project of their own and add the guide as a submodule on their desk. The `pack`
branch carries the markdown documents and nothing else — no build machinery, no meta-documentation:

```
git submodule add -b pack <this repo> doc/core
git submodule update --remote doc/core     # pull the current version of the kit
```

## Contributing

There is no canon-keeper and no gate — that's the point of the project, and it applies here too. Read
[`CLAUDE.md`](CLAUDE.md) (symlinked to `AGENTS.md`) before editing: it covers the house rules that are
easy to break by accident, chiefly the hub-and-spoke structure of `creator-kit.md` and the fact that
everything in this repo is *out-of-world* and must never leak onto a client-facing surface.
