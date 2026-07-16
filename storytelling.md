# How we tell it — an alternate reality game, told diegetically

*Companion to `creator-kit.md`. This explains the two ideas the whole project rests on — what an
**alternate reality game** is, and what **diegetic storytelling** means — and the working method that
follows from them. It absorbs and expands the kit's "show, don't tell."*

---

## What is an alternate reality game?

An alternate reality game (ARG) is a **nonlinear narrative told not through a single book or film, but
through objects scattered in the real world** — documents, websites, records, artifacts — which the
audience discovers and pieces together for themselves. There's no page one and no chapter two; there's a
mesh of things, and a reader who follows the threads assembles the story in their own head, in their own
order.

For us, the "real world" those objects live in is **the internet** — and the crucial point is that there
is only **one** internet. We do not build an internet-within-the-internet. We put up no walls, no "you are
now entering a game" portal, no frame, no label. We simply **leave real-looking things on the real
internet for anyone to find.** A visitor doesn't *enter* our game; they stumble on a website, a filing, a
blog that happens to be part of one — indistinguishable, at first glance, from any other corner of the
web. The absence of a boundary is the point: the story is loose in the world.

### Nonlinear also means you don't control who sees what

"Nonlinear" isn't only about the *order* of the pieces — it's about the fact that **we have no idea which
part of the shared creation any given person will find first, or how much of it they will ever see.** There
is no front door and no guided tour. Someone might land on a single fabricated filing, decide it's a mild
curiosity, poke about for ninety seconds, and wander off, mildly puzzled — and that is a *completely fine*
outcome. Someone else might catch the scent, follow a link, follow another, and disappear down the rabbit
hole for a fortnight. You are writing for both at once, and for everyone in between.

The design goal that follows is: **maximise the reward for discovery and exploration.** The reader who
digs should keep being paid for digging — another thread, another connection, another artifact that
quietly confirms the last one. And the single best way to generate that inexhaustible reward is
**collaboration.** Many interlinked properties, made by many hands, produce a mesh in which the narratives
seem to be *simultaneously converging and diverging* — every path you follow both explains something and
opens two new questions. Working together as improvisers, we build a bizarre, coherent-yet-uncontainable
shared world: something genuinely worth exploring, that **rewards the intelligence of people who take the
time to read and experience it.** (That is also why we play to the top of our own intelligence — see
`improvisation.md`; a world worth going deep into has to have been built by people going deep themselves.)

## What is diegetic storytelling?

"Diegetic" means *existing inside the world of the story.* We commit, strictly, to **environmental
storytelling: a narrative with no narrator.** There is no authorial voice, no caption, no one standing
outside the fiction explaining what's going on. The world tells itself, entirely, through the mundane
things it contains.

That is "show, don't tell" carried to its limit — so far that it becomes a rule with almost nothing left
to break: **we never actually tell a story. We only ever show the artifacts that would exist if the story
were true, and let the audience infer the story for themselves.** Never explain the premise, never narrate
the menace, never wink. The horror is always inferred, never stated.

## The method — imagine privately, then show

This is how you go from an idea to a node, in two movements.

**1. First, privately imagine the truth — and keep it private.** Before you build anything a visitor can
see, work out the backstory of your world in detail: who the people were, what they did, how they worked,
how the (say) evil megacorporation really made its money, what it was actually up to. Write it down for
*yourself*. This is your **lore** — out-of-world, never shown, kept in a private `lore/` folder (the
continuity checker exists to keep it straight). The reader will never read this. That's correct. Its whole
job is to make everything downstream consistent and true.

**2. Then imagine the artifacts that truth would leave behind — and show only those.** Without ever
disclosing the backstory, ask the generative question: *if all of that were real, what traces would it
have left lying around?* And then build the traces. For an evil corporation, that might be:

- the internal **memos** and the leaked **emails**;
- the corporate **issue tracker**, full of banal tickets;
- the **advertisements**, the recruitment brochure, the staff handbook;
- the **stolen source code** for the thing it builds;
- the horrified **reaction of a blogger** who stumbled onto the property and started pulling threads;
- the individual **CVs and personal websites of the perpetrators.**

Each artifact is a shard. No single one tells the story; together, they imply it — and the reader, who
assembles them into a picture nobody handed them, ends up believing that picture in a way no narration
could ever achieve, because *they* built it. **Diegetic storytelling means never telling the story, and
always showing the implications of its being true.**

**Different viewpoints on the same truth.** Notice that those shards don't share a *point of view* — the
blogger recoils in horror, the internal memo is blandly bureaucratic, the perpetrator's CV is quietly
proud. They all acknowledge the same underlying reality (the organisation is real, the thing is
happening), yet each reacts to it through a completely different lens. That clash — one shared fact, many
opposed viewpoints upon it — is much of what gives a world its depth and its texture, and it is also what
lets many separate creators and characters inhabit one shared reality honestly without anyone having to
agree about anything. (This is the richer form of "yes, and": acknowledging a reality is not the same as
agreeing with it — see `improvisation.md`.)

## Why it works

An accounting ledger that says nothing and means everything beats a paragraph of sinister narration every
single time. The conclusion a reader reaches by their own inference is unshakeable; the conclusion you
hand them on a plate is disposable. So we withhold. We build the mundane surfaces — and trust the reader
to do the terrifying arithmetic themselves.

*(For making those artifacts *convincing*, see the realism engine and the plausible-deniability tells in
`creator-kit.md`; for keeping the private lore off the public stage, see the membrane section there.)*
