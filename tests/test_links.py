"""The link checker: extraction, the three rules, and the bug that actually happened.

The centrepiece is `test_the_2026_07_16_readme_regression`. Everything else here guards
the checker; that one guards the guide, and it is the reason this module exists.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner

from build.cli import guide
from build.config import BuildConfig
from build.links import (
    Branch,
    Rule,
    Surface,
    check_links,
    check_path_separators,
    check_resolution,
    extract_links,
    main_surface,
    pack_surface,
    strip_code,
)

# --------------------------------------------------------------------------------------
# T032 — extraction, and the false positives that would sink the whole check.
# --------------------------------------------------------------------------------------


def test_a_prose_link_is_extracted() -> None:
    links = extract_links("Read [the floor](ethics.md) before you start.")
    assert [link.target for link in links] == ["ethics.md"]
    assert links[0].line == 1


def test_an_inline_code_sample_is_not_a_link() -> None:
    """THE false positive. The guide documents this convention using inline code."""
    assert extract_links("Write `[ethics.md](ethics.md)`, never a path.") == []


def test_a_double_backtick_code_sample_is_not_a_link() -> None:
    """A span whose body legitimately contains single backticks."""
    assert extract_links("Write `` `[ethics.md](ethics.md)` `` in your prose.") == []


def test_a_fenced_block_is_not_a_link() -> None:
    text = "Prose.\n\n```markdown\n[ethics.md](ethics.md)\n```\n\nMore prose.\n"
    assert extract_links(text) == []


def test_a_tilde_fenced_block_is_not_a_link() -> None:
    text = "Prose.\n\n~~~\n[ethics.md](ethics.md)\n~~~\n"
    assert extract_links(text) == []


def test_a_real_link_after_a_fenced_block_is_still_found() -> None:
    """The fence must close. A checker that stops checking is worse than no checker."""
    text = "```\ncode\n```\n\nRead [the floor](ethics.md).\n"
    assert [link.target for link in extract_links(text)] == ["ethics.md"]


def test_a_stray_backtick_does_not_blank_the_rest_of_the_document() -> None:
    """Code spans do not cross a blank line, so an unpaired tick fails closed."""
    text = "An unpaired ` tick here.\n\nRead [the floor](ethics.md).\n"
    assert [link.target for link in extract_links(text)] == ["ethics.md"]


def test_external_links_are_not_our_business() -> None:
    text = (
        "See [site](https://example.test/x), [plain](http://example.test), "
        "[mail](mailto:a@example.test) and [rel](//example.test/x)."
    )
    assert extract_links(text) == []


def test_a_pure_anchor_is_not_a_cross_reference() -> None:
    assert extract_links("Jump to [the floor](#the-floor).") == []


def test_an_anchored_sibling_resolves_on_the_document_part() -> None:
    links = extract_links("Read [the floor](ethics.md#the-floor).")
    assert links[0].target == "ethics.md#the-floor"
    assert links[0].path == "ethics.md"


def test_a_link_title_is_not_part_of_the_target() -> None:
    links = extract_links('Read [the floor](ethics.md "The moral floor").')
    assert [link.target for link in links] == ["ethics.md"]


def test_an_angle_bracketed_target_is_unwrapped() -> None:
    links = extract_links("Read [the floor](<ethics.md>).")
    assert [link.target for link in links] == ["ethics.md"]


def test_positions_survive_code_blanking() -> None:
    """Blanking rather than deleting: reported lines match the file a human opens."""
    text = "```\ncode\nmore\n```\n\nRead [the floor](ethics.md).\n"
    link = extract_links(text)[0]
    assert link.line == 6
    assert text.split("\n")[link.line - 1].startswith("Read ")


def test_strip_code_preserves_line_count() -> None:
    text = "a\n```\nb\n```\n`c`\n"
    assert strip_code(text).count("\n") == text.count("\n")


# --------------------------------------------------------------------------------------
# T032 — against the guide's own real documents. These are the files that would break.
# --------------------------------------------------------------------------------------

#: Real files that document the link convention *using* inline-code link samples. A naive
#: extractor flags the guide's own explanatory prose as a violation of the rule it is
#: explaining. Paths are relative to the repo root; missing files are skipped, because
#: this WP does not own them and a rename elsewhere must not fail this suite.
FILES_THAT_ILLUSTRATE_LINKS: list[str] = [
    "kitty-specs/guide-site-build-01KXP76R/quickstart.md",
    "CLAUDE.md",
    "doc/build.md",
]


@pytest.mark.parametrize("relative", FILES_THAT_ILLUSTRATE_LINKS)
def test_the_guides_own_inline_code_samples_are_not_extracted(
    repo_root: Path, relative: str
) -> None:
    """`[ethics.md](ethics.md)` inside backticks is a picture of a link, not a link."""
    path = repo_root / relative
    if not path.is_file():
        pytest.skip(f"{relative} is not present in this worktree.")

    text = path.read_text(encoding="utf-8")
    assert "`[ethics.md](ethics.md)`" in text, (
        f"{relative} no longer contains the inline-code link sample this test exists to "
        "guard. If the sample moved, point this test at where it went — do not delete it."
    )
    assert [link.target for link in extract_links(text) if link.path == "ethics.md"] == []


# --------------------------------------------------------------------------------------
# T033 — rule 1: no path separators (C-001).
# --------------------------------------------------------------------------------------


def test_a_bare_sibling_name_passes(pack_config: BuildConfig) -> None:
    assert check_path_separators(main_surface(pack_config)) == []


def test_a_pathed_link_fails_rule_one(pack_factory: Callable[..., BuildConfig]) -> None:
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n\nSee [the floor](src/pack/ethics.md).\n",
            "getting-started.md": "# Getting Started\n\nThe on-ramp.\n",
            "ethics.md": "# Ethics\n\nThe moral floor.\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    findings = check_path_separators(main_surface(config))

    assert len(findings) == 1
    assert findings[0].rule is Rule.PATH_SEPARATOR
    assert findings[0].target == "src/pack/ethics.md"
    assert findings[0].source == "src/pack/creator-kit.md"
    assert findings[0].line == 3


def test_the_path_separator_message_explains_why_the_rule_exists(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """An unexplained rule reads as pedantry, and pedantry gets switched off."""
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n\nSee [the floor](src/pack/ethics.md).\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    message = check_path_separators(main_surface(config))[0].describe()

    assert "src/pack/creator-kit.md:3" in message
    assert "`ethics.md`" in message, "the message must show the fix, not only the fault"
    assert "four different roots" in message
    assert "404" in message


def test_a_relative_parent_path_fails_rule_one(pack_factory: Callable[..., BuildConfig]) -> None:
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n\nSee [the floor](../pack/ethics.md).\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    findings = check_path_separators(main_surface(config))
    assert [f.target for f in findings] == ["../pack/ethics.md"]


def test_a_pathed_link_is_reported_once_not_three_times(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """It also fails to resolve on both branches. Saying so three times helps nobody."""
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n\nSee [the floor](src/pack/ethics.md).\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    findings = check_links(config)
    assert len(findings) == 1
    assert findings[0].rule is Rule.PATH_SEPARATOR


# --------------------------------------------------------------------------------------
# T034/T035 — the two branches, and the bug that has actually happened.
# --------------------------------------------------------------------------------------


def test_the_two_branches_name_the_bootstrap_differently(pack_config: BuildConfig) -> None:
    """The asymmetry is the design (C-004, FR-010), not a thing to tidy away."""
    assert "start.md" in main_surface(pack_config).names
    assert "AGENTS.md" not in main_surface(pack_config).names
    assert "AGENTS.md" in pack_surface(pack_config).names
    assert "start.md" not in pack_surface(pack_config).names
    assert Branch.MAIN.bootstrap == "start.md"
    assert Branch.PACK.bootstrap == "AGENTS.md"


def test_the_2026_07_16_readme_regression(pack_factory: Callable[..., BuildConfig]) -> None:
    """THE regression. `src/pack/README.md` linking to `AGENTS.md`.

    Written on 2026-07-16. Correct on the pack branch, a 404 on `main`, where the file
    is `start.md`. Caught only by an ad-hoc check that happened to be run. This is why
    rule 3 is not redundant with rule 2, and why this WP exists.
    """
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n\nThe starter guide.\n",
            "getting-started.md": "# Getting Started\n\nThe on-ramp.\n",
            "ethics.md": "# Ethics\n\nThe moral floor.\n",
            # The bug, verbatim: the branch's name for the bootstrap, written on main.
            "README.md": "# The kit\n\nStart with [the brief](AGENTS.md).\n",
            "start.md": "# Start here\n\nThe bootstrap.\n",
        }
    )
    findings = check_links(config)

    assert len(findings) == 1, "the link is wrong on exactly one branch — that is the bug"
    finding = findings[0]
    assert finding.rule is Rule.UNRESOLVED
    assert finding.branch is Branch.MAIN, "it 404s on main, where the bootstrap is start.md"
    assert finding.resolves_on is Branch.PACK, "and resolves on the branch, which is why it slipped"
    assert finding.source == "src/pack/README.md"
    assert finding.target == "AGENTS.md"

    message = finding.describe()
    assert "does not resolve on `main`" in message
    assert "DOES resolve on `pack`" in message
    assert "start.md" in message and "AGENTS.md" in message


def test_the_regression_link_is_correct_on_the_pack_branch(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """The other half of why it slipped through: the branch was genuinely fine."""
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n\nStart with [the brief](AGENTS.md).\n",
            "start.md": "# Start here\n",
        }
    )
    pack = pack_surface(config)
    main = main_surface(config)

    assert check_resolution(pack, other=main, label="pack branch") == []


def test_the_correct_link_to_the_bootstrap_passes_on_both_branches(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """`start.md` on main; WP06's rewrite repoints it to `AGENTS.md` on the branch."""
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n\nStart with [the brief](start.md).\n",
            "start.md": "# Start here\n",
        }
    )
    assert check_links(config) == []


