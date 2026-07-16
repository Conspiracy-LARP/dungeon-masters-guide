"""Tests for role resolution, the lint (FR-011), and the prose drift check (T011)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner

from build.cli import guide
from build.config import BuildConfig, ConfigError, load_config
from build.roles import (
    Role,
    RoleError,
    check_declaration,
    check_drift,
    chapters,
    drift_is_fatal,
    load_documents,
)

# --------------------------------------------------------------------------------------
# Role resolution
# --------------------------------------------------------------------------------------


def test_every_document_resolves_to_exactly_one_role(pack_config: BuildConfig) -> None:
    documents = load_documents(pack_config.pack_dir, pack_config)
    assert {d.filename for d in documents} == {
        "creator-kit.md",
        "getting-started.md",
        "ethics.md",
        "README.md",
        "start.md",
    }
    assert [d.role for d in documents].count(Role.CHAPTER) == 3
    assert [d.role for d in documents].count(Role.NOT_IN_BOOK) == 2


def test_chapters_carry_nav_order_and_contiguous_positions(pack_config: BuildConfig) -> None:
    documents = load_documents(pack_config.pack_dir, pack_config)
    book = chapters(documents)
    assert [d.filename for d in book] == ["creator-kit.md", "getting-started.md", "ethics.md"]
    assert [d.position for d in book] == [1, 2, 3]


def test_not_in_book_documents_have_no_position(pack_config: BuildConfig) -> None:
    documents = load_documents(pack_config.pack_dir, pack_config)
    for document in documents:
        if document.role is Role.NOT_IN_BOOK:
            assert document.position is None


def test_titles_come_from_nav(pack_config: BuildConfig) -> None:
    documents = load_documents(pack_config.pack_dir, pack_config)
    titles = {d.filename: d.title for d in documents}
    assert titles["creator-kit.md"] == "Creator Kit"


def test_not_in_book_titles_fall_back_to_the_first_h1(pack_config: BuildConfig) -> None:
    documents = load_documents(pack_config.pack_dir, pack_config)
    titles = {d.filename: d.title for d in documents}
    assert titles["start.md"] == "Start here"


def test_published_name_is_resolved_on_documents(pack_config: BuildConfig) -> None:
    documents = load_documents(pack_config.pack_dir, pack_config)
    published = {d.filename: d.published_name for d in documents}
    assert published["start.md"] == "AGENTS.md"
    assert published["getting-started.md"] == "getting-started.md"
    assert published["README.md"] == "README.md"


# --------------------------------------------------------------------------------------
# The lint — the three failure modes (FR-011, contract rules 1-3)
# --------------------------------------------------------------------------------------


def test_undeclared_document_fails(pack_factory: Callable[..., BuildConfig]) -> None:
    """Rule 1. The silent failure this whole declaration exists to make loud."""
    config = pack_factory(
        files={
            **{k: v for k, v in _default_files().items()},
            "brand-new-chapter.md": "# Brand new\n",
        }
    )
    with pytest.raises(RoleError, match=r"brand-new-chapter\.md"):
        check_declaration(config.pack_dir, config)


def test_undeclared_document_error_is_actionable(pack_factory: Callable[..., BuildConfig]) -> None:
    config = pack_factory(files={**_default_files(), "orphan.md": "# Orphan\n"})
    with pytest.raises(RoleError) as excinfo:
        check_declaration(config.pack_dir, config)
    message = str(excinfo.value)
    assert "orphan.md" in message
    assert "not_in_book" in message and "nav" in message


def test_document_declared_in_both_lists_fails(pack_factory: Callable[..., BuildConfig]) -> None:
    """Rule 2."""
    config = pack_factory(
        nav=[("Creator Kit", "creator-kit.md"), ("Start", "start.md")],
        not_in_book=["README.md", "start.md"],
        files={
            "creator-kit.md": "# Creator Kit\n",
            "README.md": "# Readme\n",
            "start.md": "# Start\n",
        },
    )
    with pytest.raises(RoleError, match=r"start\.md.*BOTH|BOTH.*start\.md"):
        check_declaration(config.pack_dir, config)


def test_declaration_naming_a_missing_file_fails(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """Rule 3."""
    config = pack_factory(
        nav=[*_default_nav(), ("Ghost", "ghost.md")],
    )
    with pytest.raises(RoleError, match=r"ghost\.md"):
        check_declaration(config.pack_dir, config)


def test_not_in_nav_disagreeing_with_not_in_book_fails(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """The two lists must agree; two lists that can disagree, will."""
    config = pack_factory(not_in_nav=["README.md"])  # start.md omitted
    with pytest.raises(RoleError, match=r"not_in_nav"):
        check_declaration(config.pack_dir, config)


def test_matching_not_in_nav_passes(pack_config: BuildConfig) -> None:
    assert pack_config.not_in_nav == ("README.md", "start.md")
    check_declaration(pack_config.pack_dir, pack_config)


def test_non_flat_pack_fails(pack_factory: Callable[..., BuildConfig]) -> None:
    """C-001: a nested pack is a build failure."""
    config = pack_factory()
    nested = config.pack_dir / "sub"
    nested.mkdir()
    (nested / "buried.md").write_text("# Buried\n", encoding="utf-8")
    with pytest.raises(RoleError, match=r"not flat"):
        check_declaration(config.pack_dir, config)


def test_a_declaration_with_a_path_separator_fails(tmp_path: Path) -> None:
    """C-001, caught at parse time."""
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: T\n"
        "site_url: https://example.test/g/\n"
        "docs_dir: src/pack\n"
        "nav:\n"
        "  - Ethics: core/ethics.md\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match=r"path separator"):
        load_config(tmp_path / "mkdocs.yml")


# --------------------------------------------------------------------------------------
# Prose drift — reports, never fixes (T011)
# --------------------------------------------------------------------------------------


def test_no_drift_when_prose_matches(pack_config: BuildConfig) -> None:
    assert check_drift(pack_config.pack_dir, pack_config) == []


def test_drift_reports_a_document_missing_from_the_prose(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    files = _default_files()
    files["README.md"] = (
        "# The kit\n\n## The documents\n\n"
        "- **[`creator-kit.md`](creator-kit.md)** — the starter guide.\n"
        "- **[`start.md`](start.md)** — the brief.\n"
    )  # getting-started.md and ethics.md dropped
    config = pack_factory(files=files)
    findings = check_drift(config.pack_dir, config)
    missing = {f.filename for f in findings if f.kind == "missing"}
    assert missing == {"getting-started.md", "ethics.md"}
    assert all(f.prose_file == "README.md" for f in findings)


def test_drift_reports_a_document_the_prose_invents(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    files = _default_files()
    files["README.md"] = files["README.md"].replace(
        "- **[`start.md`](start.md)** — the brief for an LLM.\n",
        "- **[`start.md`](start.md)** — the brief for an LLM.\n"
        "- **[`imaginary.md`](imaginary.md)** — does not exist.\n",
    )
    config = pack_factory(files=files)
    findings = check_drift(config.pack_dir, config)
    extra = {f.filename for f in findings if f.kind == "extra"}
    assert "imaginary.md" in extra


def test_drift_check_writes_nothing_to_the_pack(pack_config: BuildConfig) -> None:
    """C-002/C-006. The check reports; a human fixes the prose."""
    before = {path.name: path.read_bytes() for path in sorted(pack_config.pack_dir.glob("*.md"))}
    check_drift(pack_config.pack_dir, pack_config)
    after = {path.name: path.read_bytes() for path in sorted(pack_config.pack_dir.glob("*.md"))}
    assert before == after


def test_drift_warns_on_a_feature_branch_and_fails_on_main() -> None:
    """The decision, already made: warn on feature branches, fail on main."""
    assert drift_is_fatal("main") is True
    assert drift_is_fatal("feat/guide-site-build") is False
    assert drift_is_fatal("kitty/mission-guide-site-build-01KXP76R-lane-b") is False
    assert drift_is_fatal("") is False


def test_drift_cli_exits_non_zero_on_main_when_there_is_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The half of the rule the repo's own clean state cannot demonstrate.

    The real pack has no drift, so the fatal path is unreachable against it. Inject a
    finding to prove `main` actually fails rather than merely printing in red.
    """
    from build import cli as cli_module
    from build.roles import DriftFinding

    monkeypatch.setattr(
        cli_module,
        "check_drift",
        lambda pack_dir, config: [
            DriftFinding(prose_file="README.md", filename="ethics.md", kind="missing")
        ],
    )
    result = CliRunner().invoke(guide, ["roles", "check-drift", "--branch", "main"])
    assert result.exit_code == 1, result.output
    assert "ethics.md" in result.output


