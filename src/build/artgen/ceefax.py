"""Generate the Ceefax mock as authentic Mode 7.

Teletext drew graphics with **block mosaics**: each character cell is split into a 2x3
grid of blocks, and a cell is one colour. That constraint is the whole look. Approximating
it with smooth shapes produces something that reads as "retro" rather than as Ceefax, and a
reader who grew up with it feels the wrong note without being able to name it.

The grid is 40x25 cells (`COLS` x `ROWS`), so the mosaic canvas is 80x75 blocks. Art is
authored as strings on that canvas and emitted as `<rect>`s, cell-aligned, because that is
what the hardware could actually do.

Run: `python -m build.artgen.ceefax > src/pack/ceefax-274.svg`. The output is committed;
this module exists so the next artifact is authored rather than hand-typed.
"""

from __future__ import annotations

COLS, ROWS = 40, 25
W, H = 640, 500
CW, CH = W / COLS, H / ROWS
BW, BH = CW / 2, CH / 3

WHITE, YELLOW, CYAN, GREEN, RED, MAGENTA = (
    "#ffffff",
    "#ffff00",
    "#00ffff",
    "#00ff00",
    "#ff0000",
    "#ff00ff",
)

#: A closed eye, drawn on the block grid. Thematic: the page is about eye strain, and the
#: Directorate would have chosen it for exactly that reason and not noticed the joke.
EYE = [
    "......########......",
    "....############....",
    "..####........####..",
    ".###....####....###.",
    "##....########....##",
    "##...##########...##",
    "##....########....##",
    ".###....####....###.",
    "..####........####..",
    "....############....",
    "......########......",
]


#: A book with a frowning face on the cover. The Directorate commissioned it in earnest.
BOOK = [
    "..############################..",
    ".##############################.",
    "###..........................###",
    "###..........................###",
    "###...####............####...###",
    "###...####............####...###",
    "###...####............####...###",
    "###..........................###",
    "###..........................###",
    "###..........................###",
    "###.......############.......###",
    "###.....##............##.....###",
    "###...##................##...###",
    "###..........................###",
    "###..........................###",
    ".##############################.",
    "..############################..",
    "....########..........########..",
]

#: A crowd on a terrace: blocky heads in rows. Ceefax drew everything this way.
CROWD = [
    "..##....##....##....##....##..",
    ".####..####..####..####..####.",
    ".####..####..####..####..####.",
    "..............................",
    "####..####..####..####..####..",
    "####..####..####..####..####..",
    "..............................",
    "..##....##....##....##....##..",
    ".####..####..####..####..####.",
    ".####..####..####..####..####.",
    "##############################",
    "##############################",
]


def mosaic(art: list[str], ox: int, oy: int, colour: str) -> str:
    """Emit `art` as block rects, with its top-left block at (`ox`, `oy`)."""
    out = []
    for row, line in enumerate(art):
        for col, ch in enumerate(line):
            if ch != "#":
                continue
            x = (ox + col) * BW
            y = (oy + row) * BH
            out.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{BW:.2f}" height="{BH:.2f}" fill="{colour}"/>'
            )
    return "\n    ".join(out)


def bar(row: int, colour: str, cols: range | None = None) -> str:
    """A solid mosaic bar across `cols` of a character row: Ceefax's favourite furniture."""
    span = cols if cols is not None else range(COLS)
    return mosaic(["#" * (len(span) * 2)] * 3, span.start * 2, row * 3, colour)


def cell_text(col: int, row: int, text: str, colour: str, double: bool = False) -> str:
    """Text on the character grid. Baseline sits where Mode 7 put it."""
    size = 39 if double else 19.5
    dy = CH * 1.62 if double else CH * 0.78
    return (
        f'<text x="{col * CW:.1f}" y="{row * CH + dy:.1f}" fill="{colour}" '
        f'font-size="{size}" letter-spacing="{3 if double else 1.6}">{text}</text>'
    )


