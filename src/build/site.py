"""The site build: the landing page, the AI pointers, and the raw markdown surface.

An MkDocs hook (declared as ``hooks:`` in ``mkdocs.yml``), so that `mkdocs build`,
`mkdocs serve` and CI all get the same site and nobody has to remember a second command.

It does four things, all of them derivations from ``src/pack/`` and none of them writes
to it (C-002, C-006):

* **The landing page** (FR-001) is *extracted* from ``creator-kit.md``'s "What is this?"
  pitch at build time. There is no ``index.md`` in the pack, and there must not be: an
  authored landing page is hand-written published content, which NFR-003 forbids, and it
  would drift from the kit the first time the kit's pitch was reworded. If the extraction
  ever stops finding the pitch, the build **fails** rather than publishing a blank front
  door.
* **The AI pointer** (FR-002): every page is given the address of its own clean markdown
  source, which ``main.html`` renders both visibly and as
  ``<link rel="alternate" type="text/markdown">``.
* **The raw markdown surface** (FR-007, FR-008, FR-010): every pack document is copied
  into the output at its parallel path, byte-for-byte, with the bootstrap published as
  ``AGENTS.md``. This is the reason the mission exists — ``{base}AGENTS.md`` is the one
  URL a creator hands to a model — so the copy is verified here, in the build, and not
  only in the tests.
* **``.nojekyll``** (FR-012): without it GitHub Pages runs Jekyll over the output, which
  can quietly mangle or hide the markdown files the point above just published.

**Every address comes from :meth:`BuildConfig.absolute_url`** (NFR-001), and the base it
uses is read from the *live* MkDocs config rather than re-read from disk. That is what
makes the base a single edit (SC-006): override ``site_url`` and every generated address
in the site follows, which ``tests/test_site.py`` asserts by building the site twice.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Final

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File, Files, InclusionLevel
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page

from build.config import BuildConfig, ConfigError, load_config
from build.rename import rewrite_references
from build.roles import Document, RoleError, load_documents

#: The generated landing page's path in the docs tree. It is generated, never authored:
#: nothing of this name exists in src/pack/, and adding one would be the C-002 violation
#: this hook exists to avoid.
INDEX_FILENAME: Final[str] = "index.md"

#: The document the landing page is derived from, and the marker that opens the section
#: FR-001 names. The marker is bold running text rather than a heading — the kit answers
#: "what is this?" in its opening paragraph, before its first `##` — so the section is
#: read from the marker to the next thematic break or heading, whichever comes first.
PITCH_SOURCE: Final[str] = "creator-kit.md"
PITCH_MARKER: Final[str] = "**What is this?**"

#: Markdown thematic breaks, any of which ends the pitch.
_THEMATIC_BREAKS: Final[frozenset[str]] = frozenset({"---", "***", "___"})

#: The printable book (FR-004). WP04 produces it; the landing page links it, because
#: FR-004 requires it be linked prominently and the landing page is where a reader looks.
#: Named by the url-map contract, so it is composed from the base like every other
#: address rather than assumed to be a sibling of the index.
PDF_FILENAME: Final[str] = "dungeon-masters-guide.pdf"

#: FR-012. Empty file; its existence is the whole message.
NOJEKYLL_FILENAME: Final[str] = ".nojekyll"


class SiteError(RuntimeError):
    """The site cannot be derived from the pack as declared."""


@dataclasses.dataclass(frozen=True)
class SiteBuild:
    """Everything the hook's events need, resolved once per build.

    ``config`` here is *our* :class:`BuildConfig` — the parsed declaration with its base
    URL reconciled against the live MkDocs config — not MkDocs' own config object.
    """

    config: BuildConfig
    documents: tuple[Document, ...]
    landing_markdown: str

    def document_for(self, src_uri: str) -> Document | None:
        """The pack document a docs-tree path came from, if any."""
        return next((d for d in self.documents if d.filename == src_uri), None)


#: Resolved in `on_config`, consumed by the later events. MkDocs re-runs `on_config` on
#: every build, including each rebuild under `mkdocs serve`, so this cannot go stale.
_BUILD: SiteBuild | None = None


# --------------------------------------------------------------------------------------
# Deriving the landing page (T013)
# --------------------------------------------------------------------------------------


# The version resolver lives in build.config (the neutral shared module) so the site
# footer, llms.txt and the book all read one source and cannot disagree (SC-004).
from build.config import project_version as _project_version


def extract_pitch(markdown: str) -> str:
    """Return the "What is this?" section of the kit.

    Args:
        markdown: the source of ``creator-kit.md``.

    Returns:
        The pitch, verbatim — every byte of it the kit's own words (NFR-003).

    Raises:
        SiteError: the marker is absent or the section is empty. **Loudly, on purpose**:
            the alternative is a landing page that is silently blank, or one that has
            quietly become someone's paraphrase of a pitch that has since moved on.
    """
    lines = markdown.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.lstrip().startswith(PITCH_MARKER)),
        None,
    )
    if start is None:
        raise SiteError(
            f"{PITCH_SOURCE} no longer contains {PITCH_MARKER!r}, so the landing page "
            "has nothing to be derived from (FR-001). The site's front door is the "
            "kit's own pitch, extracted at build time — it is not authored anywhere, "
            "and it must not be. Either the kit's opening was reworded (in which case "
            "point PITCH_MARKER at the new wording) or the pitch has genuinely gone "
            "(in which case this is a content question, not a build one)."
        )

    collected: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped in _THEMATIC_BREAKS or stripped.startswith("## "):
            break
        collected.append(line)

    pitch = "\n".join(collected).strip()
    if not pitch.replace(PITCH_MARKER, "").strip():
        raise SiteError(
            f"The {PITCH_MARKER!r} section of {PITCH_SOURCE} is empty; the landing page "
            "would publish a blank front door (FR-001)."
        )
    return pitch


def _pitch_title(markdown: str) -> str:
    """The kit's own H1, which titles the landing page.

    Derived rather than invented for the same reason as the pitch itself: a title
    written here is one more place the site could contradict the guide.
    """
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise SiteError(
        f"{PITCH_SOURCE} has no H1 to title the landing page with (FR-001). Every pack "
        "document opens with one; if this one no longer does, that is a content change."
    )


def landing_markdown(config: BuildConfig, documents: tuple[Document, ...]) -> str:
    """Render the landing page's markdown: the kit's pitch, plus the ways in.

    The prose is entirely the kit's (NFR-003). What is added is navigation, and only the
    navigation the requirements name: the reading entry point, the PDF (FR-004, "linked
    prominently"), and the machine front door (FR-008). Every address is composed from
    the configured base (NFR-001).
    """
    source = (config.pack_dir / PITCH_SOURCE).read_text(encoding="utf-8")
    pitch = extract_pitch(source)
    title = _pitch_title(source)

    bootstrap = next((d for d in documents if d.filename != d.published_name), None)
    bootstrap_url = config.absolute_url(bootstrap.published_name) if bootstrap is not None else None
    pdf_url = config.absolute_url(PDF_FILENAME)

    ways_in = [
        f"- **[Read the guide]({PITCH_SOURCE})** — start with the creator kit; "
        "the whole gist in one sitting.",
        f"- **[Download the printable book]({pdf_url})** — the entire guide as a PDF.",
    ]
    if bootstrap_url is not None:
        ways_in.append(
            f"- **Reading this as an AI?** The bootstrap is at "
            f"[{bootstrap_url}]({bootstrap_url}) — self-contained, and the one address "
            "to hand a model."
        )

    return "\n".join([f"# {title}", "", pitch, "", "## Where to start", "", *ways_in, ""])


# --------------------------------------------------------------------------------------
# Publishing the raw markdown (T015) and .nojekyll (T016)
# --------------------------------------------------------------------------------------


def publish_raw_markdown(site_dir: Path, build: SiteBuild) -> dict[str, bytes]:
    """Write every pack document into the output at its parallel path.

    Byte-for-byte with the source (FR-007), with exactly one exception, which FR-010
    forces: the bootstrap is published as ``AGENTS.md``, so every published document's
    references to ``start.md`` are repointed at ``AGENTS.md`` — otherwise a model that
    fetched ``AGENTS.md`` and followed a link would 404 on a document that, under that
    name, does not exist. The rewrite is boundary-aware (``build.rename``); it does not
    touch ``getting-started.md``.

    Returns:
        The published bytes, keyed by published name — so a caller can verify the output
        without re-reading it.
    """
    published: dict[str, bytes] = {}
    for document in build.documents:
        source = build.config.pack_dir / document.filename
        try:
            original = source.read_bytes()
        except OSError as exc:
            raise SiteError(f"Cannot read {source} to publish it: {exc}") from exc

        # Bytes in, bytes out: decoding to text and back with an explicit encoding is
        # what keeps "byte-identical" true. `read_text` would silently normalise line
        # endings, which is a difference nobody would ever see until a diff of the pack
        # branch showed every line changed.
        rewritten = rewrite_references(original.decode("utf-8")).encode("utf-8")

        target = site_dir / document.published_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(rewritten)
        published[document.published_name] = rewritten

    return published


def _verify_published(site_dir: Path, build: SiteBuild) -> None:
    """Assert the machine surface is actually there, in the build, not only in a test.

    FR-008 is the mission's reason for existing and it fails silently — the site looks
    perfect either way. So the build itself checks it.
    """
    for document in build.documents:
        target = site_dir / document.published_name
        if not target.is_file():
            raise SiteError(
                f"{document.published_name} is missing from the built site, so "
                f"{build.config.absolute_url(document.published_name)} would 404 "
                "(FR-007)."
            )

    bootstrap = next((d for d in build.documents if d.filename != d.published_name), None)
    if bootstrap is None:
        return

    published = (site_dir / bootstrap.published_name).read_bytes()
    original = (build.config.pack_dir / bootstrap.filename).read_bytes()
    if published != rewrite_references(original.decode("utf-8")).encode("utf-8"):
        raise SiteError(
            f"{bootstrap.published_name} in the output is not {bootstrap.filename} from "
            "the pack. That address is the one a creator hands to a model (FR-008); it "
            "cannot be approximately right."
        )


def write_robots(site_dir: Path, config: BuildConfig) -> Path:
    """Point crawlers at the sitemap MkDocs generates.

    Generated, not authored: `docs_dir` is `src/pack/` — the product — so a hand-written
    `robots.txt` would have to live inside the guide (C-002/C-006). The sitemap URL derives
    from the one configured base (NFR-001), so a domain change carries it.
    """
    path = site_dir / "robots.txt"
    path.write_text(
        f"User-agent: *\nAllow: /\nSitemap: {config.absolute_url('sitemap.xml')}\n",
        encoding="utf-8",
    )
    return path


#: The browser-only stylesheet, authored under src/theme/ and shipped to the site root.
SITEMAP_STYLESHEET_SOURCE: Final[Path] = (
    Path(__file__).resolve().parent.parent / "theme" / "sitemap.xsl"
)
SITEMAP_STYLESHEET_NAME: Final[str] = "sitemap.xsl"


def style_sitemap(site_dir: Path, config: BuildConfig) -> None:
    """Make the MkDocs-generated sitemap render as a table when opened in a browser.

    Two steps, both cosmetic and both safe for crawlers:

    1. Copy ``sitemap.xsl`` to the site root.
    2. Insert one ``<?xml-stylesheet?>`` processing instruction after the XML
       declaration in ``sitemap.xml``. A crawler ignores the instruction and reads the
       ``<urlset>`` exactly as before; a browser follows it and renders the stylesheet.

    Degrades to a no-op rather than failing the build: if MkDocs produced no sitemap, or
    the stylesheet source is missing, there is nothing here worth breaking a publish over.
    The sitemap remains valid either way — the worst outcome is that it is not pretty.

    The ``.gz`` twin is rewritten to match, so the two never disagree (SC-004 in spirit).
    """
    sitemap = site_dir / "sitemap.xml"
    if not sitemap.is_file() or not SITEMAP_STYLESHEET_SOURCE.is_file():
        return

    (site_dir / SITEMAP_STYLESHEET_NAME).write_bytes(SITEMAP_STYLESHEET_SOURCE.read_bytes())

    href = config.absolute_url(SITEMAP_STYLESHEET_NAME)
    instruction = f'<?xml-stylesheet type="text/xsl" href="{href}"?>'
    text = sitemap.read_text(encoding="utf-8")
    if "xml-stylesheet" in text:
        return  # already styled; keep idempotent
    declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    if declaration in text:
        text = text.replace(declaration, f"{declaration}\n{instruction}", 1)
    else:
        text = f"{instruction}\n{text}"
    sitemap.write_text(text, encoding="utf-8")

    gz = site_dir / "sitemap.xml.gz"
    if gz.is_file():
        import gzip

        gz.write_bytes(gzip.compress(text.encode("utf-8")))


def write_nojekyll(site_dir: Path) -> Path:
    """Emit the empty ``.nojekyll`` marker (FR-012).

    Without it, Pages runs Jekyll over the output, which ignores files and directories
    beginning with an underscore and is free to process the rest — including the raw
    markdown this hook just published.
    """
    marker = site_dir / NOJEKYLL_FILENAME
    marker.write_bytes(b"")
    return marker


# --------------------------------------------------------------------------------------
# Wiring: MkDocs' hook events
# --------------------------------------------------------------------------------------


def _resolve(mkdocs_config: MkDocsConfig) -> SiteBuild:
    """Reconcile the declaration on disk with the live MkDocs config."""
    declaration = Path(mkdocs_config.config_file_path)
    try:
        config = load_config(declaration)
    except ConfigError as exc:
        raise PluginError(str(exc)) from exc

    site_url = mkdocs_config.site_url
    if not site_url:
        raise PluginError(
            "mkdocs.yml declares no site_url, so there is no base to derive addresses "
            "from (NFR-001). Every generated address — the AI pointer, the markdown "
            "alternate, the PDF link — needs one."
        )
    if not site_url.endswith("/"):
        raise PluginError(
            f"site_url must end with '/', got {site_url!r}. Addresses are composed by "
            "joining onto the base, so a missing slash silently welds the subpath to "
            "the filename (C-003)."
        )

    # The LIVE config wins over what was parsed from the file. This is the line that
    # makes SC-006 true: overriding site_url (a custom domain, or the base-swap test)
    # moves every address this hook generates, because none of them is composed from
    # anything else. Same for docs_dir — the pack is wherever this build says it is.
    config = dataclasses.replace(
        config,
        base_url=site_url,
        pack_dir=Path(mkdocs_config.docs_dir),
    )

    try:
        documents = tuple(load_documents(config.pack_dir, config))
    except RoleError as exc:
        raise PluginError(str(exc)) from exc

    try:
        landing = landing_markdown(config, documents)
    except (SiteError, OSError) as exc:
        raise PluginError(str(exc)) from exc

    return SiteBuild(config=config, documents=documents, landing_markdown=landing)


def _require_build() -> SiteBuild:
    if _BUILD is None:  # pragma: no cover — MkDocs always runs on_config first.
        raise PluginError("The site hook was not configured; on_config did not run.")
    return _BUILD


def on_config(config: MkDocsConfig) -> MkDocsConfig:
    """Resolve the declaration, the documents and the landing page — or fail the build.

    Also injects the version from ``pyproject.toml`` into ``config.extra`` so every surface
    states the same number from one source.
    """
    global _BUILD
    _BUILD = _resolve(config)
    config.extra["version_string"] = _project_version()
    return config


def _vacate_the_root(files: Files, build: SiteBuild) -> None:
    """Move any pack document that MkDocs would render at the site root out of the way.

    **`README.md` is why this exists, and it fails silently without it.** MkDocs maps
    both `index.md` and `README.md` to `index.html` — `File._get_stem` returns `index`
    for a file named README — so the pack's README lands on exactly the address the
    derived landing page occupies. MkDocs' own conflict handling does not catch it: that
    only compares the files it found by walking `docs_dir`, and the landing page is
    generated in this event, afterwards. Both pages render, one overwrites the other,
    and the build exits 0 — under `--strict`, with no warning.

    Neither outcome is acceptable. `README.md` is the pack branch's front door and is
    `not_in_book`; the contract is explicit that it is **not** the site index and that it
    publishes "as an ordinary page and as raw markdown like any other non-chapter
    document" (roles-declaration § The landing page). So it is republished at its own
    address, which is also the address provenance expects of it (`README/index.html`).
    """
    for document in build.documents:
        file = files.get_file_from_path(document.filename)
        if file is None or file.dest_uri != "index.html":
            continue
        stem = Path(document.filename).stem
        # `name`, `dest_uri` and `url` are cached properties; assigning to them is how
        # MkDocs itself expects a file to be redirected.
        file.name = stem
        file.dest_uri = f"{stem}/index.html"
        file.url = f"{stem}/"


def on_files(files: Files, *, config: MkDocsConfig) -> Files:
    """Add the derived landing page to the docs tree (FR-001).

    ``InclusionLevel.NOT_IN_NAV`` because the landing page is the site's front door, not
    a chapter: the reading order is `nav`'s and only `nav`'s. Without it, MkDocs would
    report the generated index as a page missing from the nav and — with
    ``validation.nav.omitted_files: warn``, which is what gives FR-011 its teeth —
    ``--strict`` would fail on the hook's own output.
    """
    build = _require_build()
    _vacate_the_root(files, build)
    files.append(
        File.generated(
            config,
            INDEX_FILENAME,
            content=build.landing_markdown,
            inclusion=InclusionLevel.NOT_IN_NAV,
        )
    )
    return files


def on_page_context(
    context: dict[str, Any],
    *,
    page: Page,
    config: MkDocsConfig,
    nav: Navigation,
) -> dict[str, Any]:
    """Give every page the address of its own clean markdown source (FR-002).

    ``main.html`` renders it twice: visibly, for a human who wants the source, and as
    ``<link rel="alternate" type="text/markdown">`` for a model that never renders the
    page at all.

    The bootstrap's page points at ``AGENTS.md`` and not ``start.md`` because the name
    comes from ``Document.published_name`` (WP02) — the rename is not special-cased here,
    so the site and the pack branch cannot disagree about it.
    """
    build = _require_build()
    document = build.document_for(page.file.src_uri)
    if document is not None:
        context["raw_markdown_url"] = build.config.absolute_url(document.published_name)
    elif page.file.src_uri == INDEX_FILENAME:
        # The landing page is an extract of the kit, so the kit is its source. Pointing
        # it at a nonexistent `index.md` would be a broken promise; pointing it at the
        # bootstrap would be a lie about what this page is.
        kit = build.document_for(PITCH_SOURCE)
        if kit is not None:
            context["raw_markdown_url"] = build.config.absolute_url(kit.published_name)
    return context


def on_post_build(*, config: MkDocsConfig) -> None:
    """Publish the raw markdown and `.nojekyll`, then check they are really there."""
    build = _require_build()
    site_dir = Path(config.site_dir)
    try:
        publish_raw_markdown(site_dir, build)
        _verify_published(site_dir, build)
    except SiteError as exc:
        raise PluginError(str(exc)) from exc
    write_nojekyll(site_dir)
    write_robots(site_dir, build.config)
    style_sitemap(site_dir, build.config)
