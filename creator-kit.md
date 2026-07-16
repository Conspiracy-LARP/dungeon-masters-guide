# The Creator Kit — a shared world of diegetic conspiracy satire

**What is this?** In a sentence: it is the *Dungeon Master's Guide* to an **alternate reality game** that
uses diegetic storytelling to ask one question — *what if all the conspiracy theories were true?*

The idea is not new. In the late 1960s and early '70s, Robert Anton Wilson and Robert Shea took every
conspiracy theory they could lay hands on and, in the LSD-hazed **_Illuminatus!_ Trilogy**, imagined them
all as simultaneously true. We are doing essentially the same thing — but aimed at the *modern* conspiracy
theories, told through *modern* media and technology, and rendered **entirely diegetically**: not as a
novel with a narrator, but as a mesh of real-looking websites, documents, and artifacts left quietly on
the open internet for the curious to stumble upon. Player-collaborators borrow the tools of comedic improv
to build this shared universe together — a sprawl of **interlinked rabbit holes that reward and perplex
the curious in equal measure.** This manifesto exists to explain the **philosophy, process, and
technology** that make that possible, and to help bring new player-collaborators into the project.

---

*Hand this whole document to an LLM (Claude Code, Codex, or similar) in a fresh session. It is
written to be read by two audiences at once: **you**, a content creator deciding whether and how to
join, and **the LLM**, which will do almost all of the building. Read it top to bottom once. Then
tell the LLM "let's begin," and it will interview you and start.*

*This is the **quick read** — the whole gist in one sitting. Several themes are summarised here in a
paragraph and expanded in their own companion documents, so you can go deep only where you want to:*

> - **[`philosophy.md`](philosophy.md)** — the detailed *why*: conspiracy steals real conversations; our answer; and why it's a fight worth joining.
> - **[`storytelling.md`](storytelling.md)** — what an alternate reality game is, and how diegetic (no-narrator) storytelling works.
> - **[`improvisation.md`](improvisation.md)** — the craft: "yes, and," radical acceptance, and turning the camera.
> - **[`ethics.md`](ethics.md)** — the moral floor for hard subjects: infer, don't embrace; never the victim.
> - **[`communications.md`](communications.md)** — how the loose community of creators finds and builds on each other.
> - **[`technical-suggestions.md`](technical-suggestions.md)** — cheap, resettable ways to actually put it all on the web.
> - **[`worked-example.md`](worked-example.md)** — one anonymised history of how a corner grew, idea by idea.
> - **[`story-continuity-checker-prompt.md`](story-continuity-checker-prompt.md)** — a personal tool to catch your own timeline bugs.

---

## 0. The mission — why this exists

Conspiracy theories don't just spread falsehood. They **hijack real problems**. There are real
questions about surveillance, about who owns the infrastructure of a city, about corporate power over
public health, about who profits from a war. The conspiracy theory swoops in, attaches itself to that
real anxiety, and then answers it with a lie so lurid and so unfalsifiable that the real question can
never be asked again. The 5G mast becomes a death-ray, and now you cannot have an honest conversation
about telecoms infrastructure. The ULEZ camera becomes a component of a genocide grid, and now you
cannot talk about air quality. The lie doesn't just mislead — it **evicts** the real concern and
squats in its place.

This project is a satire aimed at that theft. We take a conspiracy theory and we do the one thing the
theorist never expects: we **agree**. We say, "Fine. Suppose it's all true. Suppose there really is a
sinister organisation running the kill-grid / suppressing the flat earth / harvesting adrenochrome."
And then we ask the questions the theory can't survive. *Who runs it? What company? Who signs off the
purchase orders? What's the SLA on a malfunctioning death-ray? What does the cafeteria serve on
Thursday?* We render the world-ending horror as **tedious, banal, corporate business-as-usual** — and
in that incongruity the theory collapses into comedy. An atrocity run as facilities management cannot
also be a terrifying secret. The joke *is* the debunk.

Two things follow from this, and they sit at the top because everything else depends on them:

- **We satirise the conspiracy AND its consequences — never the victims, never the marginalised
  groups the theory scapegoats.** Conspiracy culture is riddled with genuinely ugly material:
  antisemitism, racism, the demonisation of minorities, the exploitation of real grief. We do not
  build on that ugliness. We satirise the *theory* and the *harm it does*, which means we defend the
  real problem *from* the conspiracy that abandoned it. That is the whole moral engine of the work.
