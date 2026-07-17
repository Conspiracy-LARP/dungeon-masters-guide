"""The single configuration of the build: the base URL, the nav, and the roles.

NFR-001 / C-003: every absolute address in every published surface derives from one
configured base URL. Moving the guide to a custom domain must be a one-value edit
(SC-006), which is only true if nothing composes a URL by hand.

**Do not build a URL with an f-string anywhere else in this package.** Call
:meth:`BuildConfig.absolute_url`. There is a test that greps the package for hostname
literals, and it will fail you.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import yaml

#: The one place the deployed address is written down. Note the two properties that
#: are easy to lose: the **subpath** (this is a project site, not a domain root — C-3)
#: and the **trailing slash** (so `absolute_url` joins without inventing one).
DEFAULT_BASE_URL: Final[str] = "https://conspiracy-larp.github.io/dungeon-masters-guide/"

#: The declaration itself, relative to the repository root.
MKDOCS_FILENAME: Final[str] = "mkdocs.yml"


class ConfigError(RuntimeError):
    """The declaration is missing, unreadable, or internally inconsistent."""


def _repo_root() -> Path:
    """The repository root: the directory holding ``mkdocs.yml``."""
    return Path(__file__).resolve().parents[2]


def _base_version() -> str:
    """The human-controlled ``major.minor`` base from ``pyproject.toml``.

    ``pyproject`` holds the *base*, bumped by hand only when a release earns a new minor or
    major. The patch is not read from here; it is derived from git (see
    :func:`project_version`), so the number climbs on its own every merge without anyone
    editing a file, and without a CI job committing back to `main` and re-triggering itself.
    """
    import re as _re

    pyproject = _repo_root() / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    match = _re.search(r'^version\s*=\s*"([^"]+)"', text, _re.M)
    if match is None:
        raise ConfigError(
            f"no `version` found in {pyproject}. The site footer, llms.txt and the book all "
            "derive the version from it; there is nowhere else to read it from."
        )
    return match.group(1)


def _git_commit_count() -> int | None:
    """Commits reachable from HEAD, or ``None`` if git cannot answer (a source tarball).

    This is the auto-incrementing patch: it rises by one on every merge to `main`, which is
    "a new number per release" with no manual step.

    **CI trap:** a shallow clone (`actions/checkout` default depth 1) returns ``1`` — every
    build would claim ``x.y.1``. The publish workflow's build job sets ``fetch-depth: 0`` so
    the count is real; :func:`project_version` refuses a count of 1 as a backstop.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=_repo_root(),
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def project_version() -> str:
    """The version stamped into every compiled surface: ``major.minor.<commit-count>``.

    ``major.minor`` is the human base (:func:`_base_version`); the patch is the git commit
    count (:func:`_git_commit_count`), so it bumps automatically each merge. The single
    source every surface reads — footer, ``llms.txt`` and the book — so no two can disagree.

    Falls back to the pyproject patch when git is unavailable, **and refuses a commit count
    of 1**: in a real repo the count is in the hundreds, so a 1 means a shallow CI checkout,
    and stamping a number known to be wrong is worse than one that is merely static.
    """
    base = _base_version()
    parts = base.split(".")
    major = parts[0] if parts else "0"
    minor = parts[1] if len(parts) > 1 else "0"
    pyproject_patch = parts[2] if len(parts) > 2 else "0"

    count = _git_commit_count()
    if count is None or count <= 1:
        return f"{major}.{minor}.{pyproject_patch}"
    return f"{major}.{minor}.{count}"


def _mkdocs_loader() -> type[yaml.SafeLoader]:
    """A YAML loader tolerant of MkDocs' custom tags (``!!python/name:``, ``!ENV``).

    We only ever read `nav`, `site_url` and `extra` — we are not executing the config —
    so unknown tags resolve to ``None`` rather than exploding.
    """

    class _Loader(yaml.SafeLoader):
        pass

    def _ignore(loader: yaml.SafeLoader, suffix: str, node: yaml.Node) -> None:
        return None

    # PyYAML's constructor-registration API is untyped upstream.
    _Loader.add_multi_constructor("tag:yaml.org,2002:python/name:", _ignore)  # type: ignore[no-untyped-call]
    _Loader.add_multi_constructor("!", _ignore)  # type: ignore[no-untyped-call]
    return _Loader


