# How we tell it — an alternate reality game, told diegetically

*Companion to `creator-kit.md` (see §6). This is the whole craft of the telling, end to end: the two
ideas the project rests on — what an **alternate reality game** is, and what **diegetic storytelling**
means — then the working method that follows from them, the **realism engine** that makes an artifact
convincing, and the **tells** that keep a convincing artifact from ever being quoted as evidence. It
absorbs and expands the kit's "show, don't tell."*

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
*yourself*. This is your **lore** — out-of-world, never shown, kept in a private `doc/lore/` folder (the
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

## The realism engine — mundane × extraordinary

Knowing *which* artifacts to show is half the job. The other half is making them feel real — and the
thing that does that is the collision of the **extraordinary** premise with an avalanche of **mundane**
detail. The horror is the given; the texture is the craft. So whenever you have an extraordinary claim,
immediately ask the small questions:

- Who *runs* it, and what's their job title?
- What's on the **procurement** system? What's the SLA? Which ticket is overdue?
- Who signs it off? Which certificate expired? Which mailbox is dead?
- **What does the cafeteria serve on Thursday?**

That last one is not a joke — the vending machine, the honesty jar, the rota dispute, the memo about
the kettle cost-centre are what sell the whole edifice. Anyone can invent a death-ray. The thing that
makes the death-ray *land* is the maintenance log for the death-ray.

**Any dry record can carry the story — a record is just one of many diegetic tools, not a gold
standard.** The trick is the same whichever form you pick: paperwork that reads, straight, as
unremarkable, and reads, with the premise in mind, as monstrous. The reader's imagination fills the
blank far more horribly than you ever could, and you never had to depict a single terrible thing. A few
of the forms this can take:

- **A table of business expenses.** A column of line items is a story if you read it right. Why did the
  senior board charter a boat, and to *where*? Whose name is on the passenger manifest that has no
  business being there? What was "hospitality, off-site (do not itemise)" for? You never explain; the
  expense line asks the question the company spent a fortune hoping nobody would ask.
- **Clinical / medical records.** To tell the story of the company that harvests adrenochrome, you do
  not describe the process — you release the case files, in terse, deadpan pseudo-medical jargon. A
  batch record. An intake note. A quality-control variance: *did the subject struggle; did an elevated
  state of terror correlate with an unusually high harvest yield?* — rendered as a clinical KPI, a line
  in a validation report, an audit finding about "cohort distress affecting throughput." The atrocity
  is entirely inferred and the artifact is entirely a QA document; the horror lives in the gap between
  the flat clinical register and what it is quietly measuring.
- **Accounting records / annual accounts.** A cost centre, a supplier ledger, a cold-chain logistics
  line, a quarterly note about "yield." (Picture an abandoned acquisition-diligence pack for a
  "non-human adrenochrome supply route" that dead-ends, in-world, on a *no-bid decision on economics* —
  the horror entirely inferred, the artifact entirely a spreadsheet.)
- **Logs, manifests, rotas, maintenance records** — the maintenance log for the death-ray; the rota
  that shows who was on shift the night the ticket was raised.

Whichever you reach for: **infer, don't embrace** (`creator-kit.md` §7, and `ethics.md` in full). Name
nothing terrible; measure it, invoice it, minute it, and let the register do the work.

## Why it works

An accounting ledger that says nothing and means everything beats a paragraph of sinister narration every
single time. The conclusion a reader reaches by their own inference is unshakeable; the conclusion you
hand them on a plate is disposable. So we withhold. We build the mundane surfaces — and trust the reader
to do the terrifying arithmetic themselves.

*(For keeping the private lore off the public stage, see the membrane section of `creator-kit.md` (§8).)*

## Plausible deniability — salt every artifact with tells

Everything above is about making the artifact convincing. This section is about surviving that — because
here is the failure mode this whole project has to survive: **what if it works too well?** You build a
straight-faced company that runs the kill-grid, a conspiracy influencer stumbles onto it, doesn't get
the joke, and starts broadcasting your fiction as *proof*. That is the exact inversion of the mission
(`creator-kit.md` §0) — mock-not-fuel turned into fuel. The defence is *not* a disclaimer (`creator-kit.md`
§7 explains why we don't use them). The defence is **built-in absurdity**: deliberate, discoverable tells
planted *inside* the artifact that anyone paying real attention will catch, and that make the thing
impossible to quote as evidence without quoting the joke along with it.

Think of them as **concealed bugs** — not mistakes, but jokes wearing the costume of mistakes. Salt a
few into everything you make. When the influencer reads your board of directors aloud on their stream,
the tell reads out too, and the "evidence" detonates in their hands.

### The line between a good tell and a bad one

This distinction is the whole craft of the section, so get it right. **A good tell reads, once spotted,
as deliberate wit.** It points at something *outside* the fiction that the reader recognises, and its
unmistakable message is *"a person planted this on purpose."* It cannot be quietly fixed, because
there's nothing to fix — it's a joke, not an error. **A bad tell reads as incompetence.** It looks like
a slip, and a debunker does one of two fatal things with it: shrugs ("sloppy record-keeping, but the
rest checks out") and keeps citing everything around it as real, or silently *corrects* it and carries
on. An error doesn't detonate the evidence. A joke does. Compare:

| ✅ Good tell (reads as a *joke*) | ❌ Bad tell (reads as a *mistake*) |
|---|---|
| A board of directors that turns out to be the cast of *Dad's Army* — points outside the fiction, unmistakably authored. | A director whose date of birth falls *after* the date he was appointed. Reads as a data-entry error; a debunker just says "typo" and moves on. |
| A company "incorporated in 1600," older than the register that holds it — an impossibility with a *mythic, authored* flavour, like a legend rather than a fat-fingered field. | A "fortnight" that is nineteen days, or a budget total that doesn't add up. Looks like arithmetic you got *wrong*, not arithmetic you *rigged*. |
| A registrar whose own certificate of incorporation certifies a *different* name — strange, deliberate, and it deepens the mystery. | A postcode in the wrong format, a misspelt statute. Just sloppiness; erodes your competence without landing a gag. |
| A QR code that decodes to a limerick; a reference number that spells a word — no one reaches these by accident. | A field left as `<placeholder>` or `lorem ipsum`. Not a tell, just an unfinished document. |

**The test:** *if a stranger spotted this, would they laugh — or would they think you'd made a mistake?*
If the honest answer is "made a mistake," it isn't a tell; it's a bug, and it will be either ignored or
corrected. Aim for the laugh. Some reliable families of the *good* kind:

- **A cast lifted from comedy.** One node's four-hundred-year-old immortal board of directors are named,
  to a man, after the cast of *Dad's Army* — Mainwaring, Wilson, Jones, Pike, Frazer, Godfrey, Walker.
  Read cold, it's a chilling list of deathless directors; read by anyone over forty, it's the Home
  Guard. You might name everyone filing tickets after 90s stand-up comedians, or the actors from *ALF*,
  or the starting eleven of some 1974 football team. Sincere on the page, ridiculous the instant someone
  recognises it — and *recognition*, not arithmetic, is what makes it land.
- **Mythic impossibilities, played dead straight.** A company incorporated in 1600, older than
  the company register that lists it. A certificate that vouches for the wrong name. These are impossible, but they
  read as *authored legend*, not clerical slips — the difference between "no one could have typed this
  by accident" and "someone typed this wrong."
- **Technical Easter eggs.** A QR code that, scanned, decodes (a UUENCODED or base64 blob, say) to a
  line of pure nonsense that gives the game away. A hidden comment, a checksum that reads as a word, an
  "encrypted" payload that decrypts to a limerick. These reward exactly the kind of person who would try
  to *authenticate* the document — and hand them the punchline for their trouble.

Aim for **a few per artifact**, vary them, and never announce them — they work precisely because
they're discovered, not flagged. The best tells do triple duty: they're funny to the reader who's in on
it, they're a landmine under anyone trying to weaponise the work, and — because they're absurd on their
face — they are the strongest possible evidence that the whole thing was always a performance. Plant
your deniability *now*, in the making; don't reach for it as an apology later.

*(Why "indistinguishable at a glance" is the goal rather than the hazard — and why the tells are what
make it safe — is the Poe's Law section of `creator-kit.md`.)*
