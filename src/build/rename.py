"""Rewriting references to the bootstrap when it changes name (FR-010).

The bootstrap is ``start.md`` on ``main`` and ``AGENTS.md`` on the pack branch. That is
deliberate, not an inconsistency to tidy up: agent tools auto-load nested ``AGENTS.md``
for the subtree being edited, and this document's first instruction is
``mkdir -p my-node/...`` — named ``AGENTS.md`` in ``src/pack/``, it would fire at whoever
is *editing the guide* and start scaffolding someone's node (C-004).

Renaming the file is half the job. Rewriting the references is the other half; skipping
it ships broken links on one branch.

This module is pure: text in, text out. No filesystem, no git — WP06 owns the tree.
"""

from __future__ import annotations

import re
from typing import Final

#: The bootstrap's name in the pack, on `main`.
SOURCE_NAME: Final[str] = "start.md"

#: The bootstrap's published name, on the pack branch and at `{base}AGENTS.md`.
PUBLISHED_NAME: Final[str] = "AGENTS.md"

#: THE TRAP, and why this pattern is not a plain `str.replace`.
#:
#: `getting-started.md` CONTAINS the substring `started.md`... and more to the point a
#: naive replace of `start.md` corrupts `getting-started.md` into
#: `getting-AGENTS.md`. This is not hypothetical: the pack branch was built by hand on
#: 2026-07-16 and this exact case had to be handled; `sed s/start.md/AGENTS.md/g`
#: silently produces a broken link that no test would have caught.
#:
#: The lookbehind requires that `start.md` is not preceded by a word character or a
#: hyphen, so `getting-started.md` (preceded by `-`) and `restart.md` (preceded by `t`)
#: are both left alone.
#:
#: The lookahead has two halves, and both are load-bearing:
#:   `(?!\w)`   — `start.markdown` is a different file.
#:   `(?!\.\w)` — `start.md.bak` is a different file, but a trailing sentence period
#:                (`read start.md.`) must still rewrite. Requiring "no dot followed by
#:                a word character" separates those two cases; a plain `(?![\w.])`
#:                would refuse to rewrite the end of a sentence, which is where the
#:                guide's prose most often names the file.
#:
#: `src/pack/start.md` itself references `getting-started.md` three times today, so the
#: trap is live in the real content, not merely theoretical.
_REFERENCE_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?<![\w\-])start\.md(?!\w)(?!\.\w)")


def rewrite_references(text: str) -> str:
    """Rewrite every reference to ``start.md`` so it points at ``AGENTS.md``.

    Rewrites both link targets — ``[the brief](start.md)`` — and inline mentions —
    ``` `start.md` ``` — because the guide's prose names the file in running text as
    well as linking to it.

    Crucially it does **not** touch ``getting-started.md``, ``restart.md``, or any other
    name that merely ends in ``start.md``.

    Args:
        text: the markdown source of one document.

    Returns:
        The same text with bootstrap references repointed. Unchanged if there are none.

    >>> rewrite_references("see [the brief](start.md)")
    'see [the brief](AGENTS.md)'
    >>> rewrite_references("see [on-ramp](getting-started.md)")
    'see [on-ramp](getting-started.md)'
    """
    return _REFERENCE_PATTERN.sub(PUBLISHED_NAME, text)


def published_name(filename: str) -> str:
    """The name ``filename`` is published under.

    Identical to ``filename`` for every document except the bootstrap (FR-010).

    Defined here, and used by both the site (WP03, which publishes the bootstrap at
    ``{base}AGENTS.md``) and the pack branch (WP06, which renames the file). One
    definition, two consumers — the two must not be able to disagree.
    """
    return PUBLISHED_NAME if filename == SOURCE_NAME else filename
