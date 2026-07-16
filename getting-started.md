# Getting started — your workspace, the interview, and your corner

*Companion to `creator-kit.md` (see §3). This is the practical on-ramp: how to set up a place to work,
and what happens in the interview the LLM runs before it writes a single artifact. Like everything in
this pack, it is a suggestion, not a procedure — but if you want to be creating within the hour, this is
the shortest path there.*

---

Getting started has two halves: **setting up a workspace**, and then letting the LLM **interview you**.

## First — set up your workspace

You don't need much, and none of it is compulsory. The suggested shape is simply this: keep a **private
project of your own** on whatever git host you like (GitHub, GitLab, Codeberg — it genuinely doesn't
matter), and add the shared **creator-kit repository as a git submodule** inside it. That submodule is
your always-at-hand copy of this manifesto and its companion files — think of it as the project's
**common operating system**: the shared reference every participant tries to hold to *as much as they
personally want to*, and no more. Pulling the submodule keeps you current as the kit evolves; your own
work stays private in the parent repo until (and unless) you choose to publish a node.

Two more things that shared repo gives you:

- **A place to signal.** Its **issue tracker** is an opt-in notice-board: open an issue to flag a hook
  you've left, invite another participant to look at something, or offer a thread for interweaving.
  Nobody is obliged to answer, or to do anything at all — it is an invitation, never a summons.
- **Starter scaffolding.** Alongside the manifesto, the kit carries the practical stuff that gets you
  building *sooner* — a suggested project layout, cheap and resettable ways to put things on the web,
  tool hints, and the git/pull-request trick for interlinking — all collected in
  [`technical-suggestions.md`](technical-suggestions.md). Plus conventions for keeping track of the
  **back-story you never explicitly show** — the private lore and timelines behind your node (the
  continuity checker in `creator-kit.md` §12 is part of this). It all exists for one reason: to give a
  large language model enough of a running start that you're creating within the hour instead of the
  week.

And now the load-bearing caveat, because freedom is the whole point: **none of this is obligatory.** Some
of you are seasoned developers with your own hard-won way of working who need no advice from strangers on
the internet — ignore every suggestion here and you are still completely, properly playing the game. The
layout, the tool hints, the submodule pattern are conveniences, not commandments. The only real goal is
to get people improvising on the web and telling a story together; everything in the starter pack is just
there to get you there faster.

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
