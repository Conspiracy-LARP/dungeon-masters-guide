# Contract — the `pack` branch

**Mission**: `guide-site-build-01KXP76R` · Serves FR-009, FR-010, C-004, C-005 · Research R4

The branch creators attach to their own project. It is a **generated artifact**, not a history.

## Consumer contract

```
git submodule add -b pack git@github.com:Conspiracy-LARP/dungeon-masters-guide.git doc/core
git submodule update --remote doc/core     # later: pull the current kit
```

A consumer gets `doc/core/creator-kit.md`, `doc/core/AGENTS.md`, and friends — flat, at the branch root.
This command is **already published to readers** in `src/pack/start.md`, `src/pack/README.md`, and
`src/pack/technical-suggestions.md`. It must keep working; if it stops, the guide is lying (R-002).

## Producer contract

Force-push an orphan commit on every push to `main`. The tree MUST be:

| Rule | Detail |
|---|---|
| **Contents** | Exactly the files of `src/pack/`, flat |
| **Rename** | `start.md` → `AGENTS.md` (FR-010, C-004) |
| **Rewrite** | Every reference to `start.md` → `AGENTS.md`, in link targets and inline text. Must not touch `getting-started.md` — naive substring replacement is a real trap here |
| **Excludes** | No `src/`, no `doc/`, no `.github/`, no `mkdocs.yml`, no build files, no meta-documentation |
| **Links** | Every relative link resolves *on this branch* (FR-013) |
| **Front door** | `README.md` stands alone — it must never reference `doc/`, `src/`, or anything absent from the branch |

## Why the bootstrap is renamed only here

`AGENTS.md` is a *loading* convention, not just a naming one: agent tools auto-load nested agent files
for the subtree being edited. The bootstrap's first instruction is `mkdir -p my-node/...`. Named
`AGENTS.md` in `src/pack/`, it would fire at a contributor editing the guide and start scaffolding a
creator's workspace. Hence: inert as `start.md` on `main`, conventional as `AGENTS.md` where a model
actually needs to find it (C-004).

## Reproduction gate (C-005)

The branch was **created by hand on 2026-07-16** as commit `d024682`, to unblock the `5g_arg` project
whose `doc/core` submodule needed somewhere safe to point. Automation must produce a **byte-identical
tree** before it takes over. Verify by comparing the generated tree against `d024682`; a difference means
either the hand build or the automation is wrong, and both must be understood before force-pushing over
a branch consumers already track.

## Read-only by contract

Consumers pin a submodule to a force-pushed branch. That is safe for a read-only reference, and unsafe
for anything else. Never commit to this branch directly — edit `src/pack/` on `main`. The generating
commit message states this on the branch itself.

## Known non-atomicity

Pages and the branch publish as separate operations, so a consumer fetching between them briefly sees the
previous tip. Accepted: both derive from the same commit, and coordinating them would need state the
stateless-static constraint (C-004) forbids. A lint failure must block both.