- **We engage the darkest topics precisely to take them back.** The point of confronting adrenochrome,
  or the 700-block on a certain London road, is not to be edgy — it is that the conspiracy has stolen
  a real horror (child abuse is real; it matters) and replaced it with a cartoon that makes the real
  thing *impossible to address*. We reclaim the subject by rendering the cartoon as absurd
  bureaucracy — and we do it by *inference*, never by depicting the harm itself. (Section 7 is the
  whole craft of this. Read it before you go near a hard topic.)

**Why tell it this way — why the diegetic mode?** Because the form *is* the argument. Conspiracy theory
is never delivered as a single, authored, labelled story. It has no centre and no author. It is diffuse
— seeped into everything, assembled by the believer from fragments scattered across the whole culture:
a screenshot here, a leaked document there, a video, a forum post, a number that "can't be a
coincidence," a "do your own research" that hands you the pleasure of connecting the dots yourself. And
because you connected them yourself, you own the conclusion, and nothing can talk you out of it. That
diffuse, centreless, reader-assembled, everything-is-connected mode is conspiracy theory's real power.
So we adopt it. We tell our satire the same way — no central text, no author's voice, no "this is
fiction" label, just a mesh of mundane artifacts scattered across real-looking websites that cross-link
into a picture you assemble for yourself. We are **using conspiracy theory's own mode against itself**:
the same "follow the threads, join the dots" method, except the dots you join lead to *Dad's Army*, to
a QR code that decodes to a limerick, to an atrocity run as facilities management — and the picture you
assemble for yourself is the debunk. That is why this is a diegetic game and not an essay: an essay
tells you the theory is absurd; this lets you *discover* it, in exactly the mode that made you believe
in the first place.

One note on spirit, because it governs everything: **this is a game — it is meant to be fun and harmless,
and it is never an attack on a person.** What it attacks, and attacks without apology, is *ideas* —
harmful ones. (Some will insist that mocking an idea they hold is mocking *them*; it isn't, and we don't
indulge the confusion.) Our sympathy is for the people conspiracy theory harms — the vandalised
communities, the neighbours who foot the bill, the families it pulls apart. We take no party line, but we
are unashamedly on the side of reason and the possibility of a reasonable conversation — the very thing
conspiracy theory destroys. The full argument for why that makes this worth doing is in `philosophy.md`.

If you are in, you are joining a small, loose troupe of people who make content about conspiracy
culture and who are, all of us, opposed to it. And — this is the delicious part — a good number of us
have had genuinely unhinged allegations thrown at us *by* conspiracy theorists. This game invites you
to take those allegations and say **yes, and**.

---

## 1. What this is — a permissionless protocol, not a canon

The closest thing you already know is probably the SCP Foundation. This is **not** that. SCP lives on
a small number of editorially-controlled wikis; senior members vote, curate, and delete to hold a
degree of narrative conformity. This project has **none of that**. There is no wiki, no council, no
canon-keeper, no vote, nobody who can tell you your contribution is "not allowed."

It is better to think of this as an **improv troupe the size of the internet**, performing one
enormous, slow-motion, never-ending scene. The rules are the rules of good improv, not the rules of an
institution:

- **Anyone can join.** You don't apply. You just build a thing and put it up.
- **Nobody is in charge.** There is no central site. Your node lives on *your* domain, *your* blog,
  *your* channel. You own it. You can change it or delete it whenever you like.
- **Interlinking is voluntary in both directions.** You may acknowledge and build on anyone else's
  work; they may acknowledge and build on yours — or not. Neither of you needs the other's permission,
  and neither of you owes the other consistency.
- **Your cast is your own — there is no single canonical organisation.** This is important, so it gets
  its own bullet. Every creator invents the companies, people, and machinery that *their* conspiracy
  theory would require. A node about the ULEZ theory might imagine an organisation that runs a network
  of directed-energy weapons; a node about flat earth might imagine something completely different — a
  cartel of geography-textbook publishers, say, or the border-wardens who patrol the lands beyond the
  great circle to keep us from seeing the truth. Entirely different companies, entirely different
  characters. You do **not** inherit anyone else's org. You *may* choose to reuse another creator's
  organisation (a "Partner," a front company, a named operative) when it's fun to — that's what
  interlinking (Section 4) is *for* — but most nodes begin with a wholly independent cast and connect,
  if at all, later, through the seams.
