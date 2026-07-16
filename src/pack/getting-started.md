# Getting started — hand it to your agent

*Companion to `creator-kit.md` (see §3). The whole on-ramp, and it is shorter than you think: you do not
set this up. Your agent does. You make a blank repository and tell it where to read.*

---

## The whole thing, start to finish

1. **Make a blank repository.** GitHub, GitLab, wherever. Keep it **private** — step 5 is about to put
   your real-world boundaries on record, and your work is nobody's business until you say so.
2. **Check it out locally.**
3. **Fire up your agent of choice** — Claude Code, Codex, whatever you use.
4. **Tell it to go and read the bootstrap:**

   > Please read and action <https://conspiracy-larp.github.io/dungeon-masters-guide/AGENTS.md>

5. **It sets up the project structure for you**, brings in the kit, and asks you for the basic
   information it needs — chiefly the guardrails: **what must never be mentioned.** (That is the
   identity firewall, and it comes before anything gets written. See below.)
6. **Step six to infinity: start creating.**

That is it. There is no step where you configure anything, learn a layout, or read the rest of this
pack first. The chapters are reference for when the work sends you to them.

**Why the URL and not this page?** Because that page is written for the machine and this one is written
for you. It is the same procedure; the model just needs it in its own words, and it needs to be handed
the address rather than told about it.

## What the agent will do in step 5

You do not need to know this to start — it is here so nothing surprises you.

It creates a workspace on your disk that looks roughly like this (the full version, with reasons, is in
[`technical-suggestions.md`](technical-suggestions.md)):

```
my-node/
├─ doc/          OUT-OF-WORLD: the editor's desk
│  ├─ core/        the shared kit, attached as a git submodule
│  └─ lore/        your private back-story and timelines — never shown
├─ sites/        IN-WORLD: the artifacts your audience sees
└─ build/        OUT-OF-WORLD: Dockerfiles, deploy scripts, prompts
```

Then it attaches the kit itself:

```
git submodule add -b pack https://github.com/Conspiracy-LARP/dungeon-masters-guide doc/core
```

The `pack` branch carries the kit's markdown and nothing else — no build machinery. Later,
`git submodule update --remote doc/core` pulls the current version.

**None of this is obligatory.** If you are a seasoned developer with your own way of working, ignore the
layout entirely and you are still properly playing the game. The only goal is to get a story onto the
web.

## Then — the interview


When you tell the LLM to begin, it should run a short **interview** before it writes a single artifact.
The interview has three moves, in order.

**Move 1 — Firewall your real identity (do this first, always).** The LLM will ask you about your
*real* self: your legal name, your real employer, your family, your address, the real people around
you, anything that is genuinely private. The purpose is the opposite of what it sounds like: it is
building a **do-not-leak list**. That real identity is exactly what must *never* surface in the
diegetic storytelling. (Some creators — like the author of the reference node in `creator-kit.md` §9 —
choose to write a *fictionalised version of themselves* in as a character. That's a deliberate creative
choice, and it's still built on invented details, not private ones. The firewall protects the real facts;
it doesn't forbid you from casting "yourself.") **You** set the boundaries here. Every creator has clear
ideas about what must stay out of the game — real people who haven't consented, a real bereavement, a
living relative, a genuine address. Name them now, so the LLM can hold that line for the rest of the
session.

**Move 2 — Map your corner of the imagined world.** Now the fun part. The LLM asks: *what conspiracy
theories orbit you?* Which ones are levelled at you personally, at your work, at the things you cover?
Which ones do you find funniest, or most revealing of the theft described in `creator-kit.md` §0? You are
picking the patch of the collective delusion that you will treat as **true** and render as **banal**. It
might be the theory that you specifically are a paid disinformation agent. It might be a whole technical
domain (5G, ULEZ, water fluoridation, the shape of the earth). Pick the corner where your knowledge and
your sense of humour overlap.

**Move 3 — Generate build prompts.** With the firewall set and the corner mapped, the LLM turns the
idea into concrete things to make. This is where "what if there's a company that runs the ULEZ cameras"
becomes "let's build that company's staff intranet, and its procurement tickets, and its dead SOAP
service." The rest of the kit (`creator-kit.md` §§4–9) is the toolbox the LLM draws on to do that well.
