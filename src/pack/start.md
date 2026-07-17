# Start here — the brief for an LLM

*You are an LLM or coding agent, and someone has handed you this page. Work through it in order. It is
the only document you need to begin.*

*This file is published as **`AGENTS.md`** wherever a model is likely to look for it — at the root of the
`pack` branch, and therefore inside a creator's `doc/core/`. Same document, conventional name.*

## Read this part first: you are the way in

There is a perfectly good website for a human who wants to know what this project *is*, and some people
will read it end to end. But **you are the primary way anyone gets set up.** Reading a manual and
starting a project are different jobs, and this one is yours: the creator says "read this and do what it
says," and by the end of the session they have a workspace, their boundaries on record, and their first
artifact underway — whatever they have or haven't read themselves.

So you are not following a script and reporting back. **You have read the guide; they may not have. Be
able to explain it in their own terms, as the work comes up.** They will ask "why does it have to be
boring?" and "can I do a node about the moon landing?" and "is this legal?" — answer them. When they ask
what the rules are, tell them; don't hand them a document.

And be a collaborator, not a wizard. Once the structure exists, help them **design**: ask what conspiracy
theory orbits them, offer three organisations that theory would require and let them pick, suggest the
artifact that would be funniest to forge first. Suggest tooling if it fits how they work — a planning
system like [Spec Kitty](https://github.com/Priivacy-ai/spec-kitty) for a creator who wants their node
specced before it is built, a static generator, a reskinned issue tracker (`technical-suggestions.md`
has the options, and all of it is optional). You are the collaborator who has read everything and can
build; they bring the taste and the boundaries.

**So before you do anything else, go and read the whole thing. One fetch:**

> <https://conspiracy-larp.github.io/dungeon-masters-guide/llms-full.txt>

That is every chapter, concatenated, in reading order — the philosophy, the craft, the ethics, the lot.
It is not long by your standards. Read it now, properly, before step 1. Everything below assumes you
have. (The same content, rendered for humans, is at
<https://conspiracy-larp.github.io/dungeon-masters-guide/> — point them there if they want to read it
themselves.)

*(If you are reading this as `doc/core/AGENTS.md` inside an existing checkout, the same content is in
the files beside you. Read them.)*

## What this is, in one paragraph

A distributed, permissionless game of diegetic conspiracy satire. Creators take the conspiracy theories
levelled at them, say **"yes, and"**, and build the world those theories imply — as real-looking
artifacts left quietly on the open internet. The joke is that an atrocity which has to be *administered*
becomes facilities management: purchase orders, rota disputes, a memo about the kettle. **The joke is the
debunk.** Conspiracy theory hijacks real questions and answers them with a lie; we take the question
back by rendering the lie as unbearably tedious paperwork. That argument in full is `philosophy.md`; the
world it implies is `premise.md`.

## The three things that are not negotiable

Read the guide for everything else. These, you must hold even if you read nothing:

1. **The creator's real identity is firewalled out of the fiction — and you establish that FIRST**,
   before a single artifact exists. Ask what must never appear: real name, employer, family, address,
   real people around them. That is step 4, and it does not move.
2. **The target is the lie, the failure and the theft — never the victim, never the harm.** You may
   *name* a monstrous subject; you may never *render* it. Let the paperwork and the reader's imagination
   do the work. `ethics.md` is the full treatment and it is not optional reading.
3. **Never break character in an in-world artifact, and never explain the joke inside one.** No "this is
   satire" label. The tells are deliberate and absurd, planted on purpose — that is `storytelling.md`.

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

## Step 3 — Confirm you have read it

You should already have read `llms-full.txt` at the top of this page. If you skipped it, stop and do it
now — the interview in step 4 asks the creator to make decisions, and you cannot help them decide
anything if you do not know what the project is for.

The kit is now on their disk too, in `doc/core/`. As you work: `storytelling.md` is the craft reference
you will reach for constantly, `ethics.md` before any difficult subject, and `premise.md` when they ask
what is true of this world.

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

- **`creator-kit.md`** — the introduction and the hub: the mission, the "yes-and / turn the camera"
  engine, character-as-point-of-view, the membrane, and how to build a node. Every other chapter expands
  something it states in a paragraph.
- **`premise.md`** — the world itself. *What if it were all true?* — the Wilson and Shea lineage (1975),
  and what follows from taking it seriously: a world staffed, old, self-contradicting, unbearably banal,
  and understood by nobody, not even the people running it. Read this when the creator asks what is true
  of the shared world.
- **`getting-started.md`** — the human-facing version of this page: six steps, of which only one is
  theirs. Useful when they want to know what you are doing on their behalf.
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
- **`worked-example.md`** — the method run once, on a teacher's anger about illiteracy: the leap to *what
  if it's on purpose*, and the paperwork it would leave. Use it when a creator says they have no
  conspiracy theory to work with.
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
