# The creator kit — the shared common operating system

These are the **constitutional documents** of a shared, permissionless world of diegetic conspiracy
satire: a slow-motion, internet-sized improv scene in which creators take the conspiracy theories
levelled at them (and at the culture they cover) and say *"yes, and,"* rendering the world-ending horror
as tedious, banal, corporate business-as-usual until the lie collapses into comedy.

This kit is meant to be the **common reference** that every participant holds to *as much as they
personally want to, and no more*. Nothing here is enforced; there is no canon-keeper and no gatekeeper.

The intended way to use it: keep a private project of your own on any git host and add the kit as a
**git submodule** on your own desk, so you always have the current shared reference to hand while your
own work stays private until you choose to publish.

```
git submodule add -b pack <the creator-kit repo> doc/core
```

The `pack` branch carries these markdown documents and nothing else: no build machinery, no
meta-documentation. `git submodule update --remote doc/core` pulls the current version of the kit.
(See `technical-suggestions.md` for the suggested project layout around it.)

Everything here is **out-of-world scaffolding** — the editor's desk, not the stage. None of it should
ever appear on a client-facing surface (see the "membrane" section of the creator kit).

## The documents

- **[`creator-kit.md`](creator-kit.md)**: the starter guide and suggested constitution. Hand this whole
  file to an LLM (Claude Code, Codex, or similar) in a fresh session and say "let's begin"; it interviews
  you (firewalling your real identity *out* of the fiction), helps you map your corner of the imagined
  world, and does almost all of the building. Start here.
- **[`premise.md`](premise.md)**: the world itself. *What if it were all true?* The Wilson and Shea
  lineage (1975), and what follows from taking it seriously: a world staffed, old, self-contradicting,
  unbearably banal, and understood by nobody, not even the people running it. The only page describing
  what is true *inside* the fiction.
- **[`getting-started.md`](getting-started.md)**: the practical on-ramp. Setting up a workspace (a
  private parent repo with this kit as a submodule), and the three-move interview the LLM runs before it
  writes a single artifact: firewall your real identity, map your corner, generate build prompts.
- **[`storytelling.md`](storytelling.md)**: what an *alternate reality game* is (a nonlinear story told
  through real objects left on the one real internet, no walls, no "start here"), and what *diegetic
  storytelling* means (a narrative with no narrator): imagine the backstory privately, then show only the
  artifacts that imply it. Absorbs "show, don't tell," and carries the two crafts that follow from it:
  the **realism engine** (mundane × extraordinary; the dry records that let you infer a horror without
  ever depicting it) and **plausible deniability** (the deliberate, discoverable tells that make an
  artifact impossible to quote as evidence without quoting the joke too).
- **[`philosophy.md`](philosophy.md)**: the detailed *why*. Conspiracy theory steals real conversations
  and hands us fake solutions; we answer, as comedians and software developers, with technical ingenuity
  and humour; diegetic satire built to be indistinguishable from the real thing, salted with tells we
  reserve the right to detonate.
- **[`worked-example.md`](worked-example.md)**: the method run once, start to finish, on a subject nobody
  would call lurid. A teacher's anger about illiteracy, the leap to *what if it's on purpose*, and the
  paperwork that leap would leave behind. The lesson: you do not need one of the famous theories. You need
  one person who is angry about something true.

- **[`improvisation.md`](improvisation.md)**: what improv teaches us about world-building. "Yes, and,"
  radical acceptance (harmonise, don't negate; ignore what you can't), Del Close's "treat your fellow
  players like poets and geniuses," and the turn-the-camera technique. The craft the whole project rests
  on.
- **[`ethics.md`](ethics.md)**: the founders' position on the hard moral questions. What we satirise
  (the lie, the failure, the theft) and what we never do (the victim, the harm, the ugliness). Read this
  before going near a difficult subject.
- **[`communications.md`](communications.md)**: how the community works. Interweaving etiquette, loose
  cells with no boss and no central forum, and the fact that we are all one another's audience (sometimes
  building on strangers who never signed up).
- **[`technical-suggestions.md`](technical-suggestions.md)**: optional practical hints. A suggested
  project layout, cheap self-hosting (Fly.io, Cloudflare free tier), why to self-host a character blog
  rather than trust a SaaS platform, and links to external tool docs. Skip it entirely if you have your
  own way of working.
- **[`story-continuity-checker-prompt.md`](story-continuity-checker-prompt.md)**: a *personal* tool,
  not a gate. Hand it to an LLM with your own node's canon to catch date/name/number contradictions
  *within your own work*. It never enforces conformity with anyone else's.
- **[`start.md`](start.md)**: the brief for an LLM. The workspace setup, the submodule, the interview,
  and the ground rules. **Point your model at this one first**, or just hand it the URL and let it do
  the rest. (In your checkout it is called `AGENTS.md`, the name models look for.)

## In one paragraph

Conspiracy theories don't just spread falsehood. They **hijack real problems** (child protection,
pollution, surveillance, who profits from what) and answer them with a lie so lurid it evicts the real
question. This project is a satire aimed at that theft. We satirise the conspiracy **and its
consequences — never the victims**, and never build on the genuinely ugly material conspiracy culture
traffics in. The craft rule for hard topics is *infer, don't embrace*: name the monstrous thing, never
render it; let the paperwork and the reader's imagination do the work. The full philosophy is in the
creator kit; the moral reasoning is in the ethics document.
