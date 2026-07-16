# Documentation about the guide

This is the documentation *for* the documentation — the non-fictional, mechanical side of the project:
how the book gets built, and how to work on it. None of it ships.

The guide itself — the product — lives in [`../src/pack/`](../src/pack/).

## What's here

- **[`build.md`](build.md)** — the task brief for compiling `src/pack/` into the three outputs (browsable
  site, typeset book, LLM-optimised source) plus the `pack` branch that creators submodule. Start here if
  you're implementing the build.
- **[`prompts/`](prompts/)** — saved LLM prompts and sessions *about building the guide*. See the caveat
  in [`prompts/README.md`](prompts/README.md); this is not where the guide's own prompts live.

For house rules when editing the text — the hub-and-spoke structure, section numbering, the membrane —
see [`../CLAUDE.md`](../CLAUDE.md) (symlinked to `AGENTS.md`), which is where both Claude Code and Codex
look automatically.

## The one distinction that matters here

The guide teaches creators to keep **out-of-world** scaffolding (the editor's desk) rigorously separate
from **in-world** artifacts (the stage). This repository applies that to itself:

- `src/pack/` — the guide. The thing readers get.
- `doc/` — the desk. Build mechanics, notes, prompts. Readers never see it.

Note the wrinkle: *everything* in this repository is out-of-world in the game's sense, because the guide
is openly a manual — it wears no diegetic costume. The `doc/` ↔ `src/` split here is a different axis:
the book versus the making of the book.
