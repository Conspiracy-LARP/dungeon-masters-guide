"""Test fixtures: a temporary pack, so tests never depend on the live src/pack/.

The real pack's contents change independently of this mission — someone edits the guide
and unrelated tests go red. Tests here build their own miniature pack and their own
declaration, and assert behaviour against that.

The one deliberate exception is `real_repo_config`, used by the handful of tests that
must hold against the actual repository today (the role lint must pass on the real
pack, and no module may hard-code a hostname).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest
import yaml

from build.config import BuildConfig, load_config

#: A miniature stand-in for the real pack: three chapters and the two non-chapters.
#:
#: `creator-kit.md` carries a quick-read box — a blockquote bullet list — because that
#: box is one of the two prose lists the drift check keeps honest. It mirrors the real
#: file's shape: the box lists the OTHER chapters, never the kit itself.
DEFAULT_CHAPTERS: dict[str, str] = {
    "creator-kit.md": (
        "# Creator Kit\n\n"
        "The starter guide. See [ethics.md](ethics.md).\n\n"
        "*This is the **quick read**:*\n\n"
        "> - **[`getting-started.md`](getting-started.md)** — the on-ramp.\n"
        "> - **[`ethics.md`](ethics.md)** — the moral floor.\n"
    ),
    "getting-started.md": "# Getting Started\n\nThe on-ramp. See [start.md](start.md).\n",
    "ethics.md": "# Ethics\n\nThe moral floor.\n",
}

DEFAULT_NOT_IN_BOOK: dict[str, str] = {
    "README.md": "# The kit\n\n## The documents\n\n"
    "- **[`creator-kit.md`](creator-kit.md)** — the starter guide.\n"
    "- **[`getting-started.md`](getting-started.md)** — the on-ramp.\n"
    "- **[`ethics.md`](ethics.md)** — the moral floor.\n"
    "- **[`start.md`](start.md)** — the brief for an LLM.\n",
    "start.md": "# Start here\n\nThe bootstrap. Then read `getting-started.md`.\n",
}

#: Titles as they appear in nav, in reading order.
DEFAULT_NAV: list[tuple[str, str]] = [
    ("Creator Kit", "creator-kit.md"),
    ("Getting Started", "getting-started.md"),
    ("Ethics", "ethics.md"),
]


def _write_mkdocs(
    root: Path,
    nav: list[tuple[str, str]],
    not_in_book: list[str],
    not_in_nav: list[str] | None = None,
    site_url: str = "https://example.test/guide/",
) -> Path:
    """Write a declaration mirroring the real one's shape."""
    config: dict[str, object] = {
        "site_name": "Test Guide",
        "site_url": site_url,
        "docs_dir": "src/pack",
        "nav": [{title: filename} for title, filename in nav],
        "extra": {"pack": {"not_in_book": not_in_book}},
    }
    listed = not_in_book if not_in_nav is None else not_in_nav
    if listed:
        config["not_in_nav"] = "\n".join(listed) + "\n"

    path = root / "mkdocs.yml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


@pytest.fixture
def pack_factory(tmp_path: Path) -> Callable[..., BuildConfig]:
    """Build a temporary pack plus its declaration, and return the parsed config.

    Keyword arguments let a test perturb exactly one thing — an undeclared file, a
    double declaration, a missing file — and leave the rest valid.
    """

    def make(
        files: dict[str, str] | None = None,
        nav: list[tuple[str, str]] | None = None,
        not_in_book: list[str] | None = None,
        not_in_nav: list[str] | None = None,
        site_url: str = "https://example.test/guide/",
    ) -> BuildConfig:
        pack_dir = tmp_path / "src" / "pack"
        pack_dir.mkdir(parents=True, exist_ok=True)

        contents = dict(DEFAULT_CHAPTERS | DEFAULT_NOT_IN_BOOK) if files is None else files
        for filename, text in contents.items():
            target = pack_dir / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")

        mkdocs_path = _write_mkdocs(
            tmp_path,
            nav=DEFAULT_NAV if nav is None else nav,
            not_in_book=list(DEFAULT_NOT_IN_BOOK) if not_in_book is None else not_in_book,
            not_in_nav=not_in_nav,
            site_url=site_url,
        )
        return load_config(mkdocs_path)

    return make


@pytest.fixture
def pack_config(pack_factory: Callable[..., BuildConfig]) -> BuildConfig:
    """A valid temporary pack: three chapters, two non-chapters, all declared."""
    return pack_factory()


@pytest.fixture
def repo_root() -> Path:
    """The repository root."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def real_repo_config() -> BuildConfig:
    """The repository's actual declaration.

    Only for the few tests that must hold against the real repo today.
    """
    return load_config()