- **The audience decides what lives.** A node succeeds not because a senior member blessed it, but
  because other creators enjoyed it enough to build on it, and — ultimately — because readers found
  it and started to follow the threads. That is the only referee. Nobody will ever tell you that you
  can't do something. The audience just quietly tells you whether it worked.

Because there's no central canon, **global contradictions are fine — in fact they're realistic.** Two
creators who *do* share an organisation can describe it completely differently; two creators who don't
share one at all is the more usual case. Real conspiracy theories
contradict each other constantly and it never slows them down; the mesh of half-agreeing stories reads
*more* true, not less. You are not maintaining a bible. You are adding a room to an impossible mansion
that has no architect.

**How this differs from SCP and the Backrooms (and why that matters).** The obvious comparisons are
shared-world projects like the SCP Foundation or the Backrooms — both of which we're fans of. But those
are *curated*: senior staff, editors, and a voting process keep a house style, a canon, a set of binding
principles and stories. This project has none of that. There are no editors and no seniors — **only the
shared manifesto you are reading now**, and it is simply a set of *operating principles you may adopt or
ignore as freely as you like.* Nobody minds. Nobody will criticise you for declining the rules. Everyone
plays this game their own way, and the whole threshold for being "in" is this: **find one other
contributor who likes the way you work, and you're in.** What exists, then, is a set of **loosely-coupled,
user-created nodes concealed within the real internet**, and the success or failure of any one property
comes down to just two things: the enthusiasm of the person who made it, and whatever audience it happens
to attract. We build for our own pleasure and the pleasure of others, and the bar is low and honest: **if
even one person finds our work amusing, it has succeeded.** As a **non-commercial** project we're not
bound by the standards of mainstream publishing, answerable to no editor and no market. We exist for two
reasons only: to **create joy**, and to make what we believe is an **important political point about the
dangers of conspiracy theory**.

**Why a formless form suits us.** There's a deeper reason this decentralised, adopt-or-ignore shape is
right — not merely convenient, but *fitting.* We are built the way conspiracy theory itself is built. A
conspiracy theory has no author and no canon either: someone tells a tall tale, the next person repeats it
with an embellishment and their own twist — often casting *themselves* as its hero — and the story mutates
as it travels. That is exactly why conspiracy theory propagates so effectively: it behaves like a
**virus**, evolving, adapting, and filling whatever conceptual niche happens to be open, always finding
new audiences and always changing shape. A satire of conspiracy theory ought to be conscious of that form
and borrow it — to spread, mutate, and fill niches the same way its target does. So our looseness is not a
weakness to apologise for; it is us adopting the very mechanism that makes the thing we satirise so
successful, and turning it to our own ends.

---

## 2. Why now — the LLM does the building

Here is the practical reason this is suddenly possible for people who are not web developers: **the
LLM does the building.** You supply an idea, some taste, and short bursts of attention. The model does
the planning, the writing, the HTML, the fake PDFs, the deployment. You do not need to know how to
make a website. You need to know what would be *funny* and *true*, and to say "no, more boring than
that" when the machine over-writes.

So the reassurance this section exists to give is about **time, not skill**:

- **It's easy to start.** Fire up Claude Code or Codex in a new session, paste in this kit, and let
  the LLM do the work. That's the whole setup step.
- **It need not eat your schedule.** Many creators here are academics or highly technical people —
  and busy. You can contribute a whole node in a few short sittings and then leave it alone for a
  month. The world doesn't require your constant presence; it just keeps your room where you left it.
- **You bring the judgement; the LLM brings the labour.** Your job is to point ("what if there's a
  company that…"), to react ("funnier if it's a purchase order"), and to hold the line on taste and on
  your own boundaries. The model handles everything downstream of that.

---

## 3. Getting started — your workspace, the interview, and your corner

Getting started has two halves: **setting up a workspace**, and then letting the LLM **interview you**.

### First — set up your workspace

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
  continuity checker in Section 14 is part of this). It all exists for one reason: to give a large
  language model enough of a running start that you're creating within the hour instead of the week.