def _frame(number: int, title: str) -> list[str]:
    """The chrome every page in the service shares: header row and index strip."""
    return [
        cell_text(1, 0, f"P{number}", WHITE),
        cell_text(7, 0, f"CEEFAX {number}", CYAN),
        cell_text(21, 0, "Mon 14 Oct", WHITE),
        cell_text(32, 0, "20:41/32", GREEN),
        bar(2, RED),
        cell_text(max(1, (40 - len(title) * 2) // 2), 4, title, YELLOW, double=True),
        bar(7, RED),
        bar(23, MAGENTA, cols=range(0, 13)),
        bar(23, GREEN, cols=range(13, 26)),
        bar(23, CYAN, cols=range(26, 40)),
        cell_text(1, 24, "Reading 273", MAGENTA),
        cell_text(15, 24, "Health 274", GREEN),
        cell_text(28, 24, "Sport 275", CYAN),
    ]


PAGES: dict[int, dict[str, object]] = {
    273: {
        "title": "READING",
        "desc": (
            "An invented Ceefax page 273 showing a large block-mosaic drawing of a book "
            "with a frowning face on its cover, over the caption ARE YOU READING TOO "
            "MUCH? and the line Ask yourself: is it making you happy?"
        ),
        "parts": lambda: [
            mosaic(BOOK, 24, 27, CYAN),
            cell_text(1, 19, "ARE YOU READING TOO MUCH?", WHITE),
            cell_text(1, 21, "Ask yourself: is it making you happy?", YELLOW),
        ],
    },
    274: {
        "title": "READING AND YOU",
        "desc": (
            "An invented Ceefax page 274 carrying a public information message claiming "
            "prolonged reading causes eye strain, poor posture, disturbed sleep and "
            "nervous exhaustion, and advising no more than 20 minutes an evening."
        ),
        "parts": lambda: [
            mosaic(EYE, 1, 27, CYAN),
            cell_text(13, 10, "A PUBLIC", CYAN),
            cell_text(13, 11, "INFORMATION", CYAN),
            cell_text(13, 12, "MESSAGE", CYAN),
            cell_text(1, 15, "Doctors now advise that prolonged", WHITE),
            cell_text(1, 16, "reading may contribute to:", WHITE),
            cell_text(4, 18, "eye strain and headache", YELLOW),
            cell_text(4, 19, "poor posture", YELLOW),
            cell_text(4, 20, "disturbed sleep", YELLOW),
            cell_text(4, 21, "nervous exhaustion", YELLOW),
        ],
    },
    275: {
        "title": "WHY NOT FOOTBALL?",
        "desc": (
            "An invented Ceefax page 275 showing a block-mosaic crowd on a terrace, "
            "recommending league football as a healthy alternative to an evening spent "
            "reading, and noting that 92 clubs play within reach of most homes and that "
            "admission is within the means of the ordinary working man."
        ),
        "parts": lambda: [
            mosaic(CROWD, 10, 27, GREEN),
            cell_text(1, 15, "A healthy evening out, in the open", WHITE),
            cell_text(1, 16, "air, among friends and neighbours.", WHITE),
            cell_text(1, 18, "92 clubs play within reach of most", YELLOW),
            cell_text(1, 19, "homes. Admission is within the means", YELLOW),
            cell_text(1, 20, "of the ordinary working man.", YELLOW),
            cell_text(1, 22, "Issued by the Directorate of Reading", CYAN),
        ],
    },
}


def render(number: int) -> str:
    page = PAGES[number]
    parts = _frame(number, str(page["title"])) + page["parts"]()  # type: ignore[operator]
    body = "\n    ".join(parts)
    desc = (
        f"{page['desc']} No such page was ever broadcast; this image is a fake, "
        "generated to show how easily documentary evidence is manufactured."
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"
     aria-labelledby="t d">
  <title id="t">Fabricated screenshot: Ceefax page {number}, never broadcast</title>
  <desc id="d">{desc}</desc>
  <rect width="{W}" height="{H}" fill="#000000"/>
  <g font-family="'Courier New', monospace" font-weight="bold">
    {body}
  </g>
</svg>
"""


if __name__ == "__main__":
    import sys
    from pathlib import Path as _Path

    out = _Path(sys.argv[1]) if len(sys.argv) > 1 else _Path(".")
    for number in PAGES:
        (out / f"ceefax-{number}.svg").write_text(render(number), encoding="utf-8")
        print(f"wrote ceefax-{number}.svg", file=sys.stderr)
