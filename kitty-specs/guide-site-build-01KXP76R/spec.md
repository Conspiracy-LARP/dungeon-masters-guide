# Specification: Guide Site, Book, and LLM Bootstrap

**Mission**: `guide-site-build-01KXP76R`
**Created**: 2026-07-16
**Status**: Draft — ready for `/spec-kitty.plan`
**Source of requirements**: `doc/build.md` (the project's own build brief), confirmed through discovery.

---

## Why this exists

The guide's text is finished, but it reaches nobody: it exists only as markdown in a git repository.
Someone deciding whether to join the project cannot read it comfortably, someone who reads on paper
cannot print it, and — most importantly — a creator cannot point their LLM at it and start building.

This mission publishes the guide. It does not write, edit, or restructure the guide's content.

## Domain Language

Terminology matters here because several words are already overloaded. These are canonical:

| Term | Means | Not to be confused with |
|---|---|---|
| **the pack** | The guide's canonical markdown, held in `src/pack/` | The `pack` **branch**, which is one published output |
| **the kit** | The pack as a creator experiences it, attached to their own project | — |
| **chapter** | One of the ten documents that form the book, in reading order | Any `.md` in the pack; two are deliberately not chapters |
| **the bootstrap** | The single document a creator hands to an LLM to begin | The human on-ramp, which is a separate chapter |
| **node** | A creator's own fictional property, built *using* the guide | This guide, which is a manual about building nodes |
| **out-of-world** | Scaffolding the audience must never meet | — |

A note the implementer must not lose: **this entire repository is out-of-world**, and the guide's own
site is openly a manual. That is why the site may explain itself freely — it is the one surface in the
project permitted to do so.

## User Scenarios & Testing

### Primary scenario — the machine front door (the load-bearing flow)

A creator has an idea and an LLM, and nothing else. They say to the model: *"read `<the one URL>` and do
what it says."* The model fetches one page, and from that alone: creates a correctly structured private
workspace, attaches the kit to it, reads the guide, and **asks the creator about their real-identity
boundaries before writing anything at all.** The creator ends the session with a workspace and an
interview underway, having read nothing themselves.

This is the scenario the mission exists for. If it fails, the mission has failed regardless of how the
site looks.

### Secondary scenario — the human evaluating the project

Someone hears about the project and lands on the site. They read the pitch, follow the nav in reading
order, and decide whether to join. On a phone, on a laptop, whichever. They can search. If they want to
go deeper, they take the book away and read it cover to cover.

### Third scenario — the reader on paper

Someone prints the book and reads it in a chair. There is a title page, a contents list with page
numbers they can act on, and no instruction anywhere that assumes they can click.

### Fourth scenario — the creator staying current

A creator who attached the kit months ago runs one command and receives the current guide, with nothing
in their project broken by the update.

### Exception paths that must be handled

- **A new document is added to the pack** and nobody declares whether it is a chapter. The build must
  fail loudly rather than silently omit it from the book.
- **The guide's own machinery leaks** into what creators receive. Must be impossible, not merely avoided.
- **A cross-reference is edited into a path** (e.g. `src/pack/ethics.md`). This breaks four surfaces at
  once and must be caught by the build, not by a reader.
- **The bootstrap's own instructions stop working** — e.g. it tells a model to attach a branch that does
  not exist. The build must verify the instructions it publishes actually run.

## Requirements

### Functional

| ID | Requirement | Status |
|---|---|---|
| FR-001 | Publish a browsable website generated from the pack, with search and a left-hand nav in the defined ten-chapter reading order. The landing page is the guide's own "What is this?" pitch. | Accepted |
| FR-002 | Every published page offers its own clean markdown source: a visible link a human can follow, and machine-discoverable metadata a model can act on without reading the page. | Accepted |
| FR-003 | ~~Publish the whole guide as a single-file document.~~ **DESCOPED 2026-07-17** by the stakeholder: the website and the LLM-readable markdown are the deliverables; nobody reads the book. | Descoped |
| FR-004 | ~~Publish a printable PDF.~~ **DESCOPED 2026-07-17.** Beyond nobody wanting it, the PDF is the only reason CI needs a 1.1GB pandoc/TeX image — measured by WP04 at ~58s cold against ~6s for the render itself. Dropping it removes the main risk to NFR-005. WP04's code is complete and stays in the repo; it is simply not in the pipeline. | Descoped |
| FR-005 | Publish a machine-readable index of the guide, following the `llms.txt` convention, whose first and most prominent entry is the bootstrap. | Accepted |
| FR-006 | Publish the entire guide concatenated into one machine-readable file, in reading order. | Accepted |
| FR-007 | Serve every document's raw markdown at a predictable parallel address, delivered as text a model can read directly — not as a download, and not converted to a rendered page. | Accepted |
| FR-008 | Serve the bootstrap at a stable, conventional address such that a model handed only that address can complete the primary scenario with no other context. | Accepted |
| FR-009 | Publish the pack as a branch creators can attach to their own project: the guide's markdown alone, flat, carrying no build machinery and no internal documentation. | Accepted |
| FR-010 | On that branch, the bootstrap is published under the conventional name models look for, and every reference to it is rewritten to match, so that links resolve on **both** the source branch and the published branch. | Accepted |
| FR-011 | Every document in the pack must have a declared role — chapter, or explicitly not-a-chapter. A document with no declared role fails the build. | Accepted |
| FR-012 | Republish all surfaces automatically whenever the guide's source changes, so no surface can lag another. | Accepted |
| FR-013 | Verify, as part of the build, that cross-references resolve on every published surface. | Accepted |

### Non-Functional

| ID | Requirement | Threshold | Status |
|---|---|---|---|
| NFR-001 | Relocatable address | Every absolute address derives from one configured value. Moving the guide to a different address is a one-value change, verified by changing it and rebuilding. | Accepted |
| NFR-002 | Readable on a phone | Every chapter readable at 320px width with no horizontal scrolling. | Accepted |
| NFR-003 | Nothing hand-authored downstream | 100% of every published surface traces to a source document in the pack. Zero hand-written pages. | Accepted |
| NFR-004 | Visual investment is bounded | Stock theme plus palette and typography only. No bespoke design work in this mission. | Accepted |
| NFR-005 | Publication latency | A change to the guide is live on all surfaces within 5 minutes of landing. | Accepted |
| NFR-006 | Legibility | Body text meets WCAG AA contrast in both light and dark presentation. | Accepted |

### Constraints

| ID | Constraint | Rationale | Status |
|---|---|---|---|
| C-001 | The pack stays flat, and its cross-references stay bare sibling links carrying no path. | This single property is what lets the same bytes serve all four surfaces without a rewrite step. Breaking it breaks all four at once. | Accepted |
| C-002 | The build must never require editing the guide's prose. Ordering and metadata live in configuration. | The prose is the product; the build serves it, not the reverse. | Accepted |
| C-003 | Hosting is stateless static content on GitHub Pages, as a project site served from a subpath, with no custom domain yet. | Chosen by the stakeholder: free, no infrastructure, source already there. A domain may follow later — hence NFR-001. | Accepted |
| C-004 | The bootstrap must not carry the conventional agent filename in the source repository — only on the published branch. | Agent files auto-load from subdirectories. The bootstrap's first instruction creates directories; it must never fire at someone editing the guide. | Accepted |
| C-005 | The published branch must be reproduced byte-for-byte by automation, then maintained by it. | The branch was bootstrapped by hand on 2026-07-16 (commit `d024682`) to unblock a downstream project. Automation must take it over, not diverge from it. | Accepted |
| C-006 | This mission does not change the guide's content. | Content and publication are separate concerns; conflating them makes both unreviewable. | Accepted |

## Success Criteria

Measured from the outside, without reference to how any of it is built:

| ID | Criterion | How it is verified |
|---|---|---|
| SC-001 | A fresh LLM session, given nothing but the one address, produces a correctly structured workspace with the kit attached, and asks about real-identity boundaries **before** writing any artifact. | Run against a real model, end to end. Not a structural check. |
| SC-002 | A creator attaches the kit to their own project with a single command that succeeds first time. | Execute the published command against the published branch from a clean checkout. |
| SC-003 | ~~Printed and read on paper.~~ **DESCOPED** with FR-003/FR-004. | n/a |
| SC-004 | No two published surfaces can disagree about the guide's content. | All surfaces are generated from the same source; verified by the absence of any hand-authored output. |
| SC-005 | A reader on a phone can read any chapter without horizontal scrolling. | Inspect at 320px. |
| SC-006 | The guide can be moved to a new address by changing one value. | Change it, rebuild, confirm every generated address follows. |
| SC-007 | A change to the guide reaches every surface within 5 minutes, with no human step. | Land a change; observe. |

## Key Entities

- **Document** — one markdown file in the pack. Has exactly one **role**: `chapter` (part of the book, at
  a defined position in the reading order) or `not-a-chapter` (published, but outside the book's flow).
  Today the not-a-chapter set is the pack's own index and the bootstrap. A document with no role is an
  error.
- **Reading order** — the sequence of chapters. Currently duplicated in prose in several places; see
  Assumptions.
- **Surface** — a published rendering of the pack: the site, the book, the printable edition, the machine
  index, the concatenated source, the raw documents, and the attachable branch.

## Assumptions

- **A-001**: The guide's content is stable enough to publish. Content changes continue independently and
  the pipeline simply republishes them.
- **A-002**: The reading order becomes **configuration** — one machine-readable declaration — and the
  prose lists that currently repeat it are checked against that declaration rather than hand-maintained.
  This was flagged as "proposed, not agreed" before this mission; the mission adopts it, because the
  build needs the order in configuration anyway (C-002) and adding another hand-maintained copy would
  make five. If the stakeholder rejects this, FR-011's lint still stands but the duplication persists.
- **A-003**: The two current not-a-chapter documents are the pack's index and the bootstrap. New
  documents default to *chapter* unless declared otherwise, and FR-011 forces the declaration.
- **A-004**: "Attractive" is satisfied by a stock theme, considered palette and typography, and good
  readability (NFR-002, NFR-004, NFR-006). A distinctive visual identity is explicitly deferred.

## Dependencies

- **D-001**: A published branch that creators attach to. It exists today by hand (C-005); automation must
  take it over.
- **D-002**: GitHub Pages must be enabled for the repository and permitted to publish from automation.
- **D-003**: The behavioural acceptance test (SC-001) requires access to a real LLM session.

## Risks

- **R-001 — the load-bearing address may not survive its host.** FR-007 and FR-008 require raw markdown
  served as readable text. The hosting platform decides the content type for `.md`, and if it serves them
  as downloads or renders them, the entire machine-facing surface fails **while the site still looks
  perfect**. This is the highest-risk requirement in the mission and the least visible failure. Prove it
  before any effort goes into presentation.
- **R-002 — the published instructions may describe something that does not exist.** The guide already
  tells creators to run a command against the published branch. That is true today only because it was
  bootstrapped by hand. If automation diverges, the guide starts lying to its readers.
- **R-003 — silent omission.** A document added to the pack without a declared role could quietly vanish
  from the book. FR-011 exists to convert that into a loud failure.

## Out of Scope

- Writing or editing the guide's content (C-006).
- A bespoke visual identity (NFR-004, A-004).
- A custom domain (C-003) — though NFR-001 must keep the door open.
- Any dynamic behaviour: comments, search-as-a-service, analytics, accounts (C-003, stateless static).
- Translations, versioned editions, or an epub.