@dataclass(frozen=True)
class BuildConfig:
    """The parsed declaration.

    This is the *only* reader of ``mkdocs.yml``. Everything downstream — roles, the
    book, `llms.txt`, the pack branch, provenance — consumes this object, so that the
    reading order and the base URL each exist exactly once.
    """

    base_url: str
    #: Chapter filenames in reading order. The order IS the reading order (contract
    #: rule 4); position N in this list is chapter N.
    nav: tuple[str, ...]
    #: Titles declared in nav, keyed by filename.
    nav_titles: dict[str, str]
    #: Published, but outside the book's flow — from ``extra.pack.not_in_book``.
    not_in_book: tuple[str, ...]
    #: MkDocs' own intentional-omission declaration. Must equal ``not_in_book``.
    not_in_nav: tuple[str, ...]
    #: Absolute path of the pack directory (``docs_dir``).
    pack_dir: Path

    def absolute_url(self, path: str) -> str:
        """Return the absolute published URL for ``path``.

        The single URL-composition helper (NFR-001). ``path`` is relative to the base
        and must not be root-relative: `/AGENTS.md` would drop the subpath and 404
        (url-map contract, C2).

        >>> cfg.absolute_url("AGENTS.md")
        'https://conspiracy-larp.github.io/dungeon-masters-guide/AGENTS.md'
        >>> cfg.absolute_url("")
        'https://conspiracy-larp.github.io/dungeon-masters-guide/'
        """
        if path.startswith(("http://", "https://")):
            raise ConfigError(
                f"absolute_url() takes a path relative to the base, not a full URL: {path!r}. "
                "Hard-coding a hostname breaks NFR-001."
            )
        if path.startswith("/"):
            raise ConfigError(
                f"absolute_url() takes a base-relative path, but got the root-relative {path!r}. "
                "The site lives on a subpath (C-003); a leading slash discards it and 404s."
            )
        return f"{self.base_url}{path}"


def _require_flat(names: list[str], where: str) -> None:
    """C-001: the pack is flat. A path separator in a declaration is a build failure."""
    for name in names:
        if "/" in name or "\\" in name:
            raise ConfigError(
                f"{where} names {name!r}, which contains a path separator. "
                "The pack is flat by design (C-001): a nested pack breaks the "
                "bare-sibling cross-link property that lets one set of bytes serve "
                "the site, the book, the pack branch and GitHub's own rendering."
            )


def _parse_nav(raw_nav: Any) -> tuple[tuple[str, ...], dict[str, str]]:
    """Flatten MkDocs' ``nav`` into ordered filenames plus their declared titles."""
    if not isinstance(raw_nav, list):
        raise ConfigError("mkdocs.yml declares no `nav:` list — the reading order is missing.")

    filenames: list[str] = []
    titles: dict[str, str] = {}
    for entry in raw_nav:
        if not isinstance(entry, dict) or len(entry) != 1:
            raise ConfigError(
                f"Unsupported nav entry {entry!r}. This guide's nav is a flat list of "
                "`Title: filename.md` pairs; nesting would imply a reading order that "
                "is not a sequence."
            )
        title, filename = next(iter(entry.items()))
        if not isinstance(filename, str):
            raise ConfigError(f"nav entry {title!r} does not name a file: {filename!r}")
        filenames.append(filename)
        titles[filename] = str(title)
    return tuple(filenames), titles


def _parse_not_in_nav(raw: Any) -> tuple[str, ...]:
    """MkDocs' ``not_in_nav`` is a newline-separated glob block."""
    if raw is None:
        return ()
    if isinstance(raw, str):
        return tuple(line.strip() for line in raw.splitlines() if line.strip())
    if isinstance(raw, list):
        return tuple(str(item).strip() for item in raw if str(item).strip())
    raise ConfigError(f"Unsupported not_in_nav declaration: {raw!r}")


def load_config(mkdocs_path: Path | None = None) -> BuildConfig:
    """Read and validate the declaration.

    Args:
        mkdocs_path: the config to read. Defaults to the repository's ``mkdocs.yml``.

    Raises:
        ConfigError: the declaration is missing or malformed.
    """
    path = mkdocs_path if mkdocs_path is not None else _repo_root() / MKDOCS_FILENAME
    if not path.is_file():
        raise ConfigError(
            f"No declaration at {path}. The build has no reading order to derive from."
        )

    raw = yaml.load(path.read_text(encoding="utf-8"), Loader=_mkdocs_loader())
    if not isinstance(raw, dict):
        raise ConfigError(f"{path} is not a YAML mapping.")

    nav, nav_titles = _parse_nav(raw.get("nav"))
    _require_flat(list(nav), "nav")

    extra = raw.get("extra") or {}
    pack_extra = (extra.get("pack") or {}) if isinstance(extra, dict) else {}
    not_in_book = tuple(str(name) for name in (pack_extra.get("not_in_book") or ()))
    _require_flat(list(not_in_book), "extra.pack.not_in_book")

    not_in_nav = _parse_not_in_nav(raw.get("not_in_nav"))

    base_url = str(raw.get("site_url") or DEFAULT_BASE_URL)
    if not base_url.endswith("/"):
        # Enforced rather than patched: a base without a trailing slash silently
        # produces `...guide AGENTS.md` style joins, which are wrong in a way that
        # only shows up in the published output.
        raise ConfigError(
            f"site_url must end with '/', got {base_url!r}. absolute_url() joins by "
            "concatenation so that the subpath (C-003) cannot be lost."
        )

    docs_dir = str(raw.get("docs_dir") or "src/pack")
    pack_dir = (path.parent / docs_dir).resolve()

    return BuildConfig(
        base_url=base_url,
        nav=nav,
        nav_titles=nav_titles,
        not_in_book=not_in_book,
        not_in_nav=not_in_nav,
        pack_dir=pack_dir,
    )
