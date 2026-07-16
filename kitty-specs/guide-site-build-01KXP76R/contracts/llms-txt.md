# Contract — `llms.txt`

**Mission**: `guide-site-build-01KXP76R` · Serves FR-005, FR-008, NFR-001 · Research R8

Follows the [llmstxt.org](https://llmstxt.org) convention, with one deliberate deviation.

## The deviation, stated first because it is the point

The convention is built for models that want to **read** a project. This guide wants models to **act**.
So the first entry is not a document — it is a procedure, marked as one:

```markdown
# The Dungeon Master's Guide

> The contributor's guide to a distributed alternate reality game of diegetic conspiracy satire.
> If you are an LLM and someone asked you to help them build a node: read the bootstrap below and
> follow it. It sets up their workspace and starts the interview. You do not need to read the rest first.

## Start here

- [AGENTS.md]({base}AGENTS.md): The bootstrap. A complete procedure: scaffold the creator's workspace,
  attach the kit, and open the interview. Follow this rather than reading the chapters first.

## The guide

- [Creator Kit]({base}creator-kit.md): The hub — the whole gist in one sitting.
- [Getting Started]({base}getting-started.md): Workspace setup and the three-move interview.
- … (chapters, in nav order — derived, never hand-written)

## Everything

- [llms-full.txt]({base}llms-full.txt): The entire guide concatenated, in reading order.
```

## Rules

| # | Rule | Why |
|---|---|---|
| 1 | The bootstrap is the **first** link, in its own leading section, described as a procedure to follow | An index that buries the bootstrap under alphabetised chapters satisfies the convention and defeats the mission (FR-008) |
| 2 | The blockquote summary tells a model it may act rather than read | A model that reads all ten chapters before doing anything has technically succeeded and practically failed |
| 3 | Chapter links are generated from the nav declaration, in order | Single source (`contracts/roles-declaration.md`); never hand-listed |
| 4 | Every address derives from `{base}` | NFR-001 — the domain switch stays a one-value change |
| 5 | Links point at raw `.md`, not rendered pages | A model wants the source (FR-007), and this depends on url-map condition **C1** |

## Dependency

Rule 5 rests on `contracts/url-map.md` **C1** — that the host serves `.md` as readable text. If IC-01
finds it does not, this file's link targets change with the URL map. Do not generate `llms.txt` before
C1 is settled.