def test_a_missing_file_fails_on_both_branches_and_names_them(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n\nSee [nowhere](does-not-exist.md).\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    findings = check_links(config)

    assert {f.branch for f in findings} == {Branch.MAIN, Branch.PACK}
    assert all(f.rule is Rule.UNRESOLVED for f in findings)
    assert all(f.resolves_on is None for f in findings)
    assert all("no such document on either branch" in f.describe() for f in findings)


def test_a_link_to_start_md_written_on_the_branch_would_fail_there(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """The mirror image of the regression: caught on `pack`, named as `pack`.

    Reachable only if WP06's rewrite regresses — which is exactly when we want to hear.
    """
    main = main_surface(pack_factory())

    broken = Surface(branch=Branch.PACK, documents={"README.md": "See [x](start.md).\n"})
    findings = check_resolution(broken, other=main, label="pack branch")

    assert len(findings) == 1
    assert findings[0].branch is Branch.PACK
    assert findings[0].resolves_on is Branch.MAIN
    assert "does not resolve on `pack`" in findings[0].describe()


def test_a_code_sample_naming_a_missing_file_does_not_fail(
    pack_factory: Callable[..., BuildConfig],
) -> None:
    """Extraction and the rules, wired together: the exclusion must hold end to end."""
    config = pack_factory(
        files={
            "creator-kit.md": "# Kit\n\nWrite `[nowhere](does-not-exist.md)` like so.\n",
            "getting-started.md": "# Getting Started\n",
            "ethics.md": "# Ethics\n",
            "README.md": "# The kit\n",
            "start.md": "# Start here\n",
        }
    )
    assert check_links(config) == []


# --------------------------------------------------------------------------------------
# T035 case 5 — the live pack. The only place testing the real thing is right: it is
# the check's actual job.
# --------------------------------------------------------------------------------------


def test_the_real_pack_passes_on_both_branches(real_repo_config: BuildConfig) -> None:
    """The live pack, today, on `main` and on the pack branch.

    If this fails it is a LIVE FINDING in src/pack/, not a test to relax. Report it;
    the build never writes to the pack (C-002, C-006).
    """
    findings = check_links(real_repo_config)
    assert findings == [], "\n".join(f.describe() for f in findings)


def test_the_real_pack_has_cross_references_to_check(real_repo_config: BuildConfig) -> None:
    """Guards the guard: a checker that finds no links passes vacuously."""
    surface = main_surface(real_repo_config)
    total = sum(len(extract_links(text)) for text in surface.documents.values())
    assert total >= 20, f"expected the pack's ~40 cross-links, extracted {total}"


# --------------------------------------------------------------------------------------
# The CLI (T034): wired for CI, and it must actually exit non-zero.
# --------------------------------------------------------------------------------------


def test_links_check_passes_against_the_real_repo() -> None:
    result = CliRunner().invoke(guide, ["links", "check"])
    assert result.exit_code == 0, result.output
    assert "OK:" in result.output


def test_links_check_is_registered_under_guide() -> None:
    result = CliRunner().invoke(guide, ["links", "--help"])
    assert result.exit_code == 0
    assert "check" in result.output