def test_drift_cli_exits_zero_on_a_feature_branch_despite_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Same drift, feature branch: reported, but does not punish the writer mid-edit."""
    from build import cli as cli_module
    from build.roles import DriftFinding

    monkeypatch.setattr(
        cli_module,
        "check_drift",
        lambda pack_dir, config: [
            DriftFinding(prose_file="README.md", filename="ethics.md", kind="missing")
        ],
    )
    result = CliRunner().invoke(guide, ["roles", "check-drift", "--branch", "feat/x"])
    assert result.exit_code == 0, result.output
    assert "ethics.md" in result.output
    assert "WILL fail on main" in result.output


# --------------------------------------------------------------------------------------
# The CLI
# --------------------------------------------------------------------------------------


def test_roles_lint_passes_against_the_real_pack() -> None:
    """The happy path, against the repository as it stands today."""
    result = CliRunner().invoke(guide, ["roles", "lint"])
    assert result.exit_code == 0, result.output
    assert "OK" in result.output


def test_real_pack_declares_ten_chapters(real_repo_config: BuildConfig) -> None:
    """The reading order is specified, not invented — doc/build.md."""
    documents = load_documents(real_repo_config.pack_dir, real_repo_config)
    book = chapters(documents)
    assert [d.filename for d in book] == [
        "creator-kit.md",
        "getting-started.md",
        "storytelling.md",
        "philosophy.md",
        "improvisation.md",
        "ethics.md",
        "communications.md",
        "worked-example.md",
        "technical-suggestions.md",
        "story-continuity-checker-prompt.md",
    ]
    assert {d.filename for d in documents if d.role is Role.NOT_IN_BOOK} == {
        "README.md",
        "start.md",
    }


def test_real_pack_has_no_prose_drift(real_repo_config: BuildConfig) -> None:
    """The prose lists agree with the declaration today; keep it that way."""
    findings = check_drift(real_repo_config.pack_dir, real_repo_config)
    assert findings == [], "\n".join(f.describe() for f in findings)


def test_check_drift_cli_reports_and_exits_zero_on_a_feature_branch() -> None:
    result = CliRunner().invoke(guide, ["roles", "check-drift", "--branch", "feat/x"])
    assert result.exit_code == 0, result.output


def test_check_drift_cli_on_main_exits_zero_when_there_is_no_drift() -> None:
    """Strictness only bites when there is actually drift."""
    result = CliRunner().invoke(guide, ["roles", "check-drift", "--branch", "main"])
    assert result.exit_code == 0, result.output


def test_roles_list_shows_the_reading_order_and_the_rename() -> None:
    result = CliRunner().invoke(guide, ["roles", "list"])
    assert result.exit_code == 0, result.output
    assert "published as AGENTS.md" in result.output


# --------------------------------------------------------------------------------------
# One list of chapters, one hostname
# --------------------------------------------------------------------------------------


def test_the_reading_order_is_declared_exactly_once(repo_root: Path) -> None:
    """No module may hard-code a chapter list.

    The reading order lives in mkdocs.yml's nav and nowhere else. If this fails, a
    second copy has crept into the build — the exact drift this design exists to end.
    """
    distinctive = "story-continuity-checker-prompt.md"
    offenders: list[str] = []
    for path in sorted((repo_root / "src" / "build").rglob("*.py")):
        if distinctive in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(repo_root)))
    assert offenders == [], (
        f"Chapter filenames appear in {offenders}. The reading order is declared once, "
        "in mkdocs.yml's nav; everything else derives it."
    )


def test_no_module_hard_codes_a_hostname(repo_root: Path) -> None:
    """NFR-001/SC-006: changing the domain must be a one-value edit.

    Only config.py may name the host, and only as the documented default.
    """
    hostname = re.compile(r"https?://(?!example\.(test|com))[\w.-]+")
    offenders: list[str] = []
    for path in sorted((repo_root / "src" / "build").rglob("*.py")):
        if path.name == "config.py":
            continue
        if hostname.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(repo_root)))
    assert offenders == [], (
        f"{offenders} hard-code a hostname. Every URL goes through "
        "config.BuildConfig.absolute_url()."
    )


def test_absolute_url_builds_subpath_correct_urls(real_repo_config: BuildConfig) -> None:
    assert (
        real_repo_config.absolute_url("AGENTS.md")
        == "https://conspiracy-larp.github.io/dungeon-masters-guide/AGENTS.md"
    )
    assert (
        real_repo_config.absolute_url("")
        == "https://conspiracy-larp.github.io/dungeon-masters-guide/"
    )


def test_absolute_url_rejects_a_root_relative_path(real_repo_config: BuildConfig) -> None:
    """`/AGENTS.md` would drop the subpath and 404 (C-003, url-map C2)."""
    with pytest.raises(ConfigError, match=r"subpath"):
        real_repo_config.absolute_url("/AGENTS.md")


def test_absolute_url_rejects_a_full_url(real_repo_config: BuildConfig) -> None:
    with pytest.raises(ConfigError, match=r"NFR-001|full URL"):
        real_repo_config.absolute_url("https://elsewhere.test/x")


def test_a_base_url_without_a_trailing_slash_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: T\n"
        "site_url: https://example.test/guide\n"
        "docs_dir: src/pack\n"
        "nav:\n"
        "  - Ethics: ethics.md\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match=r"trailing slash|end with"):
        load_config(tmp_path / "mkdocs.yml")


def _default_files() -> dict[str, str]:
    from tests.conftest import DEFAULT_CHAPTERS, DEFAULT_NOT_IN_BOOK

    return dict(DEFAULT_CHAPTERS | DEFAULT_NOT_IN_BOOK)


def _default_nav() -> list[tuple[str, str]]:
    from tests.conftest import DEFAULT_NAV

    return list(DEFAULT_NAV)
