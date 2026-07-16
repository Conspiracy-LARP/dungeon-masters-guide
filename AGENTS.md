# Start here — the brief for an LLM

*You are an LLM or coding agent, and someone has handed you this page. This is the one document you need
to begin: it sets up their workspace, brings in the kit, and starts the interview. Work through it in
order. (The human-facing version of this on-ramp, with the reasoning behind each step, is
`getting-started.md`.)*

*This file is published as **`AGENTS.md`** wherever a model is likely to look for it — at the root of the
`pack` branch, and therefore inside a creator's `doc/core/`. Same document, conventional name.*

This kit is the **shared "common operating system"** of a distributed, permissionless game of diegetic
conspiracy satire — creators taking the conspiracy theories levelled at them, saying *"yes, and,"* and
rendering the world-ending horror as tedious corporate business-as-usual until the lie collapses into
comedy. Your job is to help one creator build their corner of it. You will do almost all of the
building; they bring the idea, the taste, and the boundaries.

*If you are reading this as `doc/core/AGENTS.md` inside an existing checkout, the kit is already here —
skip to step 3.*

## Step 1 — Set up the workspace

A **private** repository of the creator's own. Private matters: their work stays theirs until they
choose to publish, and step 4 is about to put their real-world boundaries on record.

```
mkdir -p my-node/doc/lore my-node/sites my-node/build
cd my-node
git init
```

The shape, and why (`technical-suggestions.md` has the full version):

```
my-node/
├─ doc/          OUT-OF-WORLD: the editor's desk
│  ├─ core/        the shared kit (submodule, added in step 2)
│  └─ lore/        private back-story, timelines, character bios — never shown
├─ sites/        IN-WORLD: the artifacts the audience sees (each a deployable)
├─ build/        OUT-OF-WORLD: Dockerfiles, deploy scripts, prompts
└─ README.md     OUT-OF-WORLD: notes to self
```

That split is load-bearing, not decoration — see the membrane rule in the ground rules below.

## Step 2 — Bring in the kit

```
git submodule add -b pack https://github.com/Conspiracy-LARP/dungeon-masters-guide doc/core
```

The `pack` branch carries the markdown documents and nothing else. Later,
`git submodule update --remote doc/core` pulls the current version of the kit.

## Step 3 — Read the kit

Read **`doc/core/creator-kit.md`** in full before you build anything. It is the whole gist in one
sitting and it delegates to the companions below. Then, as you work: `storytelling.md` is the craft
reference you will use constantly, and `ethics.md` is required before you go near a difficult subject.

## Step 4 — Run the interview

Follow **`doc/core/getting-started.md`** (summarised in the kit's §3). Three moves, in order — and the
order is not negotiable:

1. **Firewall the creator's real identity first.** Interview them for a *do-not-leak list* — real name,
   employer, family, address, real people around them. That real identity must never surface in the
   fiction. (A creator may deliberately cast a *fictionalised* version of themselves; that's a choice,
   built on invented details, not private ones.) Do this before you write a single artifact, and hold
   the line for the rest of the session.
2. **Map their corner** of the imagined world — which conspiracy theory they'll treat as true.
3. **Generate build prompts** and start making artifacts, using the rest of the kit as your toolbox.

## The documents in the kit

- **`creator-kit.md`** — the starter guide / suggested constitution: the mission, the "yes-and / turn the
  camera" engine, character-as-point-of-view, the realism engine, plausible-deniability tells, the
  in-world/out-of-world membrane, and how to build a node. Start here.
- **`getting-started.md`** — the on-ramp expanded: the workspace/submodule setup, and the three-move
  interview (firewall, map the corner, generate build prompts). This is the flow to follow at "let's
  begin."
- **`storytelling.md`** — what an alternate reality game is and what diegetic (no-narrator) storytelling
  means: imagine the backstory privately, then show only the artifacts that imply it. Absorbs "show,
  don't tell," and carries the **realism engine** (mundane × extraordinary; the dry-record forms) and
  **plausible deniability** (the tells). This is the main craft reference when you are actually building.
- **`philosophy.md`** — the detailed *why*: conspiracy theory steals real conversations; we answer with
  technical ingenuity and humour; diegetic, indistinguishable-on-purpose satire with tells we reserve the
  right to detonate.
- **`improvisation.md`** — the craft: what improv teaches about world-building — "yes, and," radical
  acceptance, Del Close's law, and turning the camera (out to generate, toward others to offer, toward
  yourself to be inspired).
- **`worked-example.md`** — one anonymised history showing how a corner grows one idea at a time; the
  shape of the process, not a template to copy.
- **`ethics.md`** — the moral floor: you can satirise anything, but the target is the lie/failure/theft,
  never the victim or the harm. Read before going near a difficult subject.
- **`communications.md`** — how the community works: interweaving etiquette, loose cells with no boss, and
  the fact that we are all one another's audience.
- **`technical-suggestions.md`** — optional practical hints: suggested layout, cheap self-hosting, why to
  self-host rather than trust a SaaS platform.
- **`story-continuity-checker-prompt.md`** — a *personal* tool: hand it to an LLM with a node's canon to
  catch internal date/name/number contradictions. Never a conformity check against the wider world.

## Ground rules for an agent working here

- **Everything in this kit is out-of-world scaffolding — the editor's desk, not the stage.** Never copy
  these documents, or anything that *explains the joke*, into a client-facing / in-world artifact. If a
  visitor to the finished world could reach the manifesto, the joke is over. (See the "membrane" section
  of the kit.)
- **Follow `ethics.md`.** Infer, don't embrace; never the victim, never the harm, never build on the
  ugliness; observe the plain floor (no real private individuals without consent, no real-world harm
  instructions, no real bereavement inverted).
- **These are shared references, not rigid law.** The creator follows them as much as they personally
  want to. An experienced developer with their own way of working owes the kit nothing. The point is
  to get a story onto the web, not to obey a rulebook.
- **The in-world artifacts you build must carry their own tells** (`storytelling.md`) and must never break character.
