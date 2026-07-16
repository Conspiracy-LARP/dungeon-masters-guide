# AGENTS.md — working with the shared `core/`

This directory is the **shared "common operating system"** of a distributed, permissionless game of
diegetic conspiracy satire. It is designed to be dropped into a creator's own private repository as a
**git submodule**, so every participant has the same reference to hand. If you are an LLM helping a
creator build a node, read this first, then read `creator-kit.md` in full.

## Your entry point

**`creator-kit.md`** is the starter guide. When the creator says "let's begin," follow its opening flow:

1. **Firewall the creator's real identity first.** Interview them for a *do-not-leak list* — real name,
   employer, family, address, real people around them. That real identity must never surface in the
   fiction. (A creator may deliberately cast a *fictionalised* version of themselves; that's a choice,
   built on invented details, not private ones.)
2. **Map their corner** of the imagined world — which conspiracy theory they'll treat as true.
3. **Generate build prompts** and start making artifacts, using the rest of the kit as your toolbox.

## The documents here

- **`creator-kit.md`** — the starter guide / suggested constitution: the mission, the "yes-and / turn the
  camera" engine, character-as-point-of-view, the realism engine, plausible-deniability tells, the
  in-world/out-of-world membrane, and how to build a node. Start here.
- **`storytelling.md`** — what an alternate reality game is and what diegetic (no-narrator) storytelling
  means: imagine the backstory privately, then show only the artifacts that imply it. Absorbs "show,
  don't tell."
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

- **Everything in `core/` is out-of-world scaffolding — the editor's desk, not the stage.** Never copy
  these documents, or anything that *explains the joke*, into a client-facing / in-world artifact. If a
  visitor to the finished world could reach the manifesto, the joke is over. (See the "membrane" section
  of the kit.)
- **Follow `ethics.md`.** Infer, don't embrace; never the victim, never the harm, never build on the
  ugliness; observe the plain floor (no real private individuals without consent, no real-world harm
  instructions, no real bereavement inverted).
- **These are shared references, not rigid law.** The creator follows them as much as they personally
  want to. An experienced developer with their own way of working owes this folder nothing. The point is
  to get a story onto the web, not to obey a rulebook.
- **The in-world artifacts you build must carry their own tells** (kit §8) and must never break character.