And now the load-bearing caveat, because freedom is the whole point: **none of this is obligatory.** Some
of you are seasoned developers with your own hard-won way of working who need no advice from strangers on
the internet — ignore every suggestion here and you are still completely, properly playing the game. The
layout, the tool hints, the submodule pattern are conveniences, not commandments. The only real goal is
to get people improvising on the web and telling a story together; everything in the starter pack is just
there to get you there faster.

### Then — the interview

When you tell the LLM to begin, it should run a short **interview** before it writes a single artifact.
The interview has three moves, in order.

**Move 1 — Firewall your real identity (do this first, always).** The LLM will ask you about your
*real* self: your legal name, your real employer, your family, your address, the real people around
you, anything that is genuinely private. The purpose is the opposite of what it sounds like: it is
building a **do-not-leak list**. That real identity is exactly what must *never* surface in the
diegetic storytelling. (Some creators — like the author of the reference node in Section 9 — choose to
write a *fictionalised version of themselves* in as a character. That's a deliberate creative choice,
and it's still built on invented details, not private ones. The firewall protects the real facts; it
doesn't forbid you from casting "yourself.") **You** set the boundaries here. Every creator has clear
ideas about what must stay out of the game — real people who haven't consented, a real bereavement, a
living relative, a genuine address. Name them now, so the LLM can hold that line for the rest of the
session.

**Move 2 — Map your corner of the imagined world.** Now the fun part. The LLM asks: *what conspiracy
theories orbit you?* Which ones are levelled at you personally, at your work, at the things you cover?
Which ones do you find funniest, or most revealing of the theft described in Section 0? You are picking
the patch of the collective delusion that you will treat as **true** and render as **banal**. It might
be the theory that you specifically are a paid disinformation agent. It might be a whole technical
domain (5G, ULEZ, water fluoridation, the shape of the earth). Pick the corner where your knowledge and
your sense of humour overlap.

**Move 3 — Generate build prompts.** With the firewall set and the corner mapped, the LLM turns the
idea into concrete things to make. This is where "what if there's a company that runs the ULEZ cameras"
becomes "let's build that company's staff intranet, and its procurement tickets, and its dead SOAP
service." The rest of this kit (Sections 4–9) is the toolbox the LLM draws on to do that well.

---

## 4. The engine — "yes, and" and turning the camera

Everything creative in this project runs on the principles of improv, borrowed wholesale — because this
*is* improv, just performed slowly across the web instead of quickly on a stage. Two motions you'll use
constantly:

- **"Yes, and."** Accept the offer on the table — the conspiracy's premise, or another creator's
  contribution — as real, and then *add* to it. Never negate; always extend. And when another creator's
  world doesn't fit yours, reach first to **harmonise**, not to correct.
- **Turning the camera.** With no single stage, the fundamental creative act is *deciding where to point
  the camera* — which corner of the world to film next. Turn it **out** to generate (film the part nobody
  filmed: who runs the grid, who profits, the boring version); turn it **toward another creator** to
  offer a link between your worlds; turn it **toward yourself** to pull someone else's brilliant idea in
  as inspiration.

That's the whole engine. The full stagecraft — radical acceptance and harmonising instead of negating
(and when to just ignore what you can't harmonise), Del Close's *"treat your fellow players like poets and
geniuses,"* and the turn-the-camera technique with its generating and interweaving menus — is its own
document: **`improvisation.md`**. It is the craft this entire project rests on; read it early.

---

## 5. Character is a Point of View

Borrow the Upright Citizens Brigade idea: a strong comic character is not a bundle of quirks, it is a
single, specific, unwavering **Point of View** — one lens through which the character interprets
*everything*. The frightened debunker who believes reassurance is a moral duty. The procurement clerk
who genuinely cannot see the atrocity for the paperwork. The true-believer theorist who is the only
honest person in the story. Write the character's POV as **one sentence** and hand it to the LLM as a
check: every line that character produces must be consistent with that lens.

And **play it dead straight.** The villain is never winking. The clerk is not in on the joke. The
comedy comes from the *gap* between the character's sincere, mundane point of view and the horror it is
calmly processing — never from the character signalling that they know it's funny. If your operative
ever seems aware they're in a satire, you've broken it. Play every character as though their reality is
simply reality.

---

## 6. The realism engine — mundane × extraordinary

The thing that makes a node feel real is the collision of the **extraordinary** premise with an
avalanche of **mundane** detail. The horror is the given; the texture is the craft. So whenever you
have an extraordinary claim, immediately ask the small questions:

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

Whichever you reach for: infer, don't embrace (Section 7). Name nothing terrible; measure it, invoice
it, minute it, and let the register do the work.

---

## 7. Ethics — an attitude and a craft, not a rulebook

There are almost no hard rules here — hard rules insult your judgement and foreclose brave comedy before
anyone's tried it. What governs the work instead is an *attitude* (Del Close's *"treat your fellow
creators like poets and geniuses"*; taste and peer-adoption, not a banned-words list) and a *technique*
(**infer, don't embrace** — you may *name* a monstrous subject but never *render* it; let paperwork and
the reader's imagination do the work). The north star is Brass Eye's *"Paedogeddon,"* which satirised
society's hysteria about a horror, never the horror or its victims. There is a short plain floor beneath
all the freedom — no real private individuals without consent, no real-world harm instructions, nothing
that is simply cruelty in costume — and a firm recommendation against disclaimers, since a "this is
satire" banner shatters the illusion the work depends on.

**The full treatment is in [`ethics.md`](ethics.md) — read it before you go near a difficult subject.**

---

## 8. Plausible deniability — salt every artifact with tells

Here is the failure mode this whole project has to survive: **what if it works too well?** You build a
straight-faced company that runs the kill-grid, a conspiracy influencer stumbles onto it, doesn't get
the joke, and starts broadcasting your fiction as *proof*. That is the exact inversion of the mission
(Section 0) — mock-not-fuel turned into fuel. The defence is *not* a disclaimer (Section 7 explains why
we don't use them). The defence is **built-in absurdity**: deliberate, discoverable tells planted
*inside* the artifact that anyone paying real attention will catch, and that make the thing impossible
to quote as evidence without quoting the joke along with it.

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

---

## 9. Build your node — a reference, not a template

The worst thing this kit could do is hand you a fill-in-the-blanks template, because then every node
would look the same and the maze would collapse into a form. So instead, here is **one worked example**
and then a **buffet** — take what's useful, ignore the rest, invent your own forms.

**The reference — a worked example, told without names.** The companion file **`worked-example.md`** walks
through how one corner of the world actually grew, one idea at a time — a technical, rediscovered intranet;
then a blogger who "discovers" it; then the creator writing himself in as the villain; then that villain's
own straight-faced corporate consultancy homepage. What makes that shape work is worth stating here: every
piece is **mundane paperwork and public-facing corporate copy**; the villain is played dead straight
(Section 5); the horror is inferred, never stated (Section 7); and the separate pieces **interweave** — a
blogger node and a villain node, made by different hands, cross-linking into something neither author
fully controls (Section 4). That is a node. Yours will look nothing like it, and that's correct.

**The forms buffet.** Any of these can *be* a node, or part of one:

- A company's **staff intranet**: tickets, memos, an org chart, a training module.
- **Blog posts** by a character (a theorist-hero, a whistleblower, a company's own comms officer).
- **Tickets in a bug tracker** — a fault report, a work note, an assignee grumbling in the comments,
  an issue quietly closed as "won't fix."
- **Corporate memos** — the departmental notice, the all-staff bulletin, the passive-aggressive
  reminder about the kettle.
- **Internal emails** — a leaked thread, a forwarded chain with the damning line three replies down, a
  dead mailbox's auto-reply.
- **Dry records of any kind** — accounting ledgers and annual accounts, expense tables, clinical /
  medical case files, logs, manifests, rotas. Any of them can carry a whole story on their own (see
  Section 6).
- A **consultancy or product website**, played straight.
- **Regulatory filings**: incorporation certificates, court judgments, licence applications.
- A **fabricated technical document** — a standards spec, a white paper, an academic pastiche (fully
  invented authors and citations).
- A **dead web service** (a SOAP endpoint, an API that only ever returns `AUTHENTICATION_REQUIRED`).
- **Marketing / HR ephemera**: a "benefits of enrolment" brochure, a graduate-scheme cohort page.

**A caveat about this list — mind the corporate bias.** These examples lean heavily on the modern
office: intranets, tickets, memos, invoices. That's because the settings they're drawn from happen to be
offices, not because the game is. Every *setting* has its own native diegetic media, and the real move is
to imagine your setting and
ask what paperwork it would generate. A religious order leaves sermons, tithing ledgers, and pastoral
letters. A 19th-century expedition leaves logbooks, requisition chits, and letters home. A hospital
leaves charts and discharge summaries; a navy leaves signals and watch rotas; a school leaves reports
and detention slips; a game world leaves patch notes and moderation logs. Whatever world you're in,
there is almost certainly a set of dull, authentic documents it produces — find those, and you've found
your forms.

**You can write yourself in — or not.** You may cast a fictionalised you as the hero, or make an
invented conspiracy theorist the hero, or have *no hero at all*. The entire story of a node can be told
in nothing but accounting records, with no protagonist whatsoever. There is no limit and no required
shape.

---

## 10. Show, don't tell — never narrate, always imply

The one non-negotiable: **show, don't tell.** Never explain the premise, never narrate the menace, never
wink. The world is revealed only through the mundane things it contains — the ticket, the memo, the
invoice, the expired certificate — and the reader assembles the story and reaches their *own* conclusion,
which is exactly why it's unshakeable. An accounting ledger that says nothing and means everything beats
a paragraph of sinister narration every time.

**The full method — what an alternate reality game is, why we tell it with no narrator, and how to work
from a private backstory to the public artifacts that imply it — is in [`storytelling.md`](storytelling.md).**

---

## 11. Inside the world and outside it — mind the membrane

Everything you make falls on one side or the other of a membrane, and knowing which side a thing is on is
the difference between immersion and a broken fourth wall.

**Inside the world (diegetic).** The artifacts the audience is *meant to encounter as real*: the fake
intranet, the consultancy website, the fabricated filings, the blog in a character's voice, the leaked
memo, the dead SOAP service. These must never break character — no "this is satire" label, no wink, no
author's aside, not in the page, not in a view-source comment, not in a filename or an HTTP header. The
only tells permitted inside the world are the *deliberate absurdist ones* from Section 8; those are part
of the joke, not confessions that it is one.

**Outside the world (the scaffolding).** The things you need in order to build the fiction, which the
audience is never meant to meet: source code, build systems, deployment configs, Terraform, the prompts
you fed the LLM, your private notes — **and this very document.** The manifesto, the charter, the
continuity checker *explain the operating principles* and therefore shatter the illusion by their nature.
They are the editor's desk, not the stage. They belong in a repository's `doc/` folder or a private
notebook — never on a client-facing surface. If a visitor to your world can reach the document that
explains the joke, the joke is over. (Stated as a rule: *never break immersion — the only place to
document the joke is private editor notes that never reach the client.*)

**But the membrane can be crossed on purpose.** The line is *not* "code is always outside." The line is
the single question: *is the audience meant to encounter this as part of the story?* — and sometimes the
answer turns scaffolding into set-dressing. Source code is usually outside the world, but it can be
pulled inside and made a diegetic device. Suppose your node is the company that operates the 5G
energy-weapon grid. You might publish the **device drivers and control software** for that grid — the
firmware, the calibration routines, the actuation API — as a leaked or "accidentally open-sourced"
repository. That is source code for a weapon network *that never existed*, and it is emphatically
**inside** the world: an in-universe artifact the reader is meant to find and read as real, and so it
must obey every in-world rule — stay in character, carry its own tells (a register that can't exist, a
physical constant that's wrong, a code comment signed by a director off Section 8's board), and never,
ever explain itself. A fake build pipeline, a diegetic bug tracker, a "release specification" for the
kill-grid are all the same: the instant code is offered to the audience *as part of the fiction*, it has
crossed the membrane and lives on the stage.

So before you publish anything, ask which side it's on. Out-of-world scaffolding: keep it in `doc/` or
keep it private, and let it explain freely. In-world artifact: it lives on the stage, in character,
forever — even when it happens to be a thousand lines of C for a death-ray that was always a joke.

---

## 12. How we communicate together

The community side of the project has its own document: **`communications.md`**. It covers interweaving
etiquette (offer freely, hold loosely, celebrate the mutation), how we organise in loose **cells** with
no boss and no central forum, and the fact that we are all one another's audience — sometimes building
on total strangers who never signed up. The short version: when you find work you love but can't tell
who made it, don't wait for permission — build your own, fold theirs in, and leave a few clues. See
`communications.md` for the whole of it.

---

## 13. Poe's Law as the goal — indistinguishable, and that's the point

How we're organised (see `communications.md`) leads straight to an obvious, slightly vertiginous
question: **what if some of the people we
think we're playing with are real conspiracy theorists?** What if, somewhere in the mesh, our
imaginative fabrications end up shoulder to shoulder with the genuine article — the earnest believer who
really does think 5G is a kill-grid, or who has assembled some sincere anti-vax, faked-moon-landing
edifice out of their own entirely un-ironic imagination? What are the odds our satire and their sincerity
become impossible to tell apart?

Here is the thing: **that is not the failure mode. That is the win.** There's a well-known observation —
*Poe's Law* — that without a clear signal of intent, a parody of an extreme view becomes indistinguishable
from a sincere statement of it. The internet mostly treats this as a hazard. We treat it as the target.
If, working as improvising comedians, we build something that a committed conspiracy practitioner cannot
tell apart from "real" conspiracy theory, we have produced the ultimate form of satire — because we have
proved the very thing we set out to prove: that these beliefs are so untethered from reason, so purely
and gorgeously ludicrous, that *even their most ardent adherents cannot separate the genuine article from
a joke we invented on a Tuesday.* The believer who nods along to our fabricated kill-grid has, in that
nod, delivered the verdict on their own method: there is no test they can apply, no auditor, no way to
tell. That is the whole indictment, and they hand it to us themselves. Call it, if you like, *conspiracy
supremacy* — the point at which our elaborate nonsense is woven so deep into the cultural landscape that
it is load-bearing.

But "indistinguishable" is only safe — and only *satire* — because of one thing, and it is the thing
Section 8 exists for: **the tells are always already inside.** Every node is salted with its Easter eggs
— the *Dad's Army* board, the impossible incorporation in 1600, the QR code that decodes to a limerick —
quietly waiting. The work can pass for the real thing at a glance precisely *because* the proof that it
never was the real thing is baked in, primed, and ours to detonate whenever we choose. So the satire
lies dormant, in perfect camouflage, woven into the landscape — and then, the moment we decide to pull
the pin, the camouflage falls away and the whole edifice stands revealed for exactly what it always was:
a joke, and, by that same stroke, a mirror held up to the "real" theories it was indistinguishable from.
Indistinguishable going in; unmistakable coming out. **That gap is the payload** — and it is why we can
camouflage so perfectly and still, always, be telling the truth.

---

## 14. The LLM as co-author, and the continuity checker as a personal tool

Lean on the model as a genuine collaborator, not a typist. Ask it to generate three versions and pick
the most boring. Ask it what the Thursday cafeteria menu would be. Ask it who signs the purchase order.
Ask it to draft the whole fake standards document and then to insert the deadpan-impossible clause that
tells the expert reader it's a fake.

There is a **continuity-checker** prompt alongside this one (see `story-continuity-checker-prompt.md`)
that will cross-check the dates, names, company numbers, and publication order of your *own* node and
propose fixes (with a "retcon vs harmonise" choice for each — and remember Section 4: harmonising is
often the richer option). Treat it as a **personal tool, not a gate.** It's there to stop *you* tripping
over your own timeline. It is emphatically **not** a conformance check against the rest of the world —
global contradictions between your node and someone else's are fine, even desirable (Section 1). Use it
to keep your own room coherent, and let the mansion stay gloriously impossible.

---

## 15. Growing the world

There is no anointment here and no promotion ladder. You don't earn a rank, and nobody hands you the
keys. The only way the world grows is the improv way: **make work that other people want to "yes, and."**
Leave hooks other creators can grab. Turn your camera onto their nodes and tell them. Build the boring,
specific, mundane detail that makes your corner feel real enough to inhabit. And then let the audience
do what only the audience can do — decide, by reading and following the threads, what lives.

**The closing ethos, and the whole thing in one breath:**

> Build on what inspires you; imagine out of existence what doesn't; respect every creator's freedom,
> and try your hardest to build on theirs.

---

*When you're ready, tell the LLM: "Let's begin." It will start with the interview in Section 3 —
firewalling your real identity first, then mapping your corner, then generating the first thing to
build.*
