# Technical suggestions — how to build the thing, cheaply

*Companion to `creator-kit.md`. This file is **all optional** — conveniences, not commandments. It exists
to give you and your LLM a running start so you're publishing within the hour instead of the week. If
you're an experienced developer with your own way of working, ignore every word of this and you're still
playing the game exactly right.*

**The running theme of this whole pack is: keep costs low.** Most nodes you dream up won't get real
traction — that's fine, that's improv — so you want each one to cost as close to nothing as possible to
stand up and to leave running. Optimise for cheap-to-start and cheap-to-idle. Everything below serves
that.

---

## These are out-of-world details

Everything here is **out-of-world scaffolding** — hosting, build tooling, deployment, analytics. None of
it should ever surface on a client-facing page (see the "membrane" section of the creator kit). The
one interesting exception is when you deliberately make source code itself a diegetic artifact; that's
covered in the kit.

---

## Fake the period — don't actually use old technology

A lot of nodes want a *dated* look — a site that appears to have been built with twenty-year-old
technology, a neglected 2012 intranet, a 1998 GeoCities page. **You do not have to use old technology to
look old.** Build with a completely modern stack and *costume* it: period fonts, table layouts, beveled
borders, a fake `Server: Microsoft-IIS/7.5` header, `[CACHED]` tags, broken-looking widgets. You get the
best of both worlds — a convincingly ancient façade, deployed on modern infrastructure that's cheap,
fast, and easy to stand up. A node can be a thoroughly modern Python/JS app wearing a 2012 IIS costume:
the visitor sees rust, you get containers and a CDN. Self-host your fonts and libraries rather than
hot-linking a CDN, both to stay in period and to keep control.

---

## Let the LLM deploy it

Modern LLMs are genuinely good at deploying to cloud platforms — writing the Dockerfile, the config, the
DNS records, the deploy commands, and talking to the provider's CLI. You do not need to know the incantations.
Describe what you want ("a static site on Fly behind Cloudflare, on this domain") and let the model do the
plumbing. This is a large part of why standing up many small properties is now realistic for one person.

It's **expected, but not required,** that most players will build with a large language model agent system
— Claude Code, Codex, or similar. Nobody says you have to; but the whole premise of "you supply the idea,
the model does the building" leans on one, and it's what makes running many properties realistic for a
single person.

If you do use one, you might also consider pairing it with a **planning system** such as **Spec Kitty**
(<https://github.com/Priivacy-ai/spec-kitty>). The benefit: instead of hand-managing the work, you define a
project — or a single component — as a *spec*, through an ordinary conversation, then let the system loose
to break it into tasks and build them. After a morning of LLM crunching, the thing you imagined more or
less just… exists. It automates a pile of planning — not necessarily *hard* planning, but the sort that
otherwise slows you down — and simply gets you there faster. As with everything in this pack: only a
suggestion.

---

## Ship each property as an immutable, resettable bundle

Here is the pattern that makes these properties both realistic *and* carefree to run: **build each one as
a self-contained, immutable bundle — a Docker image — that resets to a known-good state every time you
deploy it.** Don't worry if you don't know what Docker is or how it works; you can trust the LLM to know
precisely how to use it. The idea to hold onto is simply this: each thing you create can exist as a single,
immutable, resettable **creative bundle** — you build it, you ship it to the cloud, it runs. Three things
make that pattern powerful.

**Build with real software — reskinned.** Diegetic fiction feels more real when it *is* real. To tell the
story of an evil corporation through its issue tracker, you don't have to write a fake issue tracker — take
a real **open-source** one and **reskin it** with the fictional corporation's logo and colours. The
buttons work, the search works, the timestamps behave, because it's a genuine application; you've merely
dressed it in costume. The same trick works with a real wiki, a real forum, a real helpdesk. Real software
wearing a fictional skin is far more convincing than anything you could fake, and the LLM can wire it up.

**Bake the story into the build.** Then make the *content* part of the image. Every time the property's
Docker image is built, a step of that build loads your seed data — the tickets and their comments, the
memos, the accounts — into that real software. The story is baked in. When the system goes live it looks
like a perfectly ordinary, fully-functioning issue tracker (or wiki, or forum) with a rich history —
because it genuinely is one — and every time you republish the image it **resets to exactly your seed
state.** Everything a visitor sees is literally real data in real software; it's just real data *you
authored*, restored fresh on every deploy. The realism is free, because none of it is faked.

**And a gift for the audience: safe vandalism.** An immutable, resettable property lets you do something
lovely. You can let a player *attack* the system — deface it, "hack" it, tear it down — completely safe in
the knowledge that the next reset restores everything as if the vandalism had never happened. It can be
genuinely cathartic for the player, and quietly delightful for you to watch. Imagine there had been an
*undo button* on the destruction of the Georgia Guidestones — the monument conspiracy folklore had made a
target, smashed one morning in the real world and gone for good. A resettable bundle gives you exactly
that button: a world that can be broken for the sheer fun of breaking it, and is whole again by morning.

---

## Where to host — pick the cheap platforms

- **Avoid AWS for this.** It's the most famous cloud, but it's built for corporate use: powerful,
  sprawling, and easy to run up a surprising bill on. For small satirical properties it's overkill and
  overpriced.
- **Fly.io** (<https://fly.io/docs/>) — cheap container hosting with **scale-to-zero**, so an idle node
  costs almost nothing. Great default.
- **Railway** (<https://railway.com/>) — similarly affordable and very easy to deploy to; another good
  choice for small apps and databases.
- **Static hosting** for anything that doesn't need a server at all (see below) is cheaper still, often
  free.

The guiding principle remains: **self-host on infrastructure you control, behind your own domain.** It
costs little and keeps the decisions in your hands.

---

## Cloudflare — resilience, speed, and faster indexing

Put **Cloudflare's free tier** (<https://developers.cloudflare.com/>) in front of every property. It
gives you DNS, free TLS, a global CDN, and edge caching, and it does three valuable things:

1. **Resilience.** With edge caching on, Cloudflare serves your pages even when your origin is asleep or
   down. This pairs beautifully with **scale-to-zero**: your web server can be completely offline to save
   money, and players still see the site — Cloudflare serves the cached copy and only wakes the origin on
   a cache miss. Cheap *and* always-up.
2. **Speed.** Pages are served from an edge near the visitor.
3. **Faster indexing.** A fast, stable, well-formed site behind Cloudflare tends to get discovered and
   indexed by search engines sooner.

---

## Not everything needs a CMS

Reach for a content-managed system only when a node genuinely needs one. A great many properties are just
**a simple collection of static HTML pages** — an intranet, a set of fabricated filings, a brochure site.
Build those as plain static content (hand-written HTML, or a generator like <https://gohugo.io/> or
<https://www.11ty.dev/>) and launch them in the simplest, cheapest possible way: a tiny static container,
or free static hosting, behind Cloudflare. Static is the cheapest, fastest, most durable option, and an
LLM can produce a whole static node end to end.

---

## Blogging engines for character voices

When a node needs a blog written in a character's point of view, **self-host** it:

- **Self-hosted WordPress** (<https://wordpress.org/documentation/>) — mature, endlessly themeable.
- **Self-hosted Ghost** (<https://ghost.org/docs/install/>) — lighter, cleaner, deploys neatly on Fly.

Either gives you a real, believable, fully-owned blog. (On *why not* a hosted SaaS blog, see below.)

### Share the expensive component across many blogs

As you accumulate properties, watch for the one costly piece and share it. For a stable of blogging
engines — say a dozen blogs, each the voice of a different character with a slightly different point of
view — the most expensive component is usually the **database server** (MySQL / MariaDB). You do **not**
need one per blog. Run **a single database server** and give each blog its own database on it; you pay
for one server, not twelve. Everything else — the web frontends — stays light and **scales to zero**, so
an idle blog costs almost nothing, and the shared database is your only always-on line item.

---

## A suggested project layout

Keep a **private parent repository** of your own (any git host), with the shared creator-kit added as a
**submodule** on your own desk — inside `doc/`, because the kit is out-of-world scaffolding like
everything else in there:

```
my-node/                     ← your private parent repo
├─ doc/                      ← OUT-OF-WORLD: the editor's desk
│  ├─ core/                  ←   the shared kit, as a git submodule (read-only reference)
│  └─ lore/                  ←   private back-story, timelines, character bios
├─ sites/                    ← IN-WORLD: the artifacts the audience sees (each a deployable)
├─ build/                    ← OUT-OF-WORLD: Dockerfiles, deploy scripts, prompts
└─ README.md                 ← OUT-OF-WORLD: notes to yourself
```

Add it by tracking the kit's **`pack` branch**, which carries the markdown documents and nothing else —
no build machinery, no meta-documentation, just the reference you actually read:

```
git submodule add -b pack <the creator-kit repo> doc/core
git submodule update --remote doc/core        # later: pull the current version of the kit
```

Honour the membrane (kit): keep out-of-world scaffolding clearly separated from in-world artifacts. Track
the back-story you imply but never show in `doc/lore/`; the continuity checker is built for exactly that.

---

## Git hosting and pull requests — a channel for interlinking

Your parent repo can be self-hosted, but there's a specific reason to keep it on a **major host — GitHub,
GitLab, Bitbucket**: you can **receive pull requests from other players.** That turns the humble git repo
into an interlinking mechanism. If another creator has a funny idea that would land best as, say, a new
entry in *your* fictional ticketing system, they don't have to ask you to build it — they can open a
**pull request** against your repo with the change already made, and you merge it, or don't. It's "turning
the camera" (see `improvisation.md`) implemented in plumbing: a low-friction, no-permission-needed way for
one creator to offer a concrete contribution to another's world. You stay fully in control — nothing lands
without your merge — but the door is open. And the pull request itself can be part of the fun: a change
proposed to an evil corporation's issue tracker, arriving from an unknown outside contributor, is a rather
nice piece of diegetic texture all on its own.

---

## Measure and get indexed

For each property you can get real insight and make sure it's findable:

- **Google Analytics** (<https://analytics.google.com/>) — see how a property is actually used. A single
  measurement snippet per site.
- **Google Search Console** (<https://search.google.com/search-console>) — verify the site, submit a
  sitemap, and confirm Google is indexing it.
- **Bing Webmaster Tools** (<https://www.bing.com/webmasters>) — the same for Bing (and you can often
  import the Search Console setup directly).

A sitemap plus these three, behind Cloudflare, is usually enough to get a new property discovered and
indexed within days.

---

## Archive.org — free permanence, and a storytelling device

Beyond the live search engines, put important pages into the **Internet Archive's Wayback Machine**
(<https://web.archive.org/>). Saving a URL takes seconds, is free, and is effectively **permanent**: the
snapshot persists even after you stop paying for hosting, retire the node, or take the page down. For a
project built on standing up cheap, disposable properties, that's a zero-cost way to make anything you
care about outlive its own web server. (<https://archive.today/> is a comparable alternative.)

But here is where a dull technical tool becomes a **storytelling device**, and the membrane blurs on
purpose. Archive a page — and *then remove the live version*. Now the only place that page exists is the
archive, and a Wayback snapshot of a page that is "no longer there" reads exactly like the most authentic
artifact in all of conspiracy culture: **the secret, deleted content they didn't want you to see.** "I
saved it before they scrubbed it" is the genre's favourite sentence, and the Wayback Machine hands it to
you for free. A live page is just a website; the *ghost* of a page, preserved in the archive after its
removal, is *evidence*. (A conspiracy-blogger character can use exactly this move in-world — a record
"removed at the request of the registrar" that the character had the foresight to save.) Used deliberately, the
archived copy is now an **in-world artifact**, so it must carry its tells (`storytelling.md`) and stay in character
like anything else on the stage.

Two cautions, because permanence cuts both ways:

- **It is genuinely hard to undo.** Only archive things you're happy to have persist essentially forever —
  clean, in-world, tells intact, and with **no real-identity leak**, because the archive will faithfully
  keep any mistake you make.
- **Archive the finished artifact, not the scaffolding.** Snapshot the in-world page; never the repo, the
  build files, or anything from the kit itself.

---

## Why NOT a hosted SaaS blog/login platform

Avoid the hosted platforms — Substack, Medium, WordPress **.com**, Ghost(Pro), hosted forums, the big
social networks — as the *home* of an in-world artifact. Three reasons:

1. **Censorship and deplatforming.** They police content against their own rules and can remove you with
   no warning and no appeal. Your work becomes a hostage to someone else's moderation queue.
2. **Misidentification.** A well-made diegetic satire is *designed* to look, at a glance, like the real
   thing (see the kit on Poe's Law). A platform's automated moderation — or a confused reporter — may
   mistake your satire for a genuine conspiracy site and pull it down. On your own domain you decide.
3. **Ownership.** Self-hosting means you own the domain, the data, and the ability to move.

Your Easter-egg tells are your defence against a *human* who reads carefully — a platform's filter won't
read carefully. Self-hosting is how you keep control of a thing meant to be mistakable for real.

---

## Domains — cheap first, transfer later

- Buy from a **cheap registrar that offers a low first-year promo** (e.g. Porkbun, <https://porkbun.com/>).
  A real domain sells the illusion far better than a `*.some-platform.com` subdomain.
- **Optimise for the short term.** Most ideas won't get traction, and you probably won't want to keep
  paying for them after year one — so buy on whatever's cheapest to *start*, and don't over-commit.
- **If a node earns its keep, move it.** When something does gain an audience, transfer the registration
  to a registrar that's cheap for *ongoing renewal* (Cloudflare Registrar sells domains at wholesale cost,
  for example). Optimise year one for cheapest-to-start; optimise year two-plus for cheapest-to-keep.

---

## A worked example — a stable of different-looking blogs

Say you want several blogs, each the voice of a different character, each looking nothing like the others.
A cheap way to stand that up:

1. **One shared database.** A single small MariaDB/MySQL instance (or one cheap managed database) holding
   one database per blog. This is your only always-on cost.
2. **N lightweight frontends.** A self-hosted Ghost or WordPress container per blog on Fly (or Railway),
   each **scaled to zero**, each with its own theme so they look completely distinct, each pointed at its
   own database on the shared server.
3. **Cloudflare in front of each**, on its own cheap first-year domain — cache on, so an idle (asleep)
   blog still serves pages instantly and only wakes the origin on a miss.
4. **Static where you can.** Any node that's really just pages skips the database and CMS entirely — plain
   static HTML behind Cloudflare, cheaper still.
5. **Analytics + Search Console + Bing** on each, so you can see which ones catch on — and quietly retire
   the ones that don't when the first year's domain lapses.

The result: a dozen visually-distinct, believable, independently-owned properties, running for roughly the
price of one small database plus a handful of near-idle containers.

---

## External references

- Fly.io — <https://fly.io/docs/> · Railway — <https://railway.com/>
- Cloudflare developer docs — <https://developers.cloudflare.com/>
- Ghost (self-hosted) — <https://ghost.org/docs/install/> · WordPress — <https://wordpress.org/documentation/>
- Docker — <https://docs.docker.com/> · Caddy — <https://caddyserver.com/docs/>
- Hugo — <https://gohugo.io/> · Eleventy — <https://www.11ty.dev/>
- Google Analytics — <https://analytics.google.com/> · Search Console — <https://search.google.com/search-console>
- Bing Webmaster Tools — <https://www.bing.com/webmasters> · Porkbun — <https://porkbun.com/>
- Internet Archive / Wayback Machine — <https://web.archive.org/> · archive.today — <https://archive.today/>

---

*Again: none of this is required. It's a shortcut from people who've already made the mistakes, to get you
creating sooner and cheaper. The only actual goal is to get a story onto the web — and to keep it cheap
enough that you never have to think twice about trying the next one.*
